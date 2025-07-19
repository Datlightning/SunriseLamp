import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from collections import deque
import random
from matplotlib.animation import FuncAnimation
import colorsys

def get_muted_contrasting_color(centers):
    # Step 1: average color from cluster centers
    avg_color = np.mean(centers, axis=0).astype(np.uint8)  # shape: (3,)
    r, g, b = avg_color / 255.0  # normalize to [0, 1]

    # Step 2: convert to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Step 3: shift hue by 180° (opposite on color wheel), clamp saturation/value
    h = (h + 0.5) % 1.0          # rotate hue
    s = 0.1      # reduce saturation
    v = min(0.7, v * 0.9)        # slightly darker

    # Step 4: convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    # input(f"Color: {round(r*255)},{round(g*255)},{round(b*255)}/n")

    return (np.array([r, g, b]) * 255).astype(np.uint8)
def amplify_saturation(color):
    r,g,b = color
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Step 3: shift hue by 180° (opposite on color wheel), clamp saturation/value
 
    s = 0.8     # reduce saturation
   

    # Step 4: convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    # input(f"Color: {round(r*255)},{round(g*255)},{round(b*255)}/n")

    return (np.array([r, g, b]) * 255).astype(np.uint8)
    
def clarify_color(point, img_data, labels, centers, stage):
    y, x = point
    true_color = img_data[y, x].astype(np.float32)
    cluster_color = centers[labels[y, x]].astype(np.float32)

    # Slight random blending weights
    k1 = random.uniform(0, 0.15)
    k2 = random.uniform(0, 0.15)
    blend_weights = [
        (0.7 - k1, 0.3 + k1),  # Stage 0
        (0.5 - k2, 0.5 + k2),  # Stage 1
        (0, 1),                # Stage 2
    ]
    wc, wt = blend_weights[stage]

    # Initial blended RGB value
    base_color = wc * cluster_color + wt * true_color
    if(stage == 2):
        return base_color
    # Convert to HSV for better vibrancy control
    r, g, b = base_color / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Slightly jitter hue and increase saturation/value
    h += random.uniform(-0.04 * (3 - stage), 0.04 * (3-stage))
    h = h % 1.0
    s = max(0, s - random.uniform(0.2, 0.4))  # boost saturation
    v = max(0, v - random.uniform(0.1, 0.2))  # boost brightness

    # Convert back to RGB
    r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
    vibrant = np.array([r2, g2, b2]) * 255
    return vibrant.astype(np.uint8)
def brighten_background(canvas1, canvas_copy, touched_mask, target_color, max_step=50):
        """
        Randomly brightens each pixel toward a target sky color.
        """
        
        untouched_mask = ~touched_mask  # shape: (h, w)
        canvas1[untouched_mask] = canvas_copy[untouched_mask]  # sets all 3 channels to 0 for untouched pixels

        # Apply noise update
        for _ in range(3):
            h, w, _ = canvas1.shape
            noise = np.random.randint(0, max_step + 1, (h, w, 3))

            # Recompute the untouched mask in case it's updated elsewhere
            untouched_mask = ~touched_mask
            for c in range(3):
                canvas1[..., c] = np.where(
                    untouched_mask,
                    np.minimum(canvas1[..., c] + noise[..., c], target_color[c]),
                    canvas1[..., c]
                )

        return canvas1
def load_and_cluster(np_img, k=5):

    h, w = np_img.shape[:2]

    flat_pixels = np_img.reshape(-1, 3)
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(flat_pixels)

    cluster_centers = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_.reshape(h, w)

    return np_img, cluster_centers, labels
def downscale_to_8x10(c):
    pil_img = Image.fromarray(c.astype(np.uint8))
    small = pil_img.resize((8, 10), resample=Image.Resampling.BOX)
    return np.array(small)
def prioritize_coords(coords, weights):
    # Get weights based on vertical position
    

    # Prioritize coords using random.random() divided by weight (higher weight → more likely to be early)
    prioritized_coords = sorted(
        zip(coords, weights),
        key=lambda cw: random.random() / cw[1]
    )

    # Strip weights from result
    return [coord for coord, _ in prioritized_coords]
def generate_animation(canvas, end_img, noise=True):
    frames= []
    high_res_frames = []
    img_data, centers, labels = load_and_cluster(end_img)
    sky_color = get_muted_contrasting_color(centers=centers)
    h,w= 80,80
    touched_mask = np.zeros((h,w), dtype=bool)
    canvas_copy = canvas.copy()
    coords = [(x, y) for y in range(80) for x in range(80)]

    # Assign weights: favor bottom pixels (y=79)
    if noise:
        weights = np.array([y for (_, y) in coords])
    else:
        weights = np.array([h - y for (_,y) in coords])
    weights = (weights + 1) ** 2  # nonlinear bias to increase bottom weight

    # Normalize to 0–1 for consistent scaling
    weights = weights / weights.max()

    # Assign random priority scaled by weights (lower = higher priority)
    prioritized_coords = prioritize_coords(coords, weights)


    canvas_small = downscale_to_8x10(canvas)
    p1,p2,p3,p4 = -1,-1,-1,-1
    frame_count = 12 if noise else 10
    pixels_per_frame = h*w//frame_count
    while True:
        if(noise):
            canvas = brighten_background(canvas,canvas_copy, touched_mask, sky_color)
        for _ in range(pixels_per_frame):
            if p4 >= len(prioritized_coords):
                return frames, high_res_frames, sky_color
            p1 += 1
            p2 += 1 if p1 > 1200 else 0
            p3 += 1 if p2 > 1200 else 0
            p4 += 1 if p3 > 1200 else 0
            if p1 >= 0 and p1 < len(prioritized_coords):
                x, y = prioritized_coords[p1]
                cluster_idx = labels[y, x]
                canvas[y, x] = clarify_color((y,x),img_data, labels, centers, -1)
                touched_mask[y, x] = True
            if p2 >= 0  and p2 < len(prioritized_coords):
                x,y = prioritized_coords[p2]
                canvas[y,x] = clarify_color((y,x),img_data, labels, centers, 0)
            if p3 >= 0  and p3 < len(prioritized_coords):
                x,y = prioritized_coords[p3]
                canvas[y,x] = clarify_color((y,x),img_data, labels, centers, 1)
            if p4 >= 0  and p4 < len(prioritized_coords):
                x,y = prioritized_coords[p4]
                canvas[y,x] = clarify_color((y,x),img_data, labels, centers, 2)
        high_frame_data = [
            [(int(pixel[0]), int(pixel[1]),  int(pixel[2])) for pixel in row]
            for row in canvas
        ]
        canvas_small = downscale_to_8x10(canvas)
        frame_data = []
        for col in range(8):
             frame_data.append([])
             for row in range(10):
                  pixel = canvas_small[row][col]
                  frame_data[col].insert(0,( int(pixel[0]), int(pixel[1]), int(pixel[2])))
                  
        frames.append(frame_data)
        high_res_frames.append(high_frame_data)
def generate_sky_blue_gradient(sky_blue, height=80, width=80):
    white = np.array([200, 200, 200], dtype=np.float32)     # White

    gradient = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        # Ratio increases from 0 (top) to 1 (bottom)
        # Bias the gradient so most of it is blue, only last 20% starts fading
        ratio = ((height-y) / height)   # Bias to make transition subtle
        color = (1 - ratio) * sky_blue + ratio * white
        gradient[y, :, :] = color.astype(np.uint8)

    return gradient
def compress(frames):
    output = bytearray()
    for frame in frames:
        for row in frame:
            for pixel in row:
                output += bytes(pixel)
    return output
def unpack(data, frames, width, height):
    assert len(data) == frames * width * height * 3, "Byte length mismatch"
    output_frames = []
    idx = 0
    for _ in range(frames):
        unpacked_data = []
        for _ in range(height):
            row = []
            for _ in range(width):
                r = data[idx]
                g = data[idx + 1]
                b = data[idx + 2]
                row.append(( r, g, b))
                idx += 3
            unpacked_data.append(row)
        output_frames.append(unpacked_data)
    return output_frames
# Create and view the gradient    
def get_frames(url):
    img = Image.open(url).convert('RGB').resize((80,80), Image.Resampling.LANCZOS)
    np_img = np.array(img)
    canvas = np.zeros((80,80,3), dtype=np.uint8)
    start, start_hr, sky_blue = generate_animation(canvas, np_img)

    canvas = generate_sky_blue_gradient(amplify_saturation(sky_blue))
    np_img = np.array(img)
    end, end_hr, _ = generate_animation(np_img, canvas, noise=False)
    return compress(start + end),  compress(start_hr + end_hr)


if __name__ == "__main__":
    url = "C:/Users/vihas/Downloads/download (4).jpeg"
    comp_frames, comp_hr_frames = get_frames(url)
    frames = unpack(comp_frames,frames=30,width=10,height=8)
    hr_frames = unpack(comp_hr_frames,frames=30,width=80,height=80)
    # print(len(frames))
    # print(len(frames[0]))
    # print(len(frames[0][0]))
    long_af_frames = [[[{'r': r, 'g': g, 'b': b} for (r, g, b) in row] for row in data] for data in frames]
    with open("file.txt", "w") as file:
        file.write(str(frames))
        file.close()
    with open("compress.txt", "w") as file:
        file.write(str(comp_frames))
        file.close()
    with open("long.txt", "w") as file:
        file.write(str(long_af_frames))
        file.close()
    print(frames)
    input("Press Enter to Visualize:\n")
    # img_data, centers, labels = load_and_cluster(url)
    # h, w = labels.shape

    # canvas = np.zeros((80, 80, 3), dtype=np.uint8)


    # coords = [(x, y) for y in range(80) for x in range(80)]

    # # Assign weights: favor bottom pixels (y=79)
    # weights = np.array([y for (_, y) in coords])
    # weights = (weights + 1) ** 2  # nonlinear bias to increase bottom weight

    # # Normalize to 0–1 for consistent scaling
    # weights = weights / weights.max()

    # # Assign random priority scaled by weights (lower = higher priority)
    # prioritized_coords = sorted(
    #     coords,
    #     key=lambda c: random.random() / ((c[1] + 1) ** 2), reverse=False # or use weights[c_idx]
    # )
    
    # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    # im = ax1.imshow(canvas)
    # ax1.axis('off')
    # touched_mask = np.zeros((80, 80), dtype=bool)

    # canvas_small = downscale_to_8x10(canvas)
    # im_small = ax2.imshow(canvas_small, interpolation='nearest')
    # ax2.set_title("8x10 Preview")
    # ax2.axis('off')
    # sky_color = get_muted_contrasting_color(centers=centers)
    # plt.title("Sunrise Reveal Animation")
    # color_clarity = {0:[],1:[],2:[]}
    

    # p1,p2,p3,p4 = -1,-1,-1,-1
    # def update(frame):
    #     global p1, p2, p3, p4, canvas
    #     pixels_per_frame = 50
    #     canvas = brighten_background(canvas, touched_mask, sky_color)
    #     for _ in range(pixels_per_frame):
    #         if p4 >= len(prioritized_coords):
    #             return [im]
    #         p1 += 1
    #         p2 += 1 if p1 > 1200 else 0
    #         p3 += 1 if p2 > 1200 else 0
    #         p4 += 1 if p3 > 1200 else 0
    #         if p1 >= 0 and p1 < len(prioritized_coords):
    #             x, y = prioritized_coords[p1]
    #             cluster_idx = labels[y, x]
    #             cluster_color = centers[cluster_idx]
    #             canvas[y, x] = cluster_color
    #             touched_mask[y, x] = True
    #         if p2 >= 0  and p2 < len(prioritized_coords):
    #             x,y = prioritized_coords[p2]
    #             canvas[y,x] = clarify_color((y,x), img_data, labels, centers, 0)
    #         if p3 >= 0  and p3 < len(prioritized_coords):
    #             x,y = prioritized_coords[p3]
    #             canvas[y,x] = clarify_color((y,x), img_data, labels, centers, 1)
    #         if p4 >= 0  and p4 < len(prioritized_coords):
    #             x,y = prioritized_coords[p4]
    #             canvas[y,x] = clarify_color((y,x), img_data, labels, centers, 2)

    #     im.set_data(canvas)
    #     canvas_small = downscale_to_8x10(canvas)
    #     im_small.set_data(canvas_small)
        
    #     return [im, im_small]
    def dict_frame_to_array(frame_dict_2d, rotate=True):
        height = len(frame_dict_2d)
        width = len(frame_dict_2d[0])
        arr = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                pixel = frame_dict_2d[y][x]
                arr[y, x] = [pixel[0], pixel[1], pixel[2]]
        if(rotate):
            return np.rot90(arr, k=1)  # Rotate 90° CCW
        return arr

    np_frames = [dict_frame_to_array(frame) for frame in frames]
    np_hr_frames = [dict_frame_to_array(frame, rotate=False) for frame in hr_frames]
    # --- Plot setup ---
    fig, (ax1, ax2) = plt.subplots(1, 2)
    im1 = ax1.imshow(np_frames[0], animated=True, interpolation='nearest')
    im2 = ax2.imshow(np_hr_frames[0], animated=True, interpolation='nearest')
    ax1.axis('off')
    ax2.axis('off')
    fig.tight_layout()


    # --- Animation function ---
    def update(i):
        im1.set_array(np_frames[i])
        im2.set_array(np_hr_frames[i])
        return [im1, im2]

    ani = FuncAnimation(
    fig, update, frames=len(np_frames), interval=300, blit=True, repeat=True
)

    plt.show()