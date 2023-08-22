FROM python:3.9-slim

WORKDIR /app


# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Kafka producer script
COPY rtsp_to_kafka.py .

CMD ["python", "rtsp_to_kafka.py"]