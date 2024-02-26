import cv2
import os
import glob

import numpy as np
from scipy.spatial import distance

def load_images(path):
    data_path = os.path.join(path,'*g')
    files = glob.glob(data_path)
    data = []
    for f in files:
        images = dict()
        images["name"] = os.path.basename(f)
        img = cv2.imread(f)
        images["image"] = img
        data.append(images)

    return data


def load_image(path):
    image = dict()
    image["name"] = os.path.basename(path)
    img = cv2.imread(path)
    image["image"] = img

    return image


def draw_image(image, name):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, 600, 600)
    cv2.imshow(name, image)
    cv2.imwrite("res/images/export/" + name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def filter_slicer_image(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Masks for different shades of red 
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    lower_red = np.array([170, 120, 70])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)

    mask = mask1 + mask2

    return mask


def filter_printer_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    filtered_image = cv2.medianBlur(gray, 11)
    _, im = cv2.threshold(filtered_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = np.ones((11, 11), np.uint8)
    # print(kernel)
    opening = cv2.morphologyEx(im, cv2.MORPH_OPEN, kernel)

    return opening


def calculate_hu_moments(image):
    moments = cv2.moments(image)
    hu_moments = cv2.HuMoments(moments).flatten()  # Flatten the 2D array

    return hu_moments


def compare_moments(moment_1, moment_2):
    difference = distance.euclidean(moment_1, moment_2)

    return difference


def successful_test():
    slicer_images = load_images("res/images/success/slicer/")
    printer_images = load_images("res/images/success/print/")

    for sl_img, pr_img in zip(slicer_images, printer_images):
        filtered_image = filter_slicer_image(sl_img["image"])
        sl_hu_moments = calculate_hu_moments(filtered_image)
        draw_image(filtered_image, sl_img["name"])

        filtered_image = filter_printer_image(pr_img["image"])
        pr_hu_moments = calculate_hu_moments(filtered_image)
        draw_image(filtered_image, pr_img["name"])

        diff = compare_moments(sl_hu_moments, pr_hu_moments)
        print("Similarity: " + sl_img["name"] + ", " + pr_img["name"] + " = " + str(diff))


def fail_test():
    slicer_image = load_image("res/images/success/slicer/01.png")
    successful_image = load_image("res/images/success/01.png")
    failed_images = load_images("res/images/fail/print/")

    filtered_image = filter_slicer_image(slicer_image["image"])
    sl_hu_moments = calculate_hu_moments(filtered_image)
    draw_image(filtered_image, slicer_image["name"])

    filtered_image = filter_printer_image(successful_image["image"])
    su_hu_moments = calculate_hu_moments(filtered_image)
    draw_image(filtered_image, successful_image["name"])

    diff = compare_moments(sl_hu_moments, su_hu_moments)
    print("Similarity: " + slicer_image["name"] + ", " + successful_image["name"] + " = " + str(diff))

    for fl_img in failed_images:
        filtered_image = filter_printer_image(fl_img["image"])
        pr_hu_moments = calculate_hu_moments(filtered_image)
        draw_image(filtered_image, fl_img["name"])

        diff = compare_moments(sl_hu_moments, pr_hu_moments)
        print("Similarity(" + slicer_image["name"] + ", " + fl_img["name"] + " = " + str(diff))


def main():
    successful_test()
    # fail_test()


if __name__== "__main__":
    main()
