from flask import Flask, render_template, request
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/save_image', methods=['POST'])
def save_image():
    image_data = request.form['imageData']
    image_name = request.form['imageName']

    # Extract base64-encoded image data
    _, encoded_data = image_data.split(',', 1)
    decoded_data = base64.b64decode(encoded_data)

    # Save the image to a file
    with open(f'{image_name}.jpg', 'wb') as f:
        f.write(decoded_data)

    return 'Image saved successfully'

if __name__ == "__main__":
    app.run(debug=True)
