Ultralytics YOLO on Jetson Nano (JetPack 4.6.x) – Docker Guide

This guide shows how to run modern Ultralytics YOLO (YOLOv8, YOLO11, etc.) on the classic Jetson Nano Developer Kit (4GB) with JetPack 4.6.1 using Docker.

Why Docker?  
JetPack 4.6.1 has Python 3.6 by default, but recent Ultralytics needs Python ≥ 3.8.  
Docker gives an isolated, pre-configured environment with:
- Compatible Python
- Latest Ultralytics
- TensorRT & GPU support
- No host library conflicts

Latest confirmed tag (as of Feb 2026): ultralytics/ultralytics:latest-jetson-jetpack4  
This tag is specifically for JetPack 4.x (including Nano) and works great for your setup.

Prerequisites
- Jetson Nano running official JetPack 4.6.1 SD card image
- Stable 5V 4A power supply (barrel jack recommended to avoid brownouts)
- Internet connection
- Camera (USB webcam or CSI IMX219) for testing
- At least 8–10 GB free space on microSD card

Enable maximum performance mode before running containers (run these on host):
sudo nvpmodel -m 0
sudo jetson_clocks

1. Install Docker on Jetson Nano
```bash
sudo apt update
sudo apt install docker.io -y

# Allow running docker without sudo (recommended)
sudo usermod -aG docker $USER

# Log out and log back in (or reboot) for group change to apply
# Type 'exit' then reconnect via SSH, or reboot:
# sudo reboot
```
Verify:
```bash
docker --version
docker info | grep -i runtime
```

You should see nvidia in the runtimes list (JetPack includes NVIDIA Container Runtime).

2. Pull the Ultralytics JetPack 4 Docker Image
```bash
# Short variable (optional but handy)
IMAGE=ultralytics/ultralytics:latest-jetson-jetpack4

# Pull the image (~2–3 GB download, arm64)
docker pull $IMAGE

If you want a pinned version (e.g., older stable), check tags on Docker Hub:  
https://hub.docker.com/r/ultralytics/ultralytics/tags?name=jetson-jetpack4

3. Run the Container – Quick Test
Basic interactive shell with GPU:
docker run -it --ipc=host --runtime=nvidia $IMAGE

Or modern syntax:
docker run -it --ipc=host --gpus all $IMAGE
```
Inside the container, quick test:
```bash
from ultralytics import YOLO
print("Ultralytics YOLO imported successfully!")
exit()  # to leave container
```
4. Practical Usage Examples \
4.1 Inference on a local image (one-shot)
```bash
docker run --ipc=host --runtime=nvidia \
  -v $(pwd)/images:/workspace/images \
  $IMAGE \
  yolo predict model=yolo11n.pt source=/workspace/images/test.jpg
```
Results save to ./runs/detect/ on host.

4.2 Real-time webcam / CSI camera detection
```bash
docker run -it --ipc=host --runtime=nvidia \
  --device /dev/video0:/dev/video0 \
  $IMAGE \
  yolo predict model=yolo11n.pt source=0 show=True
```
- Check camera device first on host: ls /dev/video* (usually /dev/video0)
- If permission denied: sudo chmod 666 /dev/video* on host

4.3 Persistent workspace (best for projects)
Mount your folder so code/models/results persist:
```bash
docker run -it --ipc=host --runtime=nvidia \
  -v /home/$USER/yolo-projects:/workspace \
  --device /dev/video0:/dev/video0 \
  $IMAGE bash
```
Inside → cd /workspace → edit/run scripts (files sync to host).

4.4 Export to TensorRT engine (recommended for 2–3× faster FPS)
Inside container:
```bash
yolo export model=yolo11n.pt format=engine device=0
```
Use the .engine file for inference (much better on Nano's limited GPU).

5. Troubleshooting
- GPU not working → Inside container: python -c "import torch; print(torch.cuda.is_available())" → should print True
- Out of memory → Nano has 4GB → Use nano/small models (yolo11n.pt), add swap if needed:
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
- Camera fails → Verify on host with v4l2-ctl --list-devices or cheese app
- Slow pull → Retry or check network
- More help → Ultralytics Jetson Guide: https://docs.ultralytics.com/guides/nvidia-jetson/

6. Simple Python Example (save as detect_live.py in workspace)
from ultralytics import YOLO

model = YOLO("yolo11n.pt")  # or yolov8n.pt / your .engine file
results = model(source=0, show=True, stream=True)  # 0 = default camera

for result in results:
    print(result.boxes)  # process detections here

Run inside container: python detect_live.py

Good luck with your Jetson Nano + YOLO projects! 🚀  
Updated for Feb 2026 – uses official latest-jetson-jetpack4 tag.