from flask import Flask, request, jsonify
import requests
from PIL import Image, ImageOps
from io import BytesIO

app = Flask(__name__)

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        print("Failed to download image from URL:", url)
        return None

def create_up_down_collage(image1_url, image2_url, output_path, frame_width=15, frame_color=(255, 0, 0), img_width=700, img_height=1050, space=10):
    # Download images from URLs
    image1 = download_image(image1_url)
    image2 = download_image(image2_url)

    if image1 and image2:
        # Resize images if width and height are specified
        if img_width and img_height:
            image1 = image1.resize((img_width, img_height), Image.LANCZOS)
            image2 = image2.resize((img_width, img_height), Image.LANCZOS)
        
        # Add space around images
        image1 = ImageOps.expand(image1, border=space, fill=(255, 0, 0))
        image2 = ImageOps.expand(image2, border=space, fill=(255, 0, 0))

        # Get the width and height of each image after resizing
        width1, height1 = image1.size
        width2, height2 = image2.size

        # Calculate the new dimensions of the collage
        new_width = max(width1, width2) + 2 * frame_width
        new_height = height1 + height2 + 2 * frame_width

        # Create a new image with a frame color background
        collage = Image.new('RGB', (new_width, new_height), frame_color)

        # Paste the first image at the top
        collage.paste(image1, (frame_width, frame_width))

        # Paste the second image at the bottom
        collage.paste(image2, (frame_width, height1 + frame_width))

        # Add the outer frame around the collage
        collage_with_frame = ImageOps.expand(collage, border=frame_width, fill=frame_color)

        # Save the final collage
        collage_with_frame.save(output_path)

@app.route('/create_kolase', methods=['POST'])
def create_kolase():
    data = request.json
    image1_url = data.get('image1_url')
    image2_url = data.get('image2_url')
    output_path = data.get('output_path')

    if not image1_url or not image2_url or not output_path:
        return jsonify({'error': 'Missing image URLs or output path'}), 400

    create_up_down_collage(image1_url, image2_url, output_path)
    return jsonify({'message': 'Kolase created successfully'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)