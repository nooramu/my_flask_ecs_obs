# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.preprocessing.image import img_to_array
from obs import ObsClient
from io import BytesIO
from PIL import Image
import numpy as np
import requests
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey'

model = VGG16(weights='imagenet')

OBS_ACCESS_KEY_ID = 'D2RWFCWOQQRMMZ0JGRK1'
OBS_SECRET_ACCESS_KEY = 'B4LXgF10cWE9gNMIK93wWHRu5C161B1BAFIM2ZHc'
OBS_ENDPOINT = 'obs.cn-north-4.myhuaweicloud.com'
OBS_BUCKET_NAME = 'yunjs'

obs_client = ObsClient(
    access_key_id=OBS_ACCESS_KEY_ID,
    secret_access_key=OBS_SECRET_ACCESS_KEY,
    server=OBS_ENDPOINT
)

def preprocess_image_from_url(image_url):
    logging.info(f"Preprocessing image from URL: {image_url}")
    response = requests.get(image_url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch image from URL: {image_url} with status code {response.status_code}")
        raise Exception(f"Failed to fetch image from URL: {image_url} with status code {response.status_code}")
    try:
        image = Image.open(BytesIO(response.content))
        image = image.resize((224, 224))
        image = img_to_array(image)
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        image = preprocess_input(image)
        return image
    except Exception as e:
        logging.error(f"Error processing image from URL: {e}")
        raise


def predict_image(image):
    logging.info("Predicting image...")
    prediction = model.predict(image)
    decoded_predictions = decode_predictions(prediction, top=1)[0]
    labels = [f"{label} ({prob * 100:.2f}%)" for _, label, prob in decoded_predictions]
    return labels

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if 'file_name' not in data:
        return jsonify({'error': 'No file_name provided'}), 400
    
    file_name = data['file_name']
    obs_url = f"https://{OBS_BUCKET_NAME}.{OBS_ENDPOINT}/{file_name}"
    
    try:
        image = preprocess_image_from_url(obs_url)
        predictions = predict_image(image)
        return jsonify({'predictions': predictions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
