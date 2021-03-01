FROM ufoym/deepo
WORKDIR /app
RUN pip3 install flask flask_cors dall-e waitress
RUN git clone https://github.com/josephrocca/dall-e-encoder-decoder-server .
RUN mkdir dall-e
RUN wget --directory-prefix=./dall-e https://cdn.openai.com/dall-e/encoder.pkl
RUN wget --directory-prefix=./dall-e https://cdn.openai.com/dall-e/decoder.pkl
RUN python3 main.py
