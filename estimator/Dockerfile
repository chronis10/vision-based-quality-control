# Use the official PyTorch image with CUDA from the NVIDIA container registry
FROM nvcr.io/nvidia/pytorch:22.12-py3

# Set the working directory in docker
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the content of the local directory to the working directory
COPY utils.py .
COPY estimator.py .

# Specify the command to run on container start
CMD [ "python", "./estimator.py" ]
