import os
import cv2

plate_files = os.listdir('/Users/wendyzhang/Desktop/plate_labels')
plate_files = sorted(plate_files)
plate_files.pop(0)

car_files = os.listdir('/Users/wendyzhang/Desktop/images')
car_files = sorted(car_files)
car_files.pop(0)

# read all plate labels, split them and produce a nested list, where each
#   element contains all labels from a single image, and each label is
#      represented by a list of strings
list_of_plate_labels = []
for filename in plate_files:
    if filename.endswith('.txt'):
        with open('/Users/wendyzhang/Desktop/plate_labels/' + filename) as f:
            content = f.readlines()
            labels_in_same_image = []
            for item in content:
                splitted_label = item.split()
                labels_in_same_image.append(splitted_label)
            list_of_plate_labels.append(labels_in_same_image)

# read all car labels, split them and produce a nested list, where each element
#   contains all labels from a single image, and each label is represented by a
#     list of strings
list_of_car_labels = []
for filename in car_files:
    if filename.endswith('.txt'):
        with open('/Users/wendyzhang/Desktop/images/' + filename) as f:
            content = f.readlines()
            labels_in_same_image = []
            for item in content:
                splitted_label = item.split()
                labels_in_same_image.append(splitted_label)
            list_of_car_labels.append(labels_in_same_image)

# list of all image files
image_files = []
for filename in car_files:
    if filename.endswith('.jpg'):
        image_files.append(filename)

# in_car_label(plate, car) determines if plate label is inside car label, where
#   plate and car are lists of strings, and returns car label if true
def in_car_label(plate, car):
    plate_cx = plate[1]
    plate_cy = plate[2]
    plate_w = plate[3]
    plate_h = plate[4]
    car_cx = car[1]
    car_cy = car[2]
    car_w = car[3]
    car_h = car[4]
    if (float(plate_cx) - float(plate_w) / 2.0 > float(car_cx) - float(car_w) /
        2.0 and \
        float(plate_cx) + float(plate_w) / 2.0 < float(car_cx) + float(car_w) /
        2.0 and \
        float(plate_cy) - float(plate_h) / 2.0 > float(car_cy) - float(car_h) /
        2.0 and \
        float(plate_cy) + float(plate_h) / 2.0 < float(car_cy) + float(car_h) /
        2.0):
        return car
    else:
        return False

# in_a_car(plate, locars) determines if plate label is inside any of the car
#   labels in locars, where plate is a list of strings and locars is a list of
#     lists of strings, and returns car label if true
def in_a_car(plate, locars):
    for i in range(len(locars)):
        if in_car_label(plate, locars[i]):
            return in_car_label(plate, locars[i])
    return False

# create a list of objects, where each object is a car with corresponding plate
#   labels
# loop through list of plate labels, check if plate label is inside any of car
#   labels, if true create object = plate, car

# a list, where each element is a list of plate label, corresponding car label,
#   and image name
list_of_three = []

# a list of three elements, first is plate label, second is car label, and third
#   is image name
plate_car_image = []
for num in range(532):     # for each image
    for i in range(len(list_of_plate_labels[num])):
        if in_a_car(list_of_plate_labels[num][i], list_of_car_labels[num]):
            car_label = in_a_car(list_of_plate_labels[num][i],
                                 list_of_car_labels[num])
            filename = image_files[num]
            plate_car_image = [list_of_plate_labels[num][i], car_label,
                               filename]
            list_of_three.append(plate_car_image)

# crop car and change plate coordinates

# list of cropped car images
cropped_list = []

for item in list_of_three:
    plate_label = item[0]
    car_label = item[1]
    image_name = item[2]
    img = cv2.imread('/Users/wendyzhang/Desktop/images/' + image_name)
    img_h, img_w, c = img.shape
    x = float(car_label[1]) - float(car_label[3]) / 2.0
    x_int = int((float(car_label[1]) * img_w) - (float(car_label[3]) * img_w) /
                                                 2.0)
    y = float(car_label[2]) - float(car_label[4]) / 2.0
    y_int = int((float(car_label[2]) * img_h) - (float(car_label[4]) * img_h) /
                                                 2.0)
    w_int = int(float(car_label[3]) * img_w)
    h_int = int(float(car_label[4]) * img_h)
    crop_img = img[y_int:y_int + h_int, x_int:x_int + w_int]
    cropped_list.append(crop_img)
    plate_x = (float(plate_label[1]) - float(plate_label[3]) / 2.0)
    plate_x = (plate_x - x) / float(car_label[3])
    plate_y = (float(plate_label[2]) - float(plate_label[4]) / 2.0)
    plate_y = (plate_y - y) / float(car_label[4])
    plate_w = float(plate_label[3]) / float(car_label[3])
    plate_h = float(plate_label[4]) / float(car_label[4])
    plate_cx = plate_x + plate_w / 2.0
    plate_cy = plate_y + plate_h / 2.0
    plate_label = [0, plate_cx, plate_cy, plate_w, plate_h]
    item[0] = plate_label

# now plate coordinates are in reference of car

# list of resized + cropped car images
resized_list = []

# resize cropped car images
for item in cropped_list:
    resized_img = cv2.resize(item, (320, 320))
    resized_list.append(resized_img)

# change plate coordinates to reflect change to image size 320 x 320
for item in list_of_three:
  plate_label = item[0]
  plate_x = (float(plate_label[1]) - float(plate_label[3]) / 2.0)

# create a new name for the object = new_name
last_image = 'n'
track = 0
for i in range(642):
    item = list_of_three[i]
    plate_label = item[0]
    image_name = item[2]
    if image_name == last_image:
        track += 1
    if image_name != last_image:
        track = 0
    new_name = image_name.replace(".jpg", "_c+r_" + str(track) + ".jpg")
    item[2] = new_name
    last_image = image_name

# write cropped+resize car to file (new_name.jpg)
# write plate coordinates from step 5 as new_name.txt with the same format as
#   original yolo
for i in range(642):
    item = list_of_three[i]
    plate_label = item[0]
    image_name = item[2]
    img = resized_list[i]
    cv2.imwrite(image_name, img)
    txt_name = image_name.replace("jpg", "txt")
    f = open(txt_name, "w")
    coordinates = " ".join(map(str, plate_label)) + "\n"
    f.write(coordinates)
    f.close()










