from PIL import Image
import numpy as np  # ← Add this line
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def compute_color_grid(image_path, num_frames):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img = img.resize((80, 80), resample=Image.LANCZOS)  # Make sure width is 80, height is 80

        img_np = np.array(img)
        h, w, _ = img_np.shape

        shift_per_frame = w // num_frames  # how many pixels to shift per frame
        frames = []

        for frame in range(num_frames):
            shift = (frame * shift_per_frame) % w

            # Shift image to the left and wrap around
            shifted_img = np.roll(img_np, -shift, axis=1)  # axis=1 for horizontal shift

            frame_grid = []
            for col in range(8):
                col_colors = []
                for row in range(10):
                    x0 = col * 10
                    y0 = row * 8
                    cell = shifted_img[y0:y0+8, x0:x0+10]
                    avg_color = cell.mean(axis=(0, 1)).astype(int)
                    col_colors.insert(0, {
                        "r": int(avg_color[0]),
                        "g": int(avg_color[1]),
                        "b": int(avg_color[2])
                    })
                frame_grid.append(col_colors)
            frames.append(frame_grid)

        return frames
def ai_this_jon(image_path, num_frames):
    frames = []
    with Image.open(image_path) as img:
        img = img.convert("RGB")

        img = img.resize((80, 80), resample=Image.LANCZOS)  # Make sure width is 80, height is 80
        img_np = np.array(img)
      


        # Create grid of average colors
        frame_grid = []
        for col in range(8):
            col_colors = []
            for row in range(10):
                x0 = col * 10
                y0 = row * 8
                cell = img_np[y0:y0+8, x0:x0+10]
                avg_color = cell.mean(axis=(0, 1)).astype(int)
                col_colors.insert(0, {
                    "r": int(avg_color[0]),
                    "g": int(avg_color[1]),
                    "b": int(avg_color[2])
                })
            frame_grid.append(col_colors)
        frames.append(frame_grid)
        
    height = len(frames[0])
    width = len(frames[0][0])
    middle = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            middle[y, x] = [frames[0][y][x]['r'], frames[0][y][x]['g'], frames[0][y][x]['b']]

    # Define start and end frames
    start = np.zeros_like(middle)                      # all black
    end = np.ones_like(middle) * 255                   # all white (or change values if desired)

    # Animation settings
    frames_per_step = 20  # frames from start → middle and middle → end
    total_frames = frames_per_step * 2

    # Prepare figure
    fig, ax = plt.subplots()
    im = ax.imshow(start.astype(np.uint8))
    ax.axis('off')
    plt.title("Interpolating Animation")

    # Animation update function
    def update(frame):
        if frame < frames_per_step:
            alpha = frame / frames_per_step
            current = (1 - alpha) * start + alpha * middle
        else:
            alpha = (frame - frames_per_step) / frames_per_step
            current = (1 - alpha) * middle + alpha * end
        im.set_data(current.astype(np.uint8))
        return [im]

    # Create and show animation
    ani = FuncAnimation(fig, update, frames=total_frames, interval=100, blit=True)
    plt.show()
    return frames

if __name__ == "__main__":
    ai_this_jon("C:/Users/vihas/Documents/GitHub/SunriseLamp/flask/static/uploads/fcff9db1ac964bfd814b8b3ccc04dfaf_4KZsFz.jpg",10)