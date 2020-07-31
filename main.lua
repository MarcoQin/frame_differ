-- frames = require("frames")
frames = require("frames1")
require ("bit")
-- love.graphics.setDefaultFilter("nearest", "nearest")
-- 
-- IMAGE_WIDTH = 960
-- IMAGE_HEIGHT = 720
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 800

canvas = love.graphics.newCanvas(IMAGE_WIDTH, IMAGE_HEIGHT)
-- canvas = love.graphics.newCanvas(1280, 720)

images = {}

function love.load()
    -- table.insert(images, love.graphics.newImage("diff0.jpg"))
    -- table.insert(images, love.graphics.newImage("diff0-min.jpg"))
    -- for i = 0, 11 do
    for i = 0, 2 do
        print(i)
        -- f_name = "diff"..tostring(i).."-min.jpg"
        f_name = "diff"..tostring(i)..".jpg"
        -- f_name = "fuck/min/diff"..tostring(i).."-min.jpg"
        table.insert(images, love.graphics.newImage(f_name))
    end

    love.graphics.setCanvas(canvas)
        love.graphics.clear()
        -- love.graphics.setBlendMode("alpha")
        -- love.graphics.setColor(255, 255, 255, 255)
        -- love.graphics.rectangle('fill', 0, 0, 100, 100)
    love.graphics.setCanvas()
end

function split(inputstr, sep)
        if sep == nil then
            sep = "%s"
        end
        local t={} ; i=1
        for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
                t[i] = tonumber(str)
                i = i + 1
        end
        return t
end

frame = 1
st = 0

raw_image = nil


function love.update(dt)
    st = st + dt
    if st >= 0.033 then  -- 0.06
    -- if st >= 1 then  -- 0.06
        st = 0
        frame = frame + 1
        if frame > #frames then
            frame = 1
        end
        data = frames[frame]
        canvas:renderTo(function()
            if frame == 1 then
                love.graphics.clear()
            end
            -- love.graphics.setColor(255, 255, 255, 255)
            -- love.graphics.setColor(255, 255, 255, 255)
            len = #data
            local offset = 0
            for idx = 1, len, 2 do
                -- offset = offset + 10
                num_1 = data[idx]
                num_2 = data[idx + 1]
                index = bit.band(bit.rshift(num_1, 22), 0x1f)
                img = images[index + 1]  -- convert lua index 0 to 1
                y = bit.band(bit.rshift(num_1, 11), 0x7ff)
                x = bit.band(num_1, 0x7ff)
                block_width = bit.band(bit.rshift(num_2, 22), 0x3ff)
                y1 = bit.band(bit.rshift(num_2, 11), 0x7ff)
                x1 = bit.band(num_2, 0x7ff)
                -- block_width = bit.band(bit.rshift(num_2, 20), 0x3ff)
                -- y1 = bit.band(bit.rshift(num_2, 10), 0x3ff)
                -- x1 = bit.band(num_2, 0x3ff)
                w, h = img:getDimensions()
                -- print("num1", num_1, index)
                -- print("num1", num_1, index, y, x)
                -- print("num2", num_2, block_width, y1, x1)
                -- quad = love.graphics.newQuad(x1, y1, block_width, 8, w, h)
                -- love.graphics.draw(img, quad, x, y)
                -- print(x, y, block_width)



                while block_width > 0 do
                    if (x1 + block_width) > w then  -- 块儿跨行了
                        valid_width = w - x1
                        -- print("too long")
                        -- print(block_width, x1, w, valid_width)
                        block_width = block_width - valid_width
                        quad = love.graphics.newQuad(x1, y1, valid_width, 8, w, h)
                        love.graphics.draw(img, quad, x, y+offset)
                        -- love.graphics.rectangle('line', x, y, valid_width, 8)
                        x = x + valid_width
                        x1 = x1 + valid_width
                        if x >= IMAGE_WIDTH then  -- 目标图片宽度
                            x = 0
                            y = y + 8
                        end
                        if x1 >= 2048 then
                            x1 = 0
                            y1 = y1 + 8
                        end
                    else
                        quad = love.graphics.newQuad(x1, y1, block_width, 8, w, h)
                        love.graphics.draw(img, quad, x, y+offset)
                        -- love.graphics.rectangle('line', x, y, block_width, 8)
                        block_width = 0
                    end
                end
            end




            -- for _, p_f in ipairs(data) do
                -- ss = split(p_f, ",")
                -- index = ss[1] + 1
                -- img = images[index]
                -- y = ss[2]
                -- x = ss[3]
                -- y1 = ss[4]
                -- x1 = ss[5]
                -- -- print(x, y, x1, y1)
                -- quad = love.graphics.newQuad(x1, y1, 8, 8, img:getDimensions())
                -- love.graphics.draw(img, quad, x, y)
            -- end
            --  love.graphics.draw(images[2], 0, 0)
            --
            --
            --
            --
        end)
        -- local canvasData = canvas:newImageData()
        -- canvasData:encode("png", tostring(frame)..".png")
        -- if frame == 20 then
            -- local canvasData = canvas:newImageData()
            -- canvasData:encode("png", "pic.png")
        -- end
        raw_image = love.graphics.newImage(string.format("imgs/core_s_%05d.jpg", frame - 1))
    end
end


function love.draw()

    love.graphics.clear()
    love.graphics.setBackgroundColor( 255, 255, 255 )
    love.graphics.setColor(255, 255, 255, 255)
    -- love.graphics.setColor(255, 255, 255, 255)
    -- love.graphics.setColor(0, 0, 0, 255)
    -- love.graphics.setBlendMode("alpha", "premultiplied")
    if raw_image then
        love.graphics.draw(raw_image, 500, 0, 0, 0.5, 0.5)
    end
    love.graphics.draw(canvas, 0, 0, 0, 1, 1)
    -- love.graphics.draw(canvas, -100, -500, 0, 1, 5)
    -- love.graphics.draw(canvas, 0, 0, 0, 0.5, 0.5)
    -- data = frames[frame]
    --         -- love.graphics.setColor(0, 0, 0, 255)
    --         for _, p_f in ipairs(data) do
    --             ss = split(p_f, ",")
    --             index = ss[1] + 1
    --             img = images[index]
    --             y = ss[2]
    --             x = ss[3]
    --             y1 = ss[4]
    --             x1 = ss[5]
    --             -- print(x, y, x1, y1)
    --             quad = love.graphics.newQuad(x1, y1, 8, 8, img:getDimensions())
    --             love.graphics.draw(img, quad, x, y)
    --         end
    -- love.graphics.draw(images[2], -500, -500)
    -- love.graphics.draw(images[4], 0, 0)
end
