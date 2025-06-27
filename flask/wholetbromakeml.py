import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
# import matplotlib.pyplot as plt
from collections import deque
import random
# from matplotlib.animation import FuncAnimation
import colorsys

def get_muted_contrasting_color(centers):
    # Step 1: average color from cluster centers
    avg_color = np.mean(centers, axis=0).astype(np.uint8)  # shape: (3,)
    r, g, b = avg_color / 255.0  # normalize to [0, 1]

    # Step 2: convert to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Step 3: shift hue by 180° (opposite on color wheel), clamp saturation/value
    h = (h + 0.5) % 1.0          # rotate hue
    s = max(0.2, s * 0.4)        # reduce saturation
    v = min(0.7, v * 0.9)        # slightly darker

    # Step 4: convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (np.array([r, g, b]) * 255).astype(np.uint8)
def clarify_color(point, img_data, labels, centers, stage):
        y,x = point
        true_color = img_data[y, x]
        cluster_idx = labels[y, x]
        cluster_color = centers[cluster_idx]
        k1 = round(random.uniform(0,0.15),2)
        k2 = round(random.uniform(0,0.15),2)
        # Define blend ratios
        blend_weights = [
            (0.7-k1, 0.3+k1),  # Stage 0: mostly cluster color
            (0.5-k2, 0.5+k2),  # Stage 1: equal blend
            (0, 1),  # Stage 2: mostly true color
        ]

        wc, wt = blend_weights[stage]
        blended = (wc * cluster_color + wt * true_color).astype(np.uint8)
        return blended

def brighten_background(canvas1, touched_mask, target_color, max_step=2):
        """
        Randomly brightens each pixel toward a target sky color.
        """
        h, w, _ = canvas1.shape
        noise = np.random.randint(1, max_step + 1, (h, w, 3))

        # Only apply noise to untouched pixels
        untouched_mask = ~touched_mask
        for c in range(3):
            canvas1[..., c] = np.where(
                untouched_mask,
                np.minimum(canvas1[..., c] + noise[..., c], target_color[c]),
                canvas1[..., c]
            )
        return canvas1


def load_and_cluster(image_path, k=5, resize_to=(80, 80)):
    img = Image.open(image_path).convert('RGB').resize(resize_to)
    np_img = np.array(img)
    h, w = np_img.shape[:2]

    flat_pixels = np_img.reshape(-1, 3)
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(flat_pixels)

    cluster_centers = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_.reshape(h, w)

    return np_img, cluster_centers, labels

def downscale_to_8x10(c):
    pil_img = Image.fromarray(c.astype(np.uint8))
    small = pil_img.resize((10, 8), resample=Image.Resampling.BOX)
    return np.array(small)
def get_frames(url):
    frames= []
    img_data, centers, labels = load_and_cluster(url)
    sky_color = get_muted_contrasting_color(centers=centers)
    touched_mask = np.zeros((80, 80), dtype=bool)

   
    canvas = np.zeros((80,80,3), dtype=np.uint8)

    coords = [(x, y) for y in range(80) for x in range(80)]

    # Assign weights: favor bottom pixels (y=79)
    weights = np.array([y for (_, y) in coords])
    weights = (weights + 1) ** 2  # nonlinear bias to increase bottom weight

    # Normalize to 0–1 for consistent scaling
    weights = weights / weights.max()

    # Assign random priority scaled by weights (lower = higher priority)
    prioritized_coords = sorted(
        coords,
        key=lambda c: random.random() / ((c[1] + 1) ** 2), reverse=False # or use weights[c_idx]
    )

    canvas_small = downscale_to_8x10(canvas)
    p1,p2,p3,p4 = -1,-1,-1,-1
    frames = 15
    pixels_per_frame = h*w//frames
    while True:
        canvas = brighten_background(canvas, touched_mask, sky_color)
        for _ in range(pixels_per_frame):
            if p4 >= len(prioritized_coords):
                return frames
            p1 += 1
            p2 += 1 if p1 > 1200 else 0
            p3 += 1 if p2 > 1200 else 0
            p4 += 1 if p3 > 1200 else 0
            if p1 >= 0 and p1 < len(prioritized_coords):
                x, y = prioritized_coords[p1]
                cluster_idx = labels[y, x]
                cluster_color = centers[cluster_idx]
                canvas[y, x] = cluster_color
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

        canvas_small = downscale_to_8x10(canvas)
        frame_data = [
            [{'r': int(pixel[0]), 'g': int(pixel[1]), 'b': int(pixel[2])} for pixel in row]
            for row in canvas_small
        ]
        frames.append(frame_data)



# if __name__ == "__main__":
#     url = "C:/Users/vihas/Documents/GitHub/SunriseLamp/flask/static/uploads/fa401a3f3f32460997caaedb1d573c84_20211229_073930-01.jpeg"
#     get_frames(url)
#     img_data, centers, labels = load_and_cluster(url)
#     h, w = labels.shape

#     canvas = np.zeros((80, 80, 3), dtype=np.uint8)


#     coords = [(x, y) for y in range(80) for x in range(80)]

#     # Assign weights: favor bottom pixels (y=79)
#     weights = np.array([y for (_, y) in coords])
#     weights = (weights + 1) ** 2  # nonlinear bias to increase bottom weight

#     # Normalize to 0–1 for consistent scaling
#     weights = weights / weights.max()

#     # Assign random priority scaled by weights (lower = higher priority)
#     prioritized_coords = sorted(
#         coords,
#         key=lambda c: random.random() / ((c[1] + 1) ** 2), reverse=False # or use weights[c_idx]
#     )
    
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
#     im = ax1.imshow(canvas)
#     ax1.axis('off')
#     touched_mask = np.zeros((80, 80), dtype=bool)

#     canvas_small = downscale_to_8x10(canvas)
#     im_small = ax2.imshow(canvas_small, interpolation='nearest')
#     ax2.set_title("8x10 Preview")
#     ax2.axis('off')
#     sky_color = get_muted_contrasting_color(centers=centers)
#     plt.title("Sunrise Reveal Animation")
#     color_clarity = {0:[],1:[],2:[]}
    

#     p1,p2,p3,p4 = -1,-1,-1,-1
#     def update(frame):
#         global p1, p2, p3, p4, canvas
#         pixels_per_frame = 50
#         canvas = brighten_background(canvas, touched_mask, sky_color)
#         for _ in range(pixels_per_frame):
#             if p4 >= len(prioritized_coords):
#                 return [im]
#             p1 += 1
#             p2 += 1 if p1 > 1200 else 0
#             p3 += 1 if p2 > 1200 else 0
#             p4 += 1 if p3 > 1200 else 0
#             if p1 >= 0 and p1 < len(prioritized_coords):
#                 x, y = prioritized_coords[p1]
#                 cluster_idx = labels[y, x]
#                 cluster_color = centers[cluster_idx]
#                 canvas[y, x] = cluster_color
#                 touched_mask[y, x] = True
#             if p2 >= 0  and p2 < len(prioritized_coords):
#                 x,y = prioritized_coords[p2]
#                 canvas[y,x] = clarify_color((y,x), img_data, labels, centers, 0)
#             if p3 >= 0  and p3 < len(prioritized_coords):
#                 x,y = prioritized_coords[p3]
#                 canvas[y,x] = clarify_color((y,x), img_data, labels, centers, 1)
#             if p4 >= 0  and p4 < len(prioritized_coords):
#                 x,y = prioritized_coords[p4]
#                 canvas[y,x] = clarify_color((y,x), img_data, labels, centers, 2)

#         im.set_data(canvas)
#         canvas_small = downscale_to_8x10(canvas)
#         im_small.set_data(canvas_small)
        
#         return [im, im_small]

#     # Step 6: Run the animation
#     anim = FuncAnimation(fig, update, frames=100, interval=50, blit=True)
#     plt.show()

