from flask import Flask, request, jsonify
import numpy as np
import joblib

app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
from flask_cors import CORS
CORS(app)

# Load the reduced model
try:
    xgb_model_reduced = joblib.load('xgb_model_reduced.pkl')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")

# Define encoding for categorical features
wind_gust_dir_mapping = {
    "N": 0, "NNE": 1, "NE": 2, "ENE": 3, "E": 4, "ESE": 5, "SE": 6, "SSE": 7,
    "S": 8, "SSW": 9, "SW": 10, "WSW": 11, "W": 12, "WNW": 13, "NW": 14, "NNW": 15
}

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse JSON data from the request
        data = request.json
        print("Received Data:", data)

        # Validate input: Check if all expected features are present
        missing_features = [feat for feat in [
            "Temp3pm", "Evaporation", "MaxTemp", "WindGustDir",
            "WindSpeed9am", "Rainfall", "Pressure9am", "Humidity9am",
            "WindDir3pm", "Pressure3pm"
        ] if feat not in data]
        if missing_features:
            return jsonify({"error": f"Missing features in input: {', '.join(missing_features)}"}), 400

        # Encode categorical features
        if data["WindGustDir"] not in wind_gust_dir_mapping or data["WindDir3pm"] not in wind_gust_dir_mapping:
            return jsonify({"error": "Invalid value for WindGustDir or WindDir3pm"}), 400
        gust_dir_encoded = wind_gust_dir_mapping[data["WindGustDir"]]
        dir3pm_encoded = wind_gust_dir_mapping[data["WindDir3pm"]]

        # Collect feature values in the correct order
        features = np.array([
            float(data["Temp3pm"]),
            float(data["Evaporation"]),
            float(data["MaxTemp"]),
            gust_dir_encoded,
            float(data["WindSpeed9am"]),
            float(data["Rainfall"]),
            float(data["Pressure9am"]),
            float(data["Humidity9am"]),
            dir3pm_encoded,
            float(data["Pressure3pm"])
        ]).reshape(1, -1)
        print("Processed Features:", features)  # Debugging: Print processed features

        # Make prediction using the reduced model
        prediction = xgb_model_reduced.predict(features)
        return jsonify({"prediction": int(prediction[0])})
    except Exception as e:
        print(f"Error during prediction: {e}")  # Debugging: Log the error
        return jsonify({"error": "An error occurred during prediction. Please check your input and try again."}), 500

if __name__ == '__main__':
    app.run(debug=True)