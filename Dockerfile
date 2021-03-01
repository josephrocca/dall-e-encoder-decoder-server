FROM ufoym/deepo
WORKDIR /app
RUN pip3 install flask flask_cors dall-e waitress

