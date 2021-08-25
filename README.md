Based on this: https://github.com/openai/DALL-E/blob/master/notebooks/usage.ipynb

# Setup:
```bash
# Build the docker image:
git clone https://github.com/josephrocca/dall-e-encoder-decoder-server
cd dall-e-encoder-decoder-server
docker build -t dall-e-encoder-decoder-server .

# Download the encoder-decoder model files:
mkdir dall-e
wget --directory-prefix=./dall-e https://cdn.openai.com/dall-e/encoder.pkl
wget --directory-prefix=./dall-e https://cdn.openai.com/dall-e/decoder.pkl

# Run the image:
# Omit `--gpus all` in the following command if you haven't installed nvidia's docker tooling (falls back to CPU)
docker run --gpus all -v $PWD:/app -w /app -p 8080:8080 -it dall-e-encoder-decoder-server python3 main.py

# After a little while it will say "Server started.", at which point the API is ready. Visit http://0.0.0.0:8080
# in your browser to test. If you'd like to change the port to 3000 (for example), then in the above `docker run ...`
# command you'd change `-p 8080:8080` to `-p 3000:8080`.
```

# Testing the API from your browser:
Open up `http://0.0.0.0:8080` in your browser to try it out. You'll see a simple interface where you can test the API by uploading an image that gets repeatedly "perturbed" in between encoding and decoding:

![perturbing penguin by repeatedly encoding, changing values, and decoding](https://user-images.githubusercontent.com/1167575/130863482-b8d08e3b-1c4b-4623-8064-e2c6b008e024.gif)


See `index.html` for the code. You can send POST requests (with **jpg** images) at `/encode/<size>` and `/decode` as shown in the example code below.

```html
<input type="file" id="fileEl">
<img id="imgEl">
```

```js
// After selecting a file with the file-picker:
let formData = new FormData();
formData.append("file", fileEl.files[0]);

// Encode:
let encoded = await fetch("http://0.0.0.0:8080/encode/256", {
  method: 'POST',
  body: formData,
}).then(r => r.json());

// The `encoded` variable now references a single-element array that
// contains a 32x32 2D array of integers where each integer is between
// 0 and 8191, inclusive. The size of the array depends on what you
// choose for `/encode/<size>`.

// Decode:
let decoded = await fetch("http://0.0.0.0:8080/decode", {
  method: 'POST',
  body: JSON.stringify(encoded),
}).then(r => r.blob());

imgEl.src = URL.createObjectURL(decoded);
```

There's also an encode-decode path for testing:
```js
let result = await fetch("http://0.0.0.0:8080/encode-decode/256", {
  method: 'POST',
  body: formData,
}).then(r => r.blob());
imgEl.src = URL.createObjectURL(result);
```

# Encoding Benchmarks

For a particular image I tested (speed will vary based on input image dimensions):

### CPU:
* 3.56 images per second at size 64
* 1.95 images per second at size 128
* 0.70 images per second at size 256
* 0.19 images per second at size 512

### GPU:
* 12.85 images per second at size 64  **(3.6x faster)**
* 11.69 images per second at size 128 **(6x faster)**
* 9.80 images per second at size 256  **(14x faster)**
* 5.49 images per second at size 512  **(28.8x faster)**

# Comparison to JPEG & WEBP

I wanted to get a rough idea of how it compares to common image formats in terms of visual quality at a constant file size. All 3 were compressed to ~1.9kb (by lowering the image size at 70% quality for JPEG and WEBP).

![comparison between DALL-E encoder/decoder and JPEG and WEBP compression](https://user-images.githubusercontent.com/1167575/130863554-d3d45aba-bc6b-4c08-9399-63824c6d8e2e.jpg)

# Comparison to VQGAN

These images are from [this notebook](https://colab.research.google.com/github/CompVis/taming-transformers/blob/master/scripts/reconstruction_usage.ipynb). VQGAN's reconstructions are impressive!

![download](https://user-images.githubusercontent.com/1167575/129307207-7e78c757-e2a2-4d3d-ae07-5ffc086ece0e.png)
![download (1)](https://user-images.githubusercontent.com/1167575/129307212-6f25643a-71c1-4d94-bf6a-b0d038b083d6.png)
![download (2)](https://user-images.githubusercontent.com/1167575/129307216-647ec483-bde3-4ef3-9f6c-d316acc7733a.png)
![download (3)](https://user-images.githubusercontent.com/1167575/129307220-c4c6daa4-f31c-4a85-a50a-4e84c654ce14.png)
![download (4)](https://user-images.githubusercontent.com/1167575/129307222-53ca4220-bb4c-46f1-bc41-a126d89ea973.png)
![download (5)](https://user-images.githubusercontent.com/1167575/129307223-f2ac3ca6-64dc-4a28-99c1-3fc1109dd9fa.png)

