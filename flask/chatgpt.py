import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def generate_sunrise_frames(res=(8, 10), frames=30):
    height, width = res
    frames_out = []

    for f in range(frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # % of sunrise complete (0 to 1)
        t = f / (frames - 1)

        # Calculate how high the "light" has risen
        lit_rows = int(height * t)

        for y in range(height):
            for x in range(width):
                if y >= height - lit_rows:
                    # Distance from horizon
                    d = height - y

                    # Red/orange ramp depending on distance from "sun"
                    intensity = (1 - d / height) * 255 * (0.5 + 0.5 * t)

                    # Introduce orange/red tone at bottom
                    r = int(min(255, intensity + np.random.randint(0, 30)))
                    g = int(min(100, intensity * 0.4 + np.random.randint(0, 10)))
                    b = int(min(50, intensity * 0.1 + np.random.randint(0, 5)))

                    frame[y, x] = [r, g, b]
                else:
                    # Still dark
                    frame[y, x] = [0, 0, 0]

        frames_out.append(frame)

    return frames_out

def display_animation(frames):
    fig, ax = plt.subplots()
    im = ax.imshow(frames[0], interpolation='nearest')
    ax.axis('off')
    plt.title("Generative Sunrise (Phase 1)")

    def update(i):
        im.set_data(frames[i])
        return [im]

    ani = FuncAnimation(fig, update, frames=len(frames), interval=100, blit=True)
    plt.show()

# === Run ===
sunrise_frames = generate_sunrise_frames(res=(8, 10), frames=30)
display_animation(sunrise_frames)
