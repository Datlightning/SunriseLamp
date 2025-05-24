import board
import neopixel
import time
import math
import random

NUM_PIXELS = 80
PIN = board.D6
pixels = neopixel.NeoPixel(PIN, NUM_PIXELS, brightness=0.4, auto_write=False)

def wheel(pos):
    # Generate rainbow colors across 0-255
    if pos < 85:
        return (int(pos * 3), int(255 - pos * 3), 0)
    elif pos < 170:
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))

def rainbow_chase(wait,count, mode):
    for j in range(0,255,count):
        for i in range(NUM_PIXELS):
            
            # Group pixels in chunks of 8
            if(mode):
                group_index = i % 10
            else:
                group_index = i//8  
            pixel_index = (group_index * 256 // 8 + j) & 255
            color = wheel(pixel_index)
            # pixels[i] = (255,255,255)
            pixels[i] = color
        pixels.show()
        time.sleep(wait)

# for i,p in enumerate(pixels): 
#     if i == 0:
#         pixels[0] = (0,0,0)
#         continue
#     pixels[i] = (0,100,100) 
# print("HELLO")
colors = []

for c in range(3):
    # Flicker a few times with varying brightness and delay
    for _ in range(random.randint(1, 3)):
        brightness = random.randint(50, 200)
        color = (brightness, brightness, brightness)
        for i in range(len(pixels)):
            pixels[i] = color
        pixels.show()
        time.sleep(random.uniform(0.05, 0.15))

        for i in range(len(pixels)):
            pixels[i] = (0, 0, 0)
        pixels.show()
        time.sleep(random.uniform(0.1, 0.2))
    
    # Slowly get brighter
    brightness = int((c + 1) / 5.0 * 255)
    for i in range(len(pixels)):
        pixels[i] = (brightness, brightness, brightness)
    pixels.show()
    time.sleep(0.2)

for i in range(len(pixels)):
    pixels[i] = (200,200,200)
pixels.show()
X, Y = 8, 10
pos = 0
hits = 0
trail = []
while True:
  
    # pos += Y + 1
    # hits += 1
    # pos %= X*Y
    # trail.insert(0, pos)
    # if(len(trail) > 3):
    #     pixels[trail.pop()] = (200,200,200) 
    #     pixels[trail[0]] = (255,0,0)
    #     pixels[trail[1]] = (255,125,0)
    #     pixels[trail[2]] = (255,255,0)
        
    # pixels.show()
    # time.sleep(0.1)
    # if hits == 80:
    #     for i in range(len(pixels)):
    #         pixels[i] = (200,200,200)
    #     time.sleep(1)
    #     pixels.show()
    #     hits = 0
    
            
    # for i in range(1,8):
    #     rainbow_chase(0,i, False)  
    # for i in range(1,8 ):
    #     rainbow_chase(0,i, False)
# with open("led-colors.txt", "r") as file:
#     for i,line in enumerate(file.read().split("\n")):
#         pixels[i] = eval(line[3:])
# while True:
    
#         pixels.show()
        # time.sleep(0.4)
#         # pixels[i] = (255,255,255)
# print("hello") 
# while True:
#     pixels.show()
#     time.sleep(5)   