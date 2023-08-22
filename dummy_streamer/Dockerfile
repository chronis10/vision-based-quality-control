FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y ffmpeg libsm6 libxext6 libxrender-dev

WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY stream_ffmpeg.py /app/
COPY images /app/images/

CMD ["python", "stream_ffmpeg.py"]