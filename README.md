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

# After a little while it will say "Serving on http://0.0.0.0:8080", at which point the API is ready.
```

# Testing the API from your browser:
Open up `http://0.0.0.0:8080` in your browser to try it out. You'll see a simple interface where you can test the API by uploading an image that gets repeatedly "perturbed" in between encoding and decoding:

![perturbing penguin by repeatedly encoding, changing values, and decoding](https://github.com/josephrocca/dall-e-encoder-decoder-server/raw/main/penguin_perturb.gif)

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

I wanted to get a rough idea of how it compares to common image formats in terms of visual quality at a constant file size. All 3 were compressed to ~1.9kb (at 70% quality for JPEG and WEBP).

![comparison between DALL-E encoder/decoder and JPEG and WEBP compression](https://github.com/josephrocca/dall-e-encoder-decoder-server/raw/main/compression-comparison.jpg)
