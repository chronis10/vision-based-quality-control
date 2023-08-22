FROM python:3.8

# Install Python dependencies
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the script to the image
COPY sync_frames.py /app/sync_frames.py

CMD ["python", "/app/sync_frames.py"]