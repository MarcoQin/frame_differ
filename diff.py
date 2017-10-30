from __future__ import print_function
import cv2
import numpy as np
import json
import time


pixels = []


def parse(img, img1, frame_index):
    print("parse frame ", frame_index)
    width = len(img)
    height = len(img[0])
    d = cv2.absdiff(img, img1)
    # d = cv2.subtract(img1, img)
    # d1 = cv2.subtract(img, img1)

    has_write_new = False

    for x in range(0, width, 8):
        for y in range(0, height, 8):
            diff = False
            for i in range(8):
                if diff:
                    break
                for j in range(8):
                    if diff:
                        break
                    color = d[x + i][y + j]
                    for rgb in color:
                        if rgb > 1:
                            diff = True
                            break

            if diff:
                if not has_write_new:
                    has_write_new = True
                # pixel_block = 0
                pixel_block = np.zeros([8, 8, 3], dtype=np.uint8)
                for i in range(8):
                    for j in range(8):
                        pixel_block[i][j] = img1[x + i][y + j]
                new_data = ((frame_index, x, y), pixel_block)
                pixels.append(new_data)

    if not has_write_new:
        pixel_block = np.zeros([8, 8, 3], dtype=np.uint8)
        # pixel_block = 0
        new_data = ((frame_index, 0, 0), pixel_block)
        pixels.append(new_data)


def save_img():
    base = 65025  # num of 8x8 pixel blocks of one image(2048 * 2048)
    img_index = 0
    global pixels
    rt = {}
    while pixels:
        w = 2048
        new = pixels[:base]
        if len(pixels) > base:
            h = 2048
            pixels = pixels[base:]
        else:
            pixels = []
            h = int(((len(new) * 8 + 8) / w + 3) * 8)
        image = np.zeros([h, w, 3], dtype=np.uint8)
        print(w)
        print(h)
        x_1 = 0
        y_1 = 0
        for block in new:
            if y_1 >= 2048:
                y_1 = 0
                x_1 += 8
            frame_info = block[0]
            frame_index, x_diff, y_diff = frame_info
            if frame_index not in rt:
                rt[frame_index] = []
            rt[frame_index].append("%s,%s,%s,%s,%s" % (img_index, x_diff, y_diff, x_1, y_1))
            # y_1 += 8
            # continue
            img_block = block[1]

            for x_x, data in enumerate(img_block):
                for y_y, pi in enumerate(data):
                    image[x_1 + x_x][y_1 + y_y] = pi

            y_1 += 8
        cv2.imwrite("diff%s.jpg" % img_index, image)
        img_index += 1
    with open("result.json", "w") as f:
        f.write(json.dumps(rt))


rt = {}

img0 = None

st = time.time()

start_num = 1
end_num = 422  # 422

for i in range(start_num, end_num):

    img = cv2.imread("%04d.jpg" % i, flags=cv2.IMREAD_UNCHANGED)
    if i == start_num:
        img0 = np.zeros([len(img), len(img[0]), 3], dtype=np.uint8)

    start = time.time()
    parse(img0, img, i)
    print("parse finish at ", time.time() - start)
    img0 = img

save_img()

ed = time.time()
print("total use: ", ed - st)
