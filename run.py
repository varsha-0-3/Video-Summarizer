from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import cv2
import numpy as np
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['video']
    threshold = float(request.form.get('threshold', 20.0))
    if file:
        video_filename = file.filename
        video_path = os.path.join(UPLOAD_FOLDER, video_filename)
        output_filename = f'summarized_{video_filename}'
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        file.save(video_path)
        summarize_video(video_path, output_path, threshold)
        
        return redirect(url_for('download', filename=output_filename))
    return "No file uploaded", 400

@app.route('/outputs/<filename>')
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

def summarize_video(input_path, output_path, threshold):
    video = cv2.VideoCapture(input_path)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)

    # Use 'mp4v' codec for MP4 files
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    ret, frame1 = video.read()
    prev_frame = frame1
    while True:
        ret, frame = video.read()
        if not ret:
            break
        if np.sum(np.abs(frame - prev_frame)) / np.size(frame) > threshold:
            writer.write(frame)
            prev_frame = frame
    video.release()
    writer.release()

if __name__ == '__main__':
    app.run(debug=True)