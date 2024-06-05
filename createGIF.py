from flask import Flask, request, jsonify
import requests
from PIL import Image, ImageDraw
from io import BytesIO
import json
import logging

app = Flask(__name__)

# Function to retrieve image from URL
def get_image_from_url(url, frame_width, frame_height):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    # Calculate aspect ratio
    aspect_ratio = min(frame_width / image.width, frame_height / image.height)
    # Resize image to fit within the frame
    new_width = int(image.width * aspect_ratio)
    new_height = int(image.height * aspect_ratio)
    return image.resize((new_width, new_height))

# Create a function to draw a default frame
def draw_frame(image, frame_width, frame_height):
    draw = ImageDraw.Draw(image)
    draw.rectangle([10, 10, frame_width - 10, frame_height - 10], outline="black", width=5)

@app.route('/generate_gif', methods=['POST'])
def generate_gif():
    data = request.json
    image_urls = data.get('image_urls', [])
    logging.error("Division by zero!")
    
    if not image_urls:
        return jsonify({"error": "No image URLs provided"}), 400
    
    # Set dimensions
    frame_width = 1050
    frame_height = 700
    # Create a list to store frames
    frames = []

    # Retrieve images from URLs and create frames
    for url in image_urls:
        image = get_image_from_url(url, frame_width, frame_height)
        # Create a blank frame
        frame = Image.new("RGB", (frame_width, frame_height), "white")
        # Paste the resized image onto the frame
        frame.paste(image, ((frame_width - image.width) // 2, (frame_height - image.height) // 2))
        # Draw the default frame
        draw_frame(frame, frame_width, frame_height)
        # Append the frame to the list
        frames.append(frame)

    # Determine the dimensions of the GIF based on the dimensions of the frames
    gif_width = max(image.width for image in frames)
    gif_height = max(image.height for image in frames)

    # Save frames as a GIF with dimensions based on the frames
    gif_bytes = BytesIO()
    frames[0].save(gif_bytes, format='GIF', save_all=True, append_images=frames[1:], loop=0, duration=1000, width=gif_width, height=gif_height)
    gif_bytes.seek(0)
    
    return gif_bytes.getvalue(), 200, {'Content-Type': 'image/gif'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)