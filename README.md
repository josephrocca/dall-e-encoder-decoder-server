Based on this: https://github.com/openai/DALL-E/blob/master/notebooks/usage.ipynb

# Setup:
```bash
# Build the docker image:
git clone https://github.com/josephrocca/dall-e-encoder-decoder-server
cd dall-e-encoder-decoder-server
docker build -t dall-e-encoder-decoder-server .

# Run the image:
# Omit `--gpus all` in the following command if you haven't installed nvidia's docker tooling (falls back to CPU)
docker run --gpus all -w /app -p 8080:8080 -it dall-e-encoder-decoder-server python3 main.py
```

# Testing the API from your browser:
Open up `http://0.0.0.0:8080/` in your browser to try it out. You'll see a simple interface where you can test the API by uploading an image that gets repeatedly "perturbed" in between encoding and decoding:

![perturbing penguin by repeatedly encoding, changing values, and decoding](https://github.com/josephrocca/dall-e-encoder-decoder-server/raw/main/penguin_perturb.gif)

See `index.html` for the code. You can send POST requests (with **jpg** images) at `/encode` and `/decode` as shown in the example below:

```html
<input type="file" id="fileEl">
<img id="imgEl">
```

```js
// After selecting a file with the file-picker:
let formData = new FormData();
formData.append("file", fileEl.files[0]);

// Encode:
let encoded = await fetch("http://0.0.0.0:8080/encode", {
  method: 'POST',
  body: formData,
}).then(r => r.json());

// The `encoded` variable now references a single-element array that
// contains a 32x32 2D array of integers where each integer is between
// 0 and 8191, inclusive. The size will be larger than 32x32 if
// `target_image_size` (on the server) is set to a larger value.

// Decode:
let decoded = await fetch("http://0.0.0.0:8080/decode", {
  method: 'POST',
  body: JSON.stringify(encoded),
}).then(r => r.blob());

imgEl.src = URL.createObjectURL(decoded);
```

There's also an encode-decode path for testing:
```js
let result = await fetch("http://0.0.0.0:8080/encode-decode", {
  method: 'POST',
  body: formData,
}).then(r => r.blob());
imgEl.src = URL.createObjectURL(result);
```
