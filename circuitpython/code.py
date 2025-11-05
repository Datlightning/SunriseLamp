
from os import getenv
 
import adafruit_connection_manager
import adafruit_requests
import board
import busio
import neopixel
from digitalio import DigitalInOut
import time
import math
import random as std_rand

from adafruit_esp32spi import adafruit_esp32spi

ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")

NUM_PIXELS = 80 
PIN = board.D6
pixels = neopixel.NeoPixel(PIN, NUM_PIXELS, brightness=0.5, auto_write=False)

on = False

def wheel(pos):
    """Generate rainbow colors across 0–255 positions."""
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)
def rainbow_chase(wait, groups = 8): 
    for j in range(0,255,5):
        for i in range(NUM_PIXELS):
            group_index = i % groups
            pixel_index = (group_index * 256 // 8 + j) & 255
            color = wheel(pixel_index)
            pixels[i] = color
        pixels.show()
        time.sleep(wait) 
def generate_fire_animate():

    return
def generate_fire_gradient_old(steps=50):
    """
    Generate a fire-like gradient from black → dark red → orange → yellow → white.
    
    Args:
        steps (int): Total number of colors in the gradient.
        
    Returns:
        list[tuple[int, int, int]]: List of RGB tuples.
    """
    # Key fire colors (black, dark red, orange-red, yellow, white)
    key_colors = [
        (0,   0,   0),       # black
        (128, 0,   0),     # dark red
        (255, 69,  0),    # orange-red
        (255, 215, 0),   # golden yellow
        (255, 255, 255)  # white
    ]
    
    gradient = []
    segments = len(key_colors) - 1
    steps_per_segment = steps // segments
    
    for i in range(segments):
        start = key_colors[i]
        end = key_colors[i + 1]
        
        for t in range(steps_per_segment):
            ratio = t / steps_per_segment
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            gradient.append((r, g, b))
    
    # Ensure last color is pure white
    gradient.append(key_colors[-1])
    
    return gradient
def gay_shooting_star(wait):
    x, y = 0, 0
    pixel_trail = []
    steps = 20
    color_offset = 0  # this will cycle colors

    for frame in range(50):
        pos = x * 10 + y
        x += 1
        y += 1
        x %= 8
        y %= 10

        if len(pixel_trail) > steps:
            pixel = pixel_trail.pop(0)
            pixels[pixel] = (0, 0, 0)

        pixel_trail.append(pos)

        # Draw the trail with rainbow colors
        for i, pixel in enumerate(pixel_trail):
            # shift color along the trail & over time
            color_index = (color_offset + i * 10) % 256
            pixels[pixel] = wheel(color_index)

        pixels.show()
        time.sleep(wait)

        color_offset = (color_offset + 5) % 256  # advance rainbow cycle
def shooting_star_gay(wait):
    x, y = 0, 0
    pixel_trail = []
    steps = 20
    frame = 0  # used to animate the base color

    for _ in range(50):
        pos = x * 10 + y
        x += 1
        y += 1
        x %= 8
        y %= 10

        if len(pixel_trail) > steps:
            pixel = pixel_trail.pop(0)
            pixels[pixel] = (0, 0, 0)

        pixel_trail.append(pos)

        # Calculate base color dynamically
        base_r = int((math.sin(frame * 0.1) * 0.5 + 0.5) * 255)
        base_g = int((math.sin(frame * 0.1 + 2*math.pi/3) * 0.5 + 0.5) * 255)
        base_b = int((math.sin(frame * 0.1 + 4*math.pi/3) * 0.5 + 0.5) * 255)
        base_color = (base_r, base_g, base_b)

        # Draw trail: fade out from base color
        for i, pixel in enumerate(pixel_trail):
            fade_ratio = i / len(pixel_trail)  # 0 at head, 1 at tail
            r = int(base_color[0] * (1 - fade_ratio))
            g = int(base_color[1] * (1 - fade_ratio))
            b = int(base_color[2] * (1 - fade_ratio))
            pixels[pixel] = (r, g, b)

        pixels.show()
        time.sleep(wait)
        frame += 1
def generate_dynamic_fire_gradient(steps=50, wheel_pos=0):
    """
    Generate a fire-like gradient from black → shades of a wheel-based color → white.

    Args:
        steps (int): Total number of colors in the gradient.
        wheel_pos (int): 0-255 position to pick the base color from the color wheel.

    Returns:
        list[tuple[int,int,int]]: List of RGB tuples.
    """
    base_color = wheel(wheel_pos % 256)  # dynamic base color from wheel
    r,g,b = base_color
    # Convert to HSV to generate darker/mid/lighter shades
    

    key_colors = [
        (0, 0, 0),  
        (r//4, g//4, b//4),        # black
        base_color, # light shade
        (min(r + r//4, 255), min(g + g//4, 255), min(b + b//4, 255)),
        (255, 255, 255)                     # white
    ]

    # Generate gradient
    gradient = []
    segments = len(key_colors) - 1
    steps_per_segment = max(1, steps // segments)

    for i in range(segments):
        start = key_colors[i]
        end = key_colors[i+1]
        for t in range(steps_per_segment):
            ratio = t / steps_per_segment
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            gradient.append((r, g, b))

    gradient.append(key_colors[-1])
    return gradient
def shooting_star(wait, old = False):
    x,y = 0,0
    pixel_trail = []
    steps = 20

    for offset in range(0,256,4):
        fire_colors = generate_dynamic_fire_gradient(steps=20, wheel_pos=offset) if old else generate_fire_gradient_old(steps=20)
        pos = x * 10 + y
        x += 1
        y += 1
        x %= 8
        y %= 10
        if len(pixel_trail) > steps:
            pixel = pixel_trail.pop(0)
            pixels[pixel] = (0,0,0)
        pixel_trail.append(pos)
        for i, pixel in enumerate(pixel_trail):
            color_index = min(i, len(fire_colors) - 1)
            pixels[pixel] = fire_colors[color_index]
        pixels.show()
        time.sleep(wait)
def clear():
    for i in range(NUM_PIXELS):
        pixels[i] = (0,0,0)
    pixels.show()
def thunder():
    rows = std_rand.randint(0,7)
    pixels_new = list(reversed(range(rows * 10 , (rows + 1) * 10 - 3)))
    for _ in range(std_rand.randint(30,50)):
        pixels_new.insert(0,None)
    pixels_old = []
    while pixels_new:
        pixel = pixels_new.pop(0)
        pixels_old.append(pixel)
        for i in reversed(range(NUM_PIXELS)):
            if i == pixel:
                pixels[i] = (121 + std_rand.randint(-5,5), 228 + std_rand.randint(-5,5), 242 + std_rand.randint(-1,5))
               
            elif i not in pixels_new and i not in pixels_old:
                color = pixels[i][0] 
                cloud = std_rand.randint(-1,1)
                color += cloud
                color = max(0,min(10,color))  
                pixels[i] = (color, color, color)  
        pixels.show()
        time.sleep(0.01)

    time.sleep(0.5)
offset = 0
select = std_rand.randint(0,8)

while on:
    select += 1 
    select %= 8
    print(select)
    if select == 0:
        clear()
        shooting_star( 0.05)  # mo elify shooting_star to accept fire_colors
    elif select == 1:
        clear()
        shooting_star_gay(0.05)
    elif select == 2:
        clear()
        shooting_star(0.05, old=True)
    elif select == 3:
        clear()
        gay_shooting_star(0.05)
    elif select == 4:
        rainbow_chase(0.05, groups=4)
    elif select == 5:
        rainbow_chase(0.05, groups=8)
    elif select == 6:
        rainbow_chase(0.05, groups=16)
    elif select == 7:
        thunder()
        thunder()
        thunder()
print("ESP32 SPI webclient test")
  
BASE_URL = "http://sunriselamp.pythonanywhere.com//"
JSON_URL = BASE_URL + "/processed-image"

LITE_JSON_URL = BASE_URL + "/get-update-lite"
DEFAULT = BASE_URL + "/default"


esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

if "SCK1" in dir(board):
    spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
else:
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

pool = adafruit_connection_manager.get_radio_socketpool(esp)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
requests = adafruit_requests.Session(pool, ssl_context)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
 
while not esp.is_connected: 
    try:
        esp.connect_AP(ssid, password)
    except OSError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print('connected')
def interpolate_frames(frame1, frame2, steps):
    """Generates intermediate frames between frame_a and frame_b."""
    interpolated = []

    for step in range(1, steps + 1):
        t = step / (steps )
        frame = []
        for arc in range(len(frame1)):
            row = []
            for height in range(len(frame1[arc])):
                r1, g1, b1 = frame1[arc][height]
                r2, g2, b2 = frame2[arc][height]
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                row.append((r, g, b))
            frame.append(row)
        interpolated.append(frame)

    return interpolated
def decode_frame_stream(b64_data, width, height, mode=0):
    BASE64_LOOKUP = {c: i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")}
    b64_data = b64_data.rstrip("=")
    if len(b64_data) % 4:
        b64_data += "A" * (4 - len(b64_data) % 4)

    def byte_stream():
        for i in range(0, len(b64_data), 4):
            n = (
                (BASE64_LOOKUP[b64_data[i]] << 18) +
                (BASE64_LOOKUP[b64_data[i+1]] << 12) +
                (BASE64_LOOKUP[b64_data[i+2]] << 6) +
                (BASE64_LOOKUP[b64_data[i+3]])
            )
            yield (n >> 16) & 0xFF
            yield (n >> 8) & 0xFF
            yield n & 0xFF
    while mode == 1:  # infinite loop over whole sequence
        stream = byte_stream()
        try:
            for _ in range(len(b64_data) * 3 // (width * height * 3)):  # number of frames per loop
                frame = []
                for _ in range(width):
                    row = []
                    for _ in range(height):
                        r = next(stream)
                        g = next(stream)
                        b = next(stream)
                        row.append((r, g, b))
                    frame.append(row)
                yield frame
        except StopIteration:
            pass
    stream = byte_stream()
    try:
        while True:
            frame = []
            for _ in range(width):
                row = []
                for _ in range(height):
                    r = next(stream)
                    g = next(stream)
                    b = next(stream)
                    row.append((r, g, b))
                frame.append(row)
            yield frame
    except StopIteration:
        return
percent_left = 0
pixel_indices = [(arc, height) for arc in range(8) for height in range(10)]
brightness = 0
def scale_color(color, brightness):
    return tuple(int(c * brightness) for c in color)
i = 1

toggle = True
while True:
    if toggle:
        i += 1
        toggle = False
    else:
        toggle = True
    i %= 16
    picture_id = None
    try: 
        # Load and decode color data
        r = requests.get(LITE_JSON_URL)
        pic_id_new = r.json()['id']
        if pic_id_new != picture_id:
            r = requests.get(JSON_URL)
            picture_id = pic_id_new
        
        enc_colors = r.json()['colors']
        mode = r.json()['type']
        frame_gen = decode_frame_stream(enc_colors, width=8, height=10, mode=mode)
        frame_count = 2

        prev_frame = next(frame_gen)   # first frame
        current = next(frame_gen)  
        next_frame = next(frame_gen)    # preload one ahead

        while True:
            # Interpolate between the two frames
            interpolated = interpolate_frames(prev_frame, current, steps=10)
            for frame in interpolated:
                for arc in range(8):
                    for height in range(10):
                        color = frame[arc][height]
                        pixels[arc * 10 + height] = scale_color(color, 0.3 if mode == 0 else 1)
                pixels.show()
                time.sleep(0.03)  # ~30fps

            # Shift forward: current becomes prev
            prev_frame = current

            try:
                # Load the next frame *while displaying the last interpolated one*
                current = next_frame
                next_frame = next(frame_gen)
                frame_count += 1
                if frame_count % 20 == 0:
                    r = requests.get(LITE_JSON_URL)
                    pic_id_new = r.json()['id']
                    if pic_id_new != picture_id:
                        picture_id = pic_id_new
                        break  # exit to outer loop to fetch new data
            except StopIteration:
                break  # no more frames

        print("Total frames received:", frame_count)  # <-- Print the count
        del frame_gen
        del prev_frame
        del current
        del interpolated

        time.sleep(4 if mode == 0 else 0)

    except Exception as e:
        print("Exception occurred:", repr(e))
        if "MemoryError" in repr(e):
            import microcontroller
            microcontroller.reset() 
        try:
            r = requests.get(DEFAULT)
            selected = r.json()['selected']
            selected = int(selected)
            print("Default effect:", selected)
            if selected == 0: 
                clear()
                shooting_star( 0.05)  # mo elify shooting_star to accept fire_colors
            elif selected == 1:
                clear()
                shooting_star_gay(0.05)
            elif selected == 2:
                clear()
                shooting_star(0.05, old=True)
            elif selected == 3:
                clear()
                gay_shooting_star(0.05)
            elif selected == 4:
                rainbow_chase(0.05, groups=4)
            elif selected == 5:
                rainbow_chase(0.05, groups=8)
            elif selected == 6:
                rainbow_chase(0.05, groups=16)
            elif selected == 7:
                thunder()
        except:
            rainbow_chase(0.02,i)