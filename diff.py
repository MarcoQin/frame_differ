from __future__ import print_function
import cv2
import numpy as np
import json
import time


pixels = []


block_width = 4  # 8
block_height = 8


def parse(img, img1, frame_index):
    print("parse frame ", frame_index)
    width = len(img)
    height = len(img[0])
    d = cv2.absdiff(img, img1)
    # d = cv2.subtract(img1, img)
    # d1 = cv2.subtract(img, img1)
    # cv2.imwrite("output/%03d.jpg" % frame_index, d)
    # return

    has_write_new = False

    for x in range(0, width, block_width):
        for y in range(0, height, block_height):
            diff = False
            for i in range(block_width):
                if diff:
                    break
                for j in range(block_height):
                    if diff:
                        break
                    # color = d[x + i][y + j]
                    color = d[y + j][x + i]
                    for rgb in color:
                        # if rgb > 1:
                        if rgb > 0:
                            diff = True
                            break

            if diff:
                if not has_write_new:
                    has_write_new = True
                # pixel_block = 0
                pixel_block = np.zeros([block_height, block_width, 3], dtype=np.uint8)
                # for i in range(block_width):
                    # for j in range(block_height):
                        # pixel_block[i][j] = img1[x + i][y + j]
                for j in range(block_height):
                    for i in range(block_width):
                        pixel_block[j][i] = img1[y + j][x + i]
                new_data = ((frame_index, x, y), pixel_block)
                pixels.append(new_data)

    if not has_write_new:
        pixel_block = np.zeros([block_height, block_width, 3], dtype=np.uint8)
        # pixel_block = 0
        new_data = ((frame_index, 0, 0), pixel_block)
        pixels.append(new_data)


def save_img():
    base = 65025  # num of 8x8 pixel blocks of one image(2048 * 2048)
    base = int((2048 / 8 - 1) * (2048 / 8 - 1))
    base = int((2048 / 4 - 1) * (2048 / 8 - 1))
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
            h = int(((len(new) * block_width + block_width) / w + 3) * 8)
        image = np.zeros([h, w, 3], dtype=np.uint8)
        print(w)
        print(h)
        x_1 = 0
        y_1 = 0
        for block in new:
            if x_1 >= 2048:
                x_1 = 0
                y_1 += block_height
            frame_info = block[0]
            frame_index, x_diff, y_diff = frame_info
            if frame_index not in rt:
                rt[frame_index] = []
            # rt[frame_index].append("%s,%s,%s,%s,%s" % (img_index, x_diff, y_diff, x_1, y_1))
            rt[frame_index].append("%s,%s,%s,%s,%s" % (img_index, y_diff, x_diff, y_1, x_1))
            # y_1 += 8
            # continue
            img_block = block[1]

            # for x_x, data in enumerate(img_block):
                # for y_y, pi in enumerate(data):
                    # image[x_1 + x_x][y_1 + y_y] = pi
            for y_y, data in enumerate(img_block):
                for x_x, pi in enumerate(data):
                    image[y_1 + y_y][x_1 + x_x] = pi

            x_1 += block_width
        cv2.imwrite("diff%s.jpg" % img_index, image)
        img_index += 1
    with open("result.json", "w") as f:
        f.write(json.dumps(rt))


rt = {}

img0 = None

st = time.time()

start_num = 0
end_num = 90  # 422

for i in range(start_num, end_num):

    img = cv2.imread("imgs/core_s_%05d.jpg" % i, flags=cv2.IMREAD_UNCHANGED)
    if i == start_num:
        img0 = np.zeros([len(img), len(img[0]), 3], dtype=np.uint8)

    start = time.time()
    parse(img0, img, i)
    print("parse finish at ", time.time() - start)
    img0 = img

save_img()

ed = time.time()
print("total use: ", ed - st)
