import cv2
import numpy as np
import cv2 as cv
from pydicom.pixel_data_handlers import apply_modality_lut


def findROI(img_data, point_cor, tolerance):
    """
    This function gives region of interest by finding pixels with value similar to the chosen point with set tolerance.
    :param img_data: matrix of pixel values of the image
    :param point_cor: tuple of x and y coordinate of the chosen point
    :param tolerance: integer value of tolerance with which points will be chosen
    :return: contours matrix, flood mask matrix
    """
    connectivity = 8
    h, w = img_data.shape[:2]
    img = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)
    flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    flood_fill_flags = (connectivity | cv.FLOODFILL_FIXED_RANGE | cv.FLOODFILL_MASK_ONLY)

    cv.floodFill(
        img,
        flood_mask,
        (point_cor[0], point_cor[1]),
        0,
        tolerance,
        tolerance,
        flood_fill_flags,
    )
    flood_mask_fin = flood_mask[1:-1, 1:-1].copy()

    contours = cv.findContours(flood_mask_fin, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(contours) == 2:
        contours = contours[0]
    elif len(contours) == 3:
        contours = contours[1]

    return contours, flood_mask_fin


def analyzeROI(dicom_data, flood_mask):
    """
    Returns info on ROI by getting values of pixels selected by flood mask in dicom data
    :param dicom_data: matrix of pixel values of dicom picture
    :param flood_mask: matrix consisting of 0 (non-selected area) and 1 (selected area)
    :return: mean, std and size of ROI
    """
    arr = dicom_data.pixel_array.astype(float)
    arr = apply_modality_lut(arr, dicom_data)
    area = arr * flood_mask

    pxnumber = np.count_nonzero(area)
    pxspacing = dicom_data.PixelSpacing
    pxarea = pxnumber * pxspacing[0] * pxspacing[1]

    area = area[np.nonzero(area)]
    mean = np.mean(area)
    std = np.std(area)

    return mean, std, pxarea
