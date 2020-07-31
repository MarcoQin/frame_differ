#!/usr/bin/env python
# encoding: utf-8


import json


TARGET_IMAGE_WIDTH = 960
TARGET_IMAGE_WIDTH = 800


with open("result.json") as f:
    data = json.loads(f.read())

keys = sorted([int(x) for x in data.keys()])

block_base_width = 4
block_base_height = 8


def check(index, x, y, diff_x, diff_y, block_width):
    """
    image:
          0  y y y y y y y y
          x
          x
          x
          x
          x
    index range: 0 - 31
    block_width range: 8 - 1000
    revert:
        diff_image_index = (num_1 >> 22) & 0x1f
        x = (num_1 >> 11) & 0x7ff
        y = num_1 & 0x7ff
        block_width = (num_2 >> 22) & 0x3ff
        diff_x = (num_2 >> 11) & 0x7ff
        diff_y = num_2 & 0x7ff
    """
    num_1 = ((index & 0x1f) << 22) | ((x & 0x7ff) << (11)) | ((y & 0x7ff))
    num_2 = ((block_width & 0x3ff) << 22) | ((diff_x & 0x7ff) << (11)) | ((diff_y & 0x7ff))
    return num_1, num_2


rt = []


for k in keys:
    print(k)
    frames = data[str(k)]
    new_frame = []
    adjusted_points = []
    for p_frame in frames:
        index, x, y, diff_x, diff_y = [int(x) for x in p_frame.split(',')]
        if adjusted_points:
            last_point = adjusted_points[-1]
            old_index, old_x, old_y, old_diff_x, old_diff_y = last_point
            if index == old_index:  # 同一张diff图片
                if x == old_x:  # 同一行
                    if (old_y + block_base_height == y):
                        #  print(old_y, y)
                        #  print(old_diff_x, old_diff_y, diff_x, diff_y)
                        # 相邻的块儿
                        adjusted_points.append((index, x, y, diff_x, diff_y))
                    else:
                        first_index, first_x, first_y, first_diff_x, first_diff_y = adjusted_points[0]
                        num_1, num_2 = check(first_index, first_x, first_y, first_diff_x, first_diff_y, len(adjusted_points) * block_base_width)
                        new_frame.append(num_1)
                        new_frame.append(num_2)
                        adjusted_points = []
                        adjusted_points.append((index, x, y, diff_x, diff_y))
                else:  # 不同一行
                    if (old_x + block_base_width == x):  # 相邻的行
                        if (old_y + block_base_height == TARGET_IMAGE_WIDTH and y == 0):  # TARGET_IMAGE_WIDTH 是目标图片宽度, 相邻行，回车转接
                            adjusted_points.append((index, x, y, diff_x, diff_y))
                        else:  # 相邻行，回车不转接
                            first_index, first_x, first_y, first_diff_x, first_diff_y = adjusted_points[0]
                            num_1, num_2 = check(first_index, first_x, first_y, first_diff_x, first_diff_y, len(adjusted_points) * block_base_width)
                            new_frame.append(num_1)
                            new_frame.append(num_2)
                            adjusted_points = []
                            adjusted_points.append((index, x, y, diff_x, diff_y))
                    else:  # 不同行且不相邻行
                        first_index, first_x, first_y, first_diff_x, first_diff_y = adjusted_points[0]
                        num_1, num_2 = check(first_index, first_x, first_y, first_diff_x, first_diff_y, len(adjusted_points) * block_base_width)
                        new_frame.append(num_1)
                        new_frame.append(num_2)
                        adjusted_points = []
                        adjusted_points.append((index, x, y, diff_x, diff_y))
            else:  # diff 不在同一张
                first_index, first_x, first_y, first_diff_x, first_diff_y = adjusted_points[0]
                num_1, num_2 = check(first_index, first_x, first_y, first_diff_x, first_diff_y, len(adjusted_points) * block_base_width)
                new_frame.append(num_1)
                new_frame.append(num_2)
                adjusted_points = []
                adjusted_points.append((index, x, y, diff_x, diff_y))
        else:  # 空adjusted_points
            adjusted_points.append((index, x, y, diff_x, diff_y))
    if adjusted_points:
        first_index, first_x, first_y, first_diff_x, first_diff_y = adjusted_points[0]
        num_1, num_2 = check(first_index, first_x, first_y, first_diff_x, first_diff_y, len(adjusted_points) * block_base_width)
        adjusted_points = None
    rt.append(new_frame)


with open("converted.json", "w") as f:
    f.write(json.dumps(rt))
