from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Function to retrieve image from URL and resize to specified dimensions
def get_image_from_url(url, image_width, image_height):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    # Resize image to the specified dimensions
    return image.resize((image_width, image_height))

# Function to add a PNG frame to an image
def add_png_frame(image, frame_path, frame_width, frame_height):
    frame = Image.open(frame_path).convert("RGBA")
    # Resize the frame to the specified dimensions
    frame = frame.resize((frame_width, frame_height), Image.LANCZOS)
    # Ensure the frame size matches the image size
    frame = frame.resize(image.size, Image.LANCZOS)
    image.paste(frame, (0, 0), frame)
    return image

@app.route('/generate_gif', methods=['POST'])
def generate_gif():
    data = request.json
    image_urls = data.get('image_urls', [])
    frame_path = data.get('frame_path', 'frame-gif-wanderlust1.png')  # path to your PNG frame
    frame_width = data.get('frame_width', 700)
    frame_height = data.get('frame_height', 1050)
    image_width = data.get('image_width', 700)  # Specify the image width
    image_height = data.get('image_height', 1050)  # Specify the image height
    
    if not image_urls:
        return jsonify({"error": "No image URLs provided"}), 400
    
    # Create a list to store frames
    frames = []

    # Retrieve images from URLs and create frames
    for url in image_urls:
        image = get_image_from_url(url, image_width, image_height)
        # Create a blank frame
        frame = Image.new("RGB", (frame_width, frame_height), "white")
        # Paste the resized image onto the frame
        frame.paste(image, ((frame_width - image.width) // 2, (frame_height - image.height) // 2))
        # Add the PNG frame
        frame = add_png_frame(frame, frame_path, frame_width, frame_height)
        # Append the frame to the list
        frames.append(frame)

    # Save frames as a GIF
    gif_bytes = BytesIO()
    frames[0].save(gif_bytes, format='GIF', save_all=True, append_images=frames[1:], loop=0, duration=1000)
    gif_bytes.seek(0)
    
    return gif_bytes.getvalue(), 200, {'Content-Type': 'image/gif'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
    # app.run(debug=True)