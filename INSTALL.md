# Development

## Conda environment
```
conda create -n qcv-system python=3.11
conda activate qcv-system
```
## Pytorch
```
conda install pytorch torchvision pytorch-cuda=11.7 -c pytorch -c nvidia
```
## Check if torch and CUDA works
```
python3
import torch
torch.cuda.is_available()
```
## Install Dependecies

```
pip install cython
pip install Pillow
pip install natsort
pip install scikit-image
pip install ipykernel notebook jupyter
pip install opencv-python
```
# Pretrained Mask-RCNN model for the task

Download it from [model link](https://drive.google.com/file/d/1YwQYNNuawxH94BsDiz0absg9goX6Tfa8/view?usp=sharing) and place it in the direcotry /estimator/models.

# Dummy Streamer

```
cd dummy_streamer
docker build -t d_streamer .
```
```
docker compose up
```

# Deployment
```
cd stream_producer
docker build -t stream_producer .
cd ..

cd timestamp_extractor
docker build -t timestamp_extractor .
cd ..

cd synchronizer
docker build -t synchronizer .
cd ..

cd estimator
docker build -t estimator .
cd ..
```

On route directory
```
docker compose up
```