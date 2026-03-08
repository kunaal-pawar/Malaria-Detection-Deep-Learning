# MalariaScope

An AI-powered Malaria Detection Web Application using Flask and TensorFlow.

## Project Structure

- `app.py`: Main Flask application that serves the UI and handles the `/predict` API endpoint.
- `malaria_final_model.h5`: The pre-trained Deep Learning model for malaria detection.
- `requirements.txt`: List of Python dependencies.
- `templates/index.html`: The main user interface.
- `static/css/style.css`: Stylesheet replicating the dark, modern UI.
- `static/js/script.js`: Frontend logic for file drag & drop, previews, and API integration.

## How to Run Locally

1. **Activate the Virtual Environment**
   It's recommended to activate the existing virtual environment before running the app.
   - On Windows (PowerShell/Command Prompt):
     ```bash
     .\.venv\Scripts\activate
     ```

2. **Install Dependencies**
   Ensure you have the required packages installed:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask Server**
   ```bash
   python app.py
   ```

4. **Access the Web App**
   Open your browser and navigate to:
   http://127.0.0.1:5000

## Notes
- The application automatically infers the input shape required by your `.h5` model. If the model accepts `(130, 130, 3)`, it processes the uploaded image accordingly.
- The UI handles the binary classification model. It maps the output probabilities to either `UNINFECTED` or `PARASITIZED`.
