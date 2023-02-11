from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QApplication


def get_screen_size():
    """
    checks current screen width and height
    :return: screen_width current screen width
    :return: screen_height   current screen height
    """
    screen_width = QApplication.primaryScreen().size().width()
    screen_height = QApplication.primaryScreen().size().height()
    return screen_width, screen_height


class ROIDialog(QDialog):
    """
        A class to present ROI information
        In order to do it creates new dialog window

        Attributes
        ----------
        mean_label : QLabel
            label containing information about mean from chosen ROI
        std_label : QLabel
            label containing information about standard deviation from chosen ROI
        size_label : QLabel
            label  containing information about real-life size of choose ROI
        cancel_btn : QDialogButtonBox
           button to close window

        Methods
        -------
        change_labels(self, mean, std, size):
            Changes displayed labels' text
            it should be used after choosing new ROI

    """

    def __init__(self):
        """
        Constructs all the necessary attributes for ROI dialog window
        Uses vertical BoxLayout
        Position the dialog window on the right side of the main window
        """
        super().__init__()

        self.setWindowTitle("ROI results")
        width, height = get_screen_size()
        self.setGeometry(width / 2 + 410, height / 2 - 170, 200, 120)

        self.cancel_btn = QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(self.cancel_btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.mean_label = QLabel("Mean: ")
        self.std_label = QLabel("Std:")
        self.size_label = QLabel("Size: ")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.mean_label)
        self.layout.addWidget(self.std_label)
        self.layout.addWidget(self.size_label)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def change_labels(self, mean, std, size):
        """
        Changes labels' displayed text
        Should be used after choosing new ROI
        :param mean: mean from new ROI
        :param std: standard deviation from new ROI
        :param size: real-life size of new ROI
        """
        self.mean_label.setText("Mean: " + str(mean) + " HU")
        self.std_label.setText("Std: " + str(std) + " HU")
        self.size_label.setText("Size: " + str(size) + " mm^2")
