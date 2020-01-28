import pytesseract
from pytesseract import Output
import cv2
import box_rectangle
from PIL import Image
from Image_to_Text import *
import os
import cv2

flyer_list = os.listdir('flyers')
for flyer in range(1, len(flyer_list)):
    def check_if_hit(arr, box):
        hit = False
        inter = set()
        for i in arr:
            if i is not box:
                if not (i.top_left[0] > box.bottom_right[0]) and not (i.bottom_right[0] < box.top_left[0]) and not (
                        i.bottom_right[1] < box.top_left[1]) and not (i.top_left[1] > box.bottom_right[1]):
                    hit = True
                    inter.add(i)

        if hit:
            return list(inter)
        else:
            return None
    print(flyer_list)
    print(flyer_list[flyer])
    #cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    #cv2.resizeWindow('image', 600, 600)
    path = 'flyers'
    path2 = os.path.join(path, flyer_list[flyer])
    img = cv2.imread(path2)
    image = Image.open(path2)

    width, height = image.size

    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    boxes_list = []
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        if h * w <= 25000:
            #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            box = box_rectangle.Rectangle([x, y], [x + w, y + h])
            boxes_list.append(box)

    movement = 22
    for box in boxes_list:
        expanding = True
        while expanding:
            box.top_left[0] -= movement
            box.top_left[1] -= movement
            box.bottom_right[0] += movement
            box.bottom_right[1] += movement

            intersected = check_if_hit(boxes_list, box)

            box.top_left[0] += movement
            box.top_left[1] += movement
            box.bottom_right[0] -= movement
            box.bottom_right[1] -= movement

            if intersected == None:
                expanding = False
            else:
                for item in intersected:
                    if item.top_left[1] < box.top_left[1]:
                        box.top_left[1] = item.top_left[1]
                    if item.bottom_right[1] > box.bottom_right[1]:
                        box.bottom_right[1] = item.bottom_right[1]
                    if item.top_left[0] < box.top_left[0]:
                        box.top_left[0] = item.top_left[0]
                    if item.bottom_right[0] > box.bottom_right[0]:
                        box.bottom_right[0] = item.bottom_right[0]
                    boxes_list.remove(item)
    for box in boxes_list:
        box.top_left[1] -= 115


    for box in boxes_list:
        cv2.rectangle(img, tuple(box.top_left), tuple(box.bottom_right), (255, 0, 0), 2)

    print(len(boxes_list))
    i = 1
    for box in boxes_list:
        cropped_image = image.crop((box.top_left[0], box.top_left[1], box.bottom_right[0], box.bottom_right[1]))
        file_name = 'crop_' + flyer_list[flyer] +'_' + str(i) +'.jpeg'
        cropped_image.save('cropped_images/' + file_name)
        i+=1

with open(file_name, mode='w') as csv_file:
    cwriter = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    cwriter.writerow(["flyer_name", "product_name", "unit_promo_price", "uom", "least_unit_for_promo", "save_per_unit", "discount", "organic"])
for fname in os.listdir("cropped_images/"):
    img = cv2.imread("cropped_images/" + fname)
    text = read(img)
    it = Item(text, fname[5:18])
    it.parse()
    it.prt("output.csv")