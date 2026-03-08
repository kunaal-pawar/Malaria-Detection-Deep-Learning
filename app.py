import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import logging
logging.getLogger('absl').setLevel(logging.ERROR)

import time
import io
import datetime
from flask import Flask, render_template, request, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global mock stats
scans_today = 2852

# ── Load all 3 models ──────────────────────────────────────────────────────────
MODEL_FILES = {
    'CustomCNN':      'best_custom_cnn_malaria_model.h5',
    'MobileNetV2':    'best_mobilenetv2_malaria_model.h5',
    'EfficientNetB0': 'best_efficientnet_malaria_model.h5',
}

models = {}
target_sizes = {}

print("\n" + "="*70)
print("MALARIA DETECTION - LOADING ALL 3 MODELS")
print("="*70)

for model_name, filename in MODEL_FILES.items():
    if os.path.exists(filename):
        try:
            print(f"Loading {model_name}...")
            m = load_model(filename)
            models[model_name] = m
            # Infer target size from model input shape
            try:
                input_shape = m.input_shape
                if input_shape and len(input_shape) >= 3:
                    target_sizes[model_name] = (input_shape[1], input_shape[2])
                else:
                    target_sizes[model_name] = (130, 130)
            except:
                target_sizes[model_name] = (130, 130)
            print(f"✓ {model_name} loaded! Input: {m.input_shape}, Target size: {target_sizes[model_name]}")
        except Exception as e:
            print(f"✗ Failed to load {model_name}: {e}")
    else:
        print(f"✗ File not found: {filename}")

print(f"\n✅ Total models loaded: {len(models)}/{len(MODEL_FILES)}")
print("="*70 + "\n")


def preprocess_image(img, target_size):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize(target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/models', methods=['GET'])
def get_models():
    return jsonify({
        'models': list(models.keys()),
        'count': len(models)
    })


@app.route('/predict', methods=['POST'])
def predict():
    global scans_today

    if not models:
        return jsonify({'error': 'No models loaded on server'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Get selected model from request, default to CustomCNN
        selected_model_name = request.form.get('model', 'CustomCNN')
        if selected_model_name not in models:
            selected_model_name = list(models.keys())[0]

        model = models[selected_model_name]
        target_size = target_sizes[selected_model_name]

        start_time = time.time()

        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))

        processed_image = preprocess_image(img, target_size)
        prediction = model.predict(processed_image)

        # Decode prediction
        pred_shape = prediction.shape
        if len(pred_shape) == 2 and pred_shape[1] > 1:
            # Categorical
            confidence = float(np.max(prediction[0]))
            class_idx = int(np.argmax(prediction[0]))
        else:
            # Binary sigmoid
            prob = float(prediction[0][0])
            if prob > 0.5:
                class_idx = 1   # Uninfected
                confidence = prob
            else:
                class_idx = 0   # Parasitized
                confidence = 1.0 - prob

        result_text = "UNINFECTED" if class_idx == 1 else "PARASITIZED"
        sub_text = "No malaria parasites detected" if class_idx == 1 else "Malaria parasites detected in sample"

        processing_time = round(time.time() - start_time, 2)
        if processing_time < 0.01:
            processing_time = 0.01

        scans_today += 1
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

        return jsonify({
            'success': True,
            'result': result_text,
            'sub_text': sub_text,
            'confidence': confidence,
            'confidence_percent': f"{round(confidence * 100, 2)}%",
            'processing_time': f"{processing_time}s",
            'timestamp': timestamp,
            'scans_today': scans_today,
            'model_used': selected_model_name
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def stats():
    return jsonify({
        'scans_today': scans_today
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'running',
        'models_loaded': list(models.keys()),
        'count': len(models)
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)