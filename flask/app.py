import os
import uuid
# import numpy as np  # ← Add this line
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
from collections import deque
from PIL import Image
# import threading
# import time
from werkzeug.utils import secure_filename
# from image_processing import compute_color_grid, ai_this_jon
from wholetbromakeml import get_frames

DEBUG = True
# UPLOAD_FOLDER = './static/uploads/' if DEBUG else '/home/vihas/sunrise-lamp/flask/static/uploads'
UPLOAD_FOLDER =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
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
        url_for('static', filename=f'uploads/{os.path.basename(path)}') for path in list(image_queue)
    ]
    return jsonify({'queue': queue_urls})
@app.route('/current-image')
def get_current_image():
    if(current_image):
        start =  url_for('static', filename=f'uploads/{os.path.basename(current_image)}')
    else:
        start = ""
    return jsonify({'current': [start]})
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
        # processed_colors = compute_color_grid(current_image, 10)
        processed_colors, _ = get_frames(current_image)
        return jsonify({'status': 'processed', 'image': current_image})
    return jsonify({'status': 'idle'})

# threading.Thread(target=process_image_queue, daemon=True).start()




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
        # processed_colors = compute_color_grid(current_image, 10)
                processed_colors, _ = get_frames(current_image)            
            else:
                image_queue.append(filepath)
            return redirect(url_for('index'))


            # Prepare URL for display (assuming /static/uploads is mapped to UPLOAD_FOLDER)
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
 