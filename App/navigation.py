import os


def get_next_series(current_path):
    """
    Finds path of next series in examination folder
    If next series doesn't exist gets first series in examination folder
    :param current_path: path of currently displayed image
    :return path: path of first image in next series in current examination folder
    """
    splited_path = current_path.split('/')
    series_name = splited_path.pop()
    series_name = splited_path.pop()
    folder_path = "/".join(splited_path)
    series_names = os.listdir(folder_path)
    try:
        index = series_names.index(series_name)
        index += 1
        series_name = series_names[index]
    except IndexError:
        series_name = series_names[0]
    path = folder_path + '/' + series_name
    images_names = os.listdir(path)
    path = path + '/' + images_names[0]
    return path


def get_new_image(current_path, image_number):
    """
    Finds path of new image in series folder
    :param current_path: path of currently displayed image
    :param image_number: image number (position in folder) we want to display
    :return path : path of new image to display
    """
    splitted_path = current_path.split('/')
    splitted_path.pop()
    folder_path = "/".join(splitted_path)
    images_names = os.listdir(folder_path)
    try:
        image_name = images_names[image_number - 1]
    except IndexError:
        return ""
    path = folder_path + '/' + image_name
    return path


def get_image_number(image_path):
    """
        checks the image position in its series folder
        :param image_path: path of currently displayed image
        :return index: image position in series folder
    """
    splitted_path = image_path.split('/')
    image_name = splitted_path.pop()
    folder_path = "/".join(splitted_path)
    images_names = os.listdir(folder_path)
    try:
        index = images_names.index(image_name)
    except IndexError:
        return 1
    index = index + 1
    return index
