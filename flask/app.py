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
from wholetbromakeml import get_frames, compress, unpack
from image_processing import compute_color_grid
import base64

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
mode = 0
picture_id = 0
effect = 0
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def extension(filename):
    return "." + filename.rsplit('.', 1)[1].lower()



@app.route('/queue')
def get_image_queue():
    # Send URLs for the queued images (not the one currently processing)
    queue_urls = [
        url_for('static', filename=f'uploads/{os.path.basename(path)}') for path in list(map(lambda x: x[1],  list(image_queue)))
    ]
    return jsonify({'queue': queue_urls})
@app.route('/epic-debug')
def epic_debug():
    return jsonify({'queue': list(image_queue)})
@app.route('/current-image')
def get_current_image():
    if(current_image):
        start =  url_for('static', filename=f'uploads/{os.path.basename(current_image)}')
    else:
        start = ""
    return jsonify({'current': [start]})
#192.168.68.133
@app.route('/get-update-lite')
def get_update_lite():
    global picture_id
    return jsonify({'id': picture_id})
@app.route('/regular-colors')
def get_regular_colors():
    global processed_colors
    if(processed_colors):
        b64_colors = unpack(processed_colors)
        return jsonify({"colors": b64_colors})
    else:
        return jsonify({"colors":""})
@app.route('/process-image-queue')
def process_image_queue():

    token = request.args.get("token")
    if token != SECRET_KEY:
        abort(403)

    global processed_colors, current_image, picture_id
    if image_queue:
        if current_image:
            os.remove(current_image)
        instruction, current_image = image_queue.popleft()
        picture_id += 1
        picture_id %= 2
        # processed_colors = compute_color_grid(current_image, 10)
        if instruction == 0:
            processed_colors, _ = get_frames(current_image)
        else :
            processed_colors = compress(compute_color_grid(current_image, 10))
        return jsonify({'status': 'processed', 'image': current_image})
    return jsonify({'status': 'idle'})

# threading.Thread(target=process_image_queue, daemon=True).start()




@app.route('/processed-image', methods=['GET'])
def get_processed_image():
    global processed_colors
    global mode

    if(processed_colors):
        b64_colors = base64.b64encode(processed_colors).decode('utf-8')
        return jsonify({"colors": b64_colors, "type":mode})
    else: 
        return jsonify({"colors":[], "type":None})
@app.route('/processed-image1', methods=['GET'])
def get_processed_image1():
    global processed_colors
    if(processed_colors):
        b64_colors = base64.b64encode(processed_colors).decode('utf-8')
        return jsonify({"colors": b64_colors})
    else:
        return jsonify({"colors":""})
@app.route('/default')
def default():
    global effect
    print(effect)
    return jsonify({"selected": effect})
@app.route('/', methods=['GET', 'POST'])
def index():
    global image_queue
    global processed_colors
    global current_image
    global mode
    global effect
    uploaded_url = None

    if request.method == "POST":
        action = request.form.get("action")
        if action == "default":
            print('it work')
            effect = request.form.get("effect")
            
            current_image = None
            processed_colors = None
            mode = None
            image_queue.clear()
            return redirect(url_for('index'))

              # "sunrise" or "panorama"
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
                mode = 0 if action=="sunrise" else 1

        # processed_colors = compute_color_grid(current_image, 10)
                if action=="sunrise":
                    processed_colors, _ = get_frames(current_image)            
                else:
                    processed_colors = compress(compute_color_grid(current_image, 10))
            else:
                mode = 0 if action=="sunrise" else 1
                image_queue.append((0 if action=="sunrise" else 1, filepath))
            return redirect(url_for('index'))


            # Prepare URL for display (assuming /static/uploads is mapped to UPLOAD_FOLDER)
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
 