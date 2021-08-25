FROM ufoym/deepo
WORKDIR /app
RUN pip3 install flask==2.0.1 flask_cors==3.0.10 dall-e==0.1 waitress==2.0.0
