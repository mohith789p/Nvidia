# Jetson Nano Setup & Computer Vision Experiments

This repository documents the step-by-step setup, configuration, and experimentation workflow on **NVIDIA Jetson Nano**, with a focus on system access, GPU verification, and basic computer vision tasks using YOLO and OpenCV.

The notebooks are designed to be followed **in sequence**. Skipping steps will lead to confusion or broken setups.

---

## 📂 Notebook Overview

### `01-jetson-nano-setup.ipynb`
Initial setup and preparation of the Jetson Nano.

**Covers:**
- First-time boot and OS setup
- Basic system configuration
- Network readiness and environment preparation

This notebook lays the foundation for everything that follows.

---

### `02_jetson_nano_terminal_and_gpu_check.ipynb`
Terminal access and GPU capability verification.

**Covers:**
- Accessing the Jetson terminal
- System information checks
- GPU and CUDA availability verification
- Clarifying common misconceptions about GPU acceleration

This step ensures the hardware and software environment is actually usable.

---

### `03_jetson_nomachine.ipynb`
Remote desktop access using **NoMachine**.

**Covers:**
- Installing and configuring NoMachine
- Accessing the Jetson GUI remotely
- When and why GUI access is required instead of SSH

Useful when headless access is not sufficient.

---

### `04_object_detection_using_yolo.ipynb`
Object detection experiments using **Ultralytics YOLO**.

**Covers:**
- Installing YOLO and dependencies
- Running object detection on images, videos, and webcam input
- Headless execution via SSH
- Understanding outputs (annotated videos, bounding box labels)

This notebook focuses on experimentation, not production deployment.

---

### `05_opencv_installation.ipynb`
Installing and validating **OpenCV** on Jetson Nano.

**Covers:**
- OpenCV installation steps
- Verifying a correct installation
- Basic image and camera access checks

OpenCV installation on ARM systems requires careful handling, which this notebook addresses.

---

### `06_accessing_jupyter_using_docker.ipynb`
Running Jupyter Notebook using **Docker**.

**Covers:**
- Motivation for using Docker
- Running Jupyter inside a container
- Port exposure and access configuration
- Avoiding dependency conflicts on the host system

This notebook emphasizes isolation and reproducibility.

---

## ⚠️ Important Notes

- These notebooks form a workflow, not standalone tutorials.
- Some notebooks were initially prototyped using **Google Colab** and adapted for Jetson Nano.
- GPU acceleration depends on correct drivers, CUDA installation, and model selection.
- Headless execution is treated as a primary use case.

---

## 🎯 Intended Audience

- Students exploring NVIDIA Jetson Nano
- Developers learning edge-based computer vision
- Anyone seeking a practical, no-hype understanding of Jetson capabilities
