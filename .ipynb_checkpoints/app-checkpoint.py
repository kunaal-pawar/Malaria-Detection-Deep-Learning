from flask import Flask, render_template, request
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

app = Flask(__name__)
model = load_model("malaria_final_model.h5")

img_size = 224

def predict_image(img_path):
    img = image.load_img(img_path, target_size=(img_size, img_size))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    prediction = model.predict(img_array)[0][0]
    
    if prediction < 0.5:
        return "Parasitized"
    else:
        return "Uninfected"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        filepath = os.path.join("static", file.filename)
        file.save(filepath)
        result = predict_image(filepath)
        return render_template('index.html', result=result, image_path=filepath)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)