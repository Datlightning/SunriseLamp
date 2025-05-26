import os
import uuid
import numpy as np  # ← Add this line
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
from collections import deque
from PIL import Image
import threading
import time
from werkzeug.utils import secure_filename



UPLOAD_FOLDER = './static/uploads/'
ALLOWED_EXTENSIONS = {'jpg', 'png', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
SECRET_KEY = "68c2b6ceb89ed3cd1f1c0e78d5fd79f710bef290bda90a70"
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
image_queue = deque()
current_image = None
processed_colors = []  # Global variable to hold the grid of RGB values

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def extension(filename):
    return "." + filename.rsplit('.', 1)[1].lower()



@app.route('/queue')
def get_image_queue():
    # Send URLs for the queued images (not the one currently processing)
    queue_urls = [
        f'/static/uploads/{os.path.basename(path)}' for path in list(image_queue)
    ]
    return jsonify({'queue': queue_urls})
@app.route('/current-image')
def get_current_image():
    url = f'/static/uploads/{os.path.basename(current_image)}'
    return jsonify({'current': [url]})
#192.168.68.133
@app.route('/process-image-queue')
def process_image_queue():

    token = request.args.get("token")
    if token != SECRET_KEY:
        abort(403)

    global processed_colors, current_image
    if image_queue:
        if current_image:
            os.remove(current_image)
        current_image = image_queue.popleft()
        processed_colors = compute_color_grid(current_image)
        return jsonify({'status': 'processed', 'image': current_image})
    return jsonify({'status': 'idle'})

# threading.Thread(target=process_image_queue, daemon=True).start()

def compute_color_grid(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img = img.resize((80, 80))  # Resize to simplify averaging

        grid = []
        for row in range(8):
            row_colors = []
            for col in range(10):
                cell = img.crop((col*8, row*10, (col+1)*8, (row+1)*10))
                pixels = np.array(cell)
                avg_color = pixels.mean(axis=(0, 1)).astype(int)
                row_colors.append({
                    "r": int(avg_color[0]),
                    "g": int(avg_color[1]),
                    "b": int(avg_color[2])
                })
            grid.append(row_colors)
        return grid
    


@app.route('/processed-image', methods=['GET'])
def get_processed_image():
    global processed_colors
    return jsonify({"colors": processed_colors})

@app.route('/', methods=['GET', 'POST'])
def index():
    global image_queue
    global processed_colors
    global current_image

    uploaded_url = None

    if request.method == "POST":
        file = request.files.get('file')
        if file and file.filename != '':
            # Sanitize original filename
            safe_name = secure_filename(file.filename)

            # Generate unique filename by prepending UUID hex string
            unique_name = f"{uuid.uuid4().hex}_{safe_name}"

            # Full path to save
            filepath = os.path.join(UPLOAD_FOLDER, unique_name)

            # Open, convert, save image
            image = Image.open(file.stream).convert('RGB')
            image.save(filepath)

            # Add to queue
            if not current_image:
                current_image = filepath
                processed_colors = compute_color_grid(filepath)
            else:
                image_queue.append(filepath)
            return redirect(url_for('index'))


            # Prepare URL for display (assuming /static/uploads is mapped to UPLOAD_FOLDER)
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
 