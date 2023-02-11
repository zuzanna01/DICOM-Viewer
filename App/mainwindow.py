import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pydicom
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QWidget, \
    QFileDialog, QSlider, QSpinBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from App import navigation
from App import roipicker
from App.ROIDialog import ROIDialog


class MainWindow(QMainWindow):
    """
    Class representing main window of the application
    """
    resized = Signal()
    setImage = Signal(np.ndarray)
    dnnEdge = Signal(np.ndarray)

    # Current file as cvImage
    cvImage = ""
    # Current file path
    currPath = ""
    # Current dile dicom data
    dicom_data = ""

    def __init__(self, parent=None):
        """
        Initiation of MainWindow object. Creates main window of the application with default values.
        :param parent: not used in this program
        """
        super().__init__(parent)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Sliders
        self.brislider = QSlider()
        self.brislider.setRange(0, 2 * 255)
        self.brislider.setValue(255)
        self.brislider.valueChanged.connect(self.regulateImage)
        self.conslider = QSlider()
        self.conslider.setRange(0, 2 * 127)
        self.conslider.setValue(127)
        self.conslider.valueChanged.connect(self.regulateImage)
        self.imageslider = QSlider()
        self.imageslider.setRange(0, 0)
        self.imageslider.valueChanged.connect(self.change_image)

        # Buttons
        openBtn = QPushButton("Open image")
        openBtn.clicked.connect(self.chooseFile)
        restoreBtn = QPushButton("Reset")
        restoreBtn.clicked.connect(self.restore)
        roiBtn = QPushButton("Pick ROI")
        roiBtn.clicked.connect(self.chooseROI)
        nextSeriesBtn = QPushButton("Next series")
        nextSeriesBtn.clicked.connect(self.set_next_series)
        operLab = QLabel("ROI Tolerance:")
        self.regulation = QSpinBox()
        self.regulation.setRange(1, 255)
        self.regulation.setSingleStep(1)
        self.regulation.setValue(30)
        self.timeLab = QLabel("")
        self.letters = QLabel("N     C     B  ")
        self.brightness = QLabel("Brightness (B): 255    ")
        self.contrast = QLabel("Contrast   (C): 127    ")

        self.roi_dialog = ROIDialog()
        # Layouts
        layoutVal = QVBoxLayout()
        layoutVal.addWidget(self.contrast)
        layoutVal.addWidget(self.brightness)

        layoutBtn = QHBoxLayout()
        layoutBtn.addWidget(openBtn)
        layoutBtn.addWidget(restoreBtn)
        layoutBtn.addWidget(nextSeriesBtn)
        layoutBtn.addWidget(roiBtn)
        layoutBtn.addWidget(self.timeLab)
        layoutBtn.addWidget(operLab)
        layoutBtn.addWidget(self.regulation)
        layoutBtn.addWidget(self.timeLab)
        layoutBtn.addLayout(layoutVal)
        layoutBtn.addStretch()
        layoutBtn.addWidget(self.letters)

        layoutSld = QHBoxLayout()
        layoutSld.addWidget(self.canvas)
        layoutSld.addWidget(self.imageslider)
        layoutSld.addWidget(self.conslider)
        layoutSld.addWidget(self.brislider)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(layoutSld)
        layout.addLayout(layoutBtn)

        # Main layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()

    @Slot()
    def chooseFile(self):
        """
        Method opens file explorer and allows user to choose a .dcm file. Runs displayDicom.
        :return:
        """
        self.figure.clear()
        self.canvas.draw()
        image_path = QFileDialog.getOpenFileName(self, "Select file", filter="DICOM files (*.dcm)")
        self.currPath = image_path[0]
        self.set_image_slider()
        self.displayDicom(self.currPath)
        self.restore()

    def displayDicom(self, imagePath):
        """
        Method displays DICOM image from given path in a matplot. Does nothing if the imagePath is empty.
        :param: imagePath: path to file we want to open
        :return:
        """
        if imagePath == "":
            return

        dcm = pydicom.dcmread(imagePath, force=True)

        if 'PixelData' in dcm:
            imageData = dcm.pixel_array.astype(float)

            scaled_image = (np.maximum(imageData, 0) / imageData.max()) * 255.0

            scaled_image = np.uint8(scaled_image)
            final_image = cv2.cvtColor(np.array(scaled_image), cv2.COLOR_RGB2BGR)
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            ax.imshow(final_image, plt.cm.bone)
            self.canvas.draw()
            self.cvImage = final_image
            self.dicom_data = dcm

    @Slot()
    def chooseROI(self):
        """
        Allows user to choose region of interest on loaded image by selecting one pixel of that area, runs roipicker.py
        functions and displays the image with the ROI. Does nothing if there is no image currenty loaded.
        :return:
        """
        try:
            if str(self.cvImage) == "":
                return

            coords = self.figure.ginput(1, 0)
            coords = [round(item) for item in coords[0]]
            img_data = self.regulateImage()

            contours, flood_mask = roipicker.findROI(img_data, coords, self.regulation.value())
            info = roipicker.analyzeROI(self.dicom_data, flood_mask)

            viz = img_data.copy()
            viz = cv2.drawContours(viz, contours, -1, color=(0, 255, 0), thickness=-1)
            viz = cv2.addWeighted(img_data, 0.75, viz, 0.25, 0)
            viz = cv2.drawContours(viz, contours, -1, color=(0, 255, 0), thickness=1)
            ax = self.figure.add_subplot(111)
            ax.imshow(viz)
            self.canvas.draw()
            self.displayROIInfo(info)
            if str(contours) == "":
                return
        except RuntimeError:
            pass
        finally:
            pass

    def regulateImage(self):
        """
        Regulates image's brightness and contrast and their values according to slider's positions and displays the
        changed image. Run every time slider moves. Only changes values if there is no image loaded.
        :return:
        """
        self.roi_dialog.change_labels(0, 0, 0)
        self.brightness.setText("Brightness (B): " + str(self.brislider.value()) + "    ")
        self.contrast.setText("Contrast   (C): " + str(self.conslider.value()) + "    ")

        if str(self.cvImage) == "":
            return

        brightness = int((self.brislider.value() - 0) * (255 - (-255)) / (510 - 0) + (-255))
        contrast = int((self.conslider.value() - 0) * (127 - (-127)) / (254 - 0) + (-127))

        if brightness != 0:

            if brightness > 0:
                shadow = brightness
                maxim = 255
            else:
                shadow = 0
                maxim = 255 + brightness

            al_pha = (maxim - shadow) / 255
            ga_mma = shadow

            cal = cv2.addWeighted(self.cvImage, al_pha, self.cvImage, 0, ga_mma)
        else:
            cal = self.cvImage

        if contrast != 0:
            Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            Gamma = 127 * (1 - Alpha)

            cal = cv2.addWeighted(cal, Alpha, cal, 0, Gamma)

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.imshow(cal, plt.cm.bone)
        self.canvas.draw()

        return cal

    def restore(self):
        """
        Restores original settings of current image and default values to sliders and ROI info if it's window is active.
        :return:
        """
        self.displayDicom(self.currPath)
        self.brislider.setValue(255)
        self.conslider.setValue(127)
        self.roi_dialog.change_labels(0, 0, 0)

    def set_next_series(self):
        """
        Loads next series of DICOM files from current examination folder and displays first image from it
        Does nothing if current image path is empty.
        :return:
        """
        self.roi_dialog.change_labels(0, 0, 0)
        if self.currPath == "":
            return
        self.currPath = navigation.get_next_series(self.currPath)
        self.displayDicom(self.currPath)
        self.set_image_slider()

    def set_image_slider(self):
        """
        Checks number of images in chosen series folder and sets slider range
        Next, checks image (indicated by the current path) position in a folder and sets slider position

        Should be used after choosing new series or examination
        :return:
        """
        if self.currPath == "":
            return
        splitted_path = self.currPath.split('/')
        splitted_path.pop()
        folder_path = "/".join(splitted_path)
        number_of_images = 0
        for path in os.scandir(folder_path):
            if path.is_file():
                number_of_images += 1
        self.imageslider.setRange(1, number_of_images)
        image_number = navigation.get_image_number(self.currPath)
        self.imageslider.setValue(image_number)
        self.letters.setText(str(image_number) + "    C     B  ")

    def change_image(self):
        """
        Changes current image path based on slider position and displays new image
        :return:
        """
        self.roi_dialog.change_labels(0, 0, 0)
        image_number = self.imageslider.value()
        self.currPath = navigation.get_new_image(self.currPath, image_number)
        self.displayDicom(self.currPath)
        self.letters.setText(str(image_number) + "     C     B  ")
        self.regulateImage()

    def displayROIInfo(self, info):
        """
        Method displaying information on selected ROI in a popup window.
        :param info: vector of ROI information [mean, std, size]
        :return:
        """
        mean = round(info[0], 2)
        std = round(info[1], 2)
        size = round(info[2], 2)
        self.roi_dialog.change_labels(mean, std, size)
        self.roi_dialog.show()

    def closeEvent(self, event):
        """
        Method changing close operation
        With main window closed is also ROI dialog window if opened
        :param event:
        :return:
        """
        if self.roi_dialog is not None:
            self.roi_dialog.close()
