# frame differ

导出的格式为二元数组，每个内部的数组都代表一帧。数组里以两个 int 为一组数据，这里以 num1, num2 表示，如下：

```
[
	[num1, num2, num1, num2], // 第一帧
	[num1, num2, num1, num2], // 第二帧
	[num1, num2, num1, num2], // 第三帧
	...
]

```

num1 和 num2 的转换方式如下：

```
图片坐标以这样的方式记录:
          0  y y y y y y y y
          x
          x
          x
          x
          x
          
          index range: 0 - 31 // diff 图片 index 范围
          block_width range: 4 - 1000  // 每个连续 block 长度范围


          diff_image_index = (num_1 >> 22) & 0x1f  // 从 num_1 得知图片 index
          // 原始帧（还未转换的帧）的坐标
          x = (num_1 >> 11) & 0x7ff  
          y = num_1 & 0x7ff
          
          // 对应的 diff 图片上的图像块儿坐标
          block_width = (num_2 >> 22) & 0x3ff  // 如果几个块是连续的，那就当做一个连续的块看待
          diff_x = (num_2 >> 11) & 0x7ff
          diff_y = num_2 & 0x7ff
```



直接播放示例代码(lua):

```lua
data = frames[frame] 
canvas:renderTo(function()
    if frame == 1 then
      love.graphics.clear()
    end
    len = #data

    for idx = 1, len, 2 do -- 以 2 为 step 循环当前帧所在的数组。
      num_1 = data[idx]
      num_2 = data[idx + 1]
      -- 从 num_1 和 num_2 做坐标转换
      index = bit.band(bit.rshift(num_1, 22), 0x1f)
      -- 通过 index 拿到 diff 图像
      img = images[index + 1]  -- convert lua index 0 to 1
      y = bit.band(bit.rshift(num_1, 11), 0x7ff)
      x = bit.band(num_1, 0x7ff)
      block_width = bit.band(bit.rshift(num_2, 22), 0x3ff)
      y1 = bit.band(bit.rshift(num_2, 11), 0x7ff)
      x1 = bit.band(num_2, 0x7ff)

      w, h = img:getDimensions()

      while block_width > 0 do
        if (x1 + block_width) > w then  -- 块儿跨行了，先把本行的读完，然后再读下一行数据
          valid_width = w - x1
          block_width = block_width - valid_width
          -- quad 是从 diff 图片中根据坐标拿的一小块图片, 一般 block_width 长，8 像素高
          quad = love.graphics.newQuad(x1, y1, valid_width, 8, w, h)
          love.graphics.draw(img, quad, x, y)  -- 直接在 canvas 上覆盖绘制
          x = x + valid_width
          x1 = x1 + valid_width
          if x >= IMAGE_WIDTH then  -- 目标图片宽度，这里是 800
            x = 0
            y = y + 8
          end
          if x1 >= 2048 then
            x1 = 0
            y1 = y1 + 8
          end
        else
          quad = love.graphics.newQuad(x1, y1, block_width, 8, w, h)
          love.graphics.draw(img, quad, x, y)
          block_width = 0
        end
      end
    end

  end)
```

上述代码能把当前帧的图像绘制在 canvas 上。

因为是累计式 diff，后一帧的图像依赖于前一帧，所以每次绘制不能将前一帧的图像擦除（除了第一帧）。

可以使用的办法是，先把所有的帧绘制一遍，没绘制一帧便将当前的 canvas 做 snapshot，之后就无须再根据 diff 绘制（而且根据 diff 无法朝前播放）