import io
import os, sys
import requests
import PIL
import numpy as np

import torch
import torch.nn.functional as F
import torchvision.transforms as T
import torchvision.transforms.functional as TF

from dall_e          import map_pixels, unmap_pixels, load_model
from IPython.display import display, display_markdown

target_image_size = 256

def download_image(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return PIL.Image.open(io.BytesIO(resp.content))

def preprocess(img):
    s = min(img.size)

    if s < target_image_size:
        raise ValueError(f'min dim for image {s} < {target_image_size}')

    r = target_image_size / s
    s = (round(r * img.size[1]), round(r * img.size[0]))
    # img = TF.resize(img, s, interpolation=PIL.Image.LANCZOS)
    img = TF.resize(img, s, interpolation=TF.InterpolationMode.LANCZOS)
    img = TF.center_crop(img, output_size=2 * [target_image_size])
    img = torch.unsqueeze(T.ToTensor()(img), 0)
    return map_pixels(img)

dev = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# The Dockerfile downloads these .pkl files from here:  https://cdn.openai.com/dall-e/encoder.pkl   https://cdn.openai.com/dall-e/decoder.pkl
enc = load_model("./dall-e/encoder.pkl", dev)
dec = load_model("./dall-e/decoder.pkl", dev)


from flask import Flask, request, send_file, send_from_directory, jsonify
import json 
from waitress import serve

app = Flask('app')

# Uncomment these two lines to enable CORS headers for all routes:
# from flask_cors import CORS
# CORS(app)  

def serve_pil_image(pil_img):
    img_io = io.BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/', methods=["GET"])
def home():
  return send_from_directory(".", "index.html")

@app.route('/encode-decode', methods=["POST"])
def encode_decode():
  data = request.files['file']
  x = preprocess(PIL.Image.open(data))
  z_logits = enc(x.to(dev))
  z = torch.argmax(z_logits, axis=1)
  z = F.one_hot(z, num_classes=enc.vocab_size).permute(0, 3, 1, 2).float()
  x_stats = dec(z).float()
  x_rec = unmap_pixels(torch.sigmoid(x_stats[:, :3]))
  x_rec = T.ToPILImage(mode='RGB')(x_rec[0])
  return serve_pil_image(x_rec)

@app.route('/encode', methods=["POST"])
def encode():
  data = request.files['file']
  x = preprocess(PIL.Image.open(data))
  z_logits = enc(x.to(dev))
  z = torch.argmax(z_logits, axis=1)
  return jsonify(z.cpu().numpy().tolist())

@app.route('/decode', methods=["POST"])
def decode():
  z = request.get_json(force=True)
  z = np.array(z)
  z = torch.from_numpy(z).to(dev)
  z = F.one_hot(z, num_classes=enc.vocab_size).permute(0, 3, 1, 2).float()
  x_stats = dec(z).float()
  x_rec = unmap_pixels(torch.sigmoid(x_stats[:, :3]))
  x_rec = T.ToPILImage(mode='RGB')(x_rec[0])
  return serve_pil_image(x_rec)

serve(app, host="0.0.0.0", port=8080)
