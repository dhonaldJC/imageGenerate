import os
import base64
import requests
from flask import Flask, request, jsonify, send_file, url_for
from flask_cors import CORS
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.RequestException as e:
        print(f"Failed to download image from URL {url}: {e}")
        return None

def add_png_frame(image, frame_path):
    frame = Image.open(frame_path).convert("RGBA")
    # Ensure the frame retains its original size
    frame = frame.resize(image.size, Image.LANCZOS)
    frame.paste(image, (0, 0), image)
    return frame

def crop_top(image, percent):
    width, height = image.size
    crop_height = int(height * percent)
    # Crop the top portion
    cropped_image = image.crop((0, 0, width, crop_height))
    return cropped_image

def create_up_down_collage(image1_url, image2_url, output_path, frame_path=None, crop_percent=0, collage_size=(700, 1050)):
    # Download images from URLs
    image1 = download_image(image1_url)
    image2 = download_image(image2_url)

    if image1 and image2:
        # Resize images if needed
        image1 = image1.resize((300, 500), Image.LANCZOS)  # Resize image1 to 300x500
        image2 = image2.resize((300, 500), Image.LANCZOS)  # Resize image2 to 300x500

        # Crop image1 at the top by the specified percentage
        image1 = crop_top(image1, crop_percent)

        # Get the width and height of each image
        width1, height1 = image1.size
        width2, height2 = image2.size

        # Calculate the new dimensions of the collage
        new_width = max(width1, width2)
        new_height = height1 + height2

        # Create a new image with a transparent background
        collage = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))

        # Paste the first image at the top
        collage.paste(image1, (0, 0))

        # Paste the second image at the bottom
        collage.paste(image2, (0, height1))

        # Resize the collage to desired dimensions
        collage = collage.resize(collage_size, Image.LANCZOS)

        # If frame_path is provided, add it on top of all elements
        if frame_path:
            frame = Image.open(frame_path).convert("RGBA")
            # Ensure the frame retains its original size
            frame = frame.resize(collage.size, Image.LANCZOS)
            collage = Image.alpha_composite(collage, frame)
            
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the final collage
        collage.save(output_path)

@app.route('/create_kolase', methods=['POST'])
def create_kolase():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    image1_url = data.get('image1_url')
    image2_url = data.get('image2_url')
    if not image1_url or not image2_url:
        return jsonify({'error': 'Missing image URLs'}), 400

    output_dir = data.get('output_dir', 'output')
    output_path = os.path.join(output_dir, 'kolase.png')
    frame_path = data.get('frame_path', 'frame-photo-wanderlust1.png')
    crop_percent = data.get('crop_percent', 0.8)
    collage_size = data.get('collage_size', (700, 1050))

    os.makedirs(output_dir, exist_ok=True)
    create_up_down_collage(image1_url, image2_url, output_path, frame_path, crop_percent, collage_size)

    # Encode the saved image to Base64
    with open(output_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Generate the URL for the image
    image_url = url_for('serve_image', filename='kolase.png', _external=True)

    # Prepare the JSON response
    response_data = {
        'message': 'Collage created successfully',
        'collage_base64': encoded_image,
        'collage_url': image_url
    }

    return jsonify(response_data), 200

@app.route('/images/<filename>')
def serve_image(filename):
    return send_file(os.path.join('output', filename), mimetype='image/png')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
    # app.run(debug=True)