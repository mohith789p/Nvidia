# 📚 Complete Setup and Run Guide

## Classical GPU vs Jetson Nano: Edge AI Comparison Framework

This guide provides step-by-step instructions to set up and run the complete comparison on both Windows PC and Jetson Nano.

---

## 🎯 Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Windows PC Setup](#windows-pc-setup)
4. [Jetson Nano Setup](#jetson-nano-setup)
5. [Running Benchmarks](#running-benchmarks)
6. [Generating Comparison](#generating-comparison)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This project compares:
- **Windows PC**: Classical discrete GPU with PCIe data transfers
- **Jetson Nano**: Integrated GPU with Unified Memory Architecture (UMA)

You can run both simultaneously and compare results side-by-side!

### What You'll Learn
- How PCIe bottlenecks affect GPU performance
- Why Unified Memory Architecture matters for edge AI
- When to use discrete vs integrated GPUs
- How to measure and compare architectures quantitatively

---

## System Requirements

### Windows PC

**Hardware:**
- ✅ NVIDIA RTX GPU (2070 or better recommended)
- ✅ 8GB+ RAM
- ✅ 50GB free disk space (for PyTorch)

**Software:**
- ✅ Windows 10/11
- ✅ Python 3.9+
- ✅ NVIDIA CUDA 11.8+ (installed and working)
- ✅ NVIDIA cuDNN 8.6+

**Check CUDA:**
```bash
# Open Command Prompt
nvidia-smi

# Should show your GPU
# Example:
# | NVIDIA-SMI 546.17    Driver Version: 546.17    CUDA Version: 12.2   |
# | NVIDIA RTX 2070 with Max-Q Design  |
```

### Jetson Nano

**Hardware:**
- ✅ Jetson Nano Developer Kit
- ✅ 5V/4A power supply (recommended)
- ✅ microSD card 64GB+ (UHS-1 recommended)
- ✅ Ethernet connection (or WiFi module)

**Software:**
- ✅ JetPack 4.6+ (includes CUDA, cuDNN, TensorRT)
- ✅ Python 3.8+ (pre-installed)
- ✅ Internet connection

**Check CUDA on Jetson:**
```bash
# SSH to Jetson Nano
ssh jetson@<jetson_ip>

# Check CUDA
nvcc --version

# Should show CUDA version (e.g., 10.2)
```

---

## Windows PC Setup

### Step 1: Prepare Project Directory

```bash
# Open Command Prompt (Win+R, type cmd)

# Create project directory
mkdir C:\edge-ai-comparison
cd C:\edge-ai-comparison

# Create subdirectories
mkdir results
```

### Step 2: Copy Project Files

Download all Python scripts to `C:\edge-ai-comparison\`:
- `windows_pc_phase1.py`
- `windows_pc_phase3_gpu.py`
- `run_comparison.bat`
- `visual_dashboard.py`

### Step 3: Run Automated Setup

```bash
# Navigate to project directory
cd C:\edge-ai-comparison

# Make the batch file executable (usually automatic on Windows)
# Double-click run_comparison.bat OR run from Command Prompt:

run_comparison.bat
```

**This will automatically:**
1. Create virtual environment (`venv_windows`)
2. Install PyTorch with CUDA support
3. Download YOLOv8 Nano model (~7MB)
4. Create test video (~10MB)
5. Run Phase 1 (CPU baseline) - ~30 seconds
6. Run Phase 3 (GPU accelerated) - ~30 seconds

### Step 4: Wait for Results

Expected output:
```
════════════════════════════════════════════════════════════════
⭐ PHASE 1: CPU Baseline
════════════════════════════════════════════════════════════════

Frame    FPS          Latency (ms)
───────────────────────────────────────────
30       3.00         333.33
60       3.00         333.33
...

════════════════════════════════════════════════════════════════
⭐ PHASE 3: GPU Accelerated (with PCIe overhead)
════════════════════════════════════════════════════════════════

Frame    FPS          Latency (ms)
───────────────────────────────────────────
30       28.50        35.09
60       28.25        35.40
...
```

### Step 5: Check Results

Results are saved in `results/` directory:
- `results/windows_phase1.json` - CPU baseline metrics
- `results/windows_phase3.json` - GPU with PCIe overhead metrics

```bash
# List results
dir results\

# Should show:
# windows_phase1.json
# windows_phase3.json
```

---

## Jetson Nano Setup

### Step 1: Flash JetPack (if needed)

If Jetson Nano is new, flash JetPack 4.6+:

**From your development PC:**
1. Download NVIDIA SDK Manager
2. Follow official Jetson Nano setup guide
3. Ensure JetPack 4.6+ is installed

**Check JetPack version on Jetson:**
```bash
ssh jetson@<jetson_ip>
cat /etc/nv_tegra_release
# Should show JetPack 4.6 or later
```

### Step 2: Prepare Project Directory

```bash
# SSH to Jetson Nano
ssh jetson@<jetson_ip>

# Create project directory
mkdir ~/edge-ai-comparison
cd ~/edge-ai-comparison

# Create subdirectories
mkdir results
```

### Step 3: Copy Project Files

Transfer files from your development PC to Jetson:

```bash
# From Windows Command Prompt
scp jetson_nano_phase1.py jetson@<jetson_ip>:~/edge-ai-comparison/
scp jetson_nano_phase3_uma.py jetson@<jetson_ip>:~/edge-ai-comparison/
scp run_comparison.sh jetson@<jetson_ip>:~/edge-ai-comparison/
scp visual_dashboard.py jetson@<jetson_ip>:~/edge-ai-comparison/
```

Or manually:
1. Download all files
2. Use WinSCP or FileZilla to transfer
3. Place in `~/edge-ai-comparison/`

### Step 4: Make Shell Script Executable

```bash
# SSH to Jetson Nano
ssh jetson@<jetson_ip>
cd ~/edge-ai-comparison

# Make script executable
chmod +x run_comparison.sh
```

### Step 5: Run Automated Setup

```bash
# SSH to Jetson Nano
ssh jetson@<jetson_ip>
cd ~/edge-ai-comparison

# Run the comparison script
bash run_comparison.sh
```

**This will automatically:**
1. Create virtual environment (`venv_jetson`)
2. Install PyTorch for Jetson ARM
3. Download YOLOv8 Nano model
4. Create test video
5. Run Phase 1 (CPU baseline) - ~30 seconds
6. Run Phase 3 (GPU with UMA) - ~30 seconds

### Step 6: Wait for Results

Expected output:
```
🚀 JETSON NANO - PHASE 1: CPU BASELINE
═════════════════════════════════════════

Frame    FPS          Latency (ms)     Temp (°C)
──────────────────────────────────────────────
10       0.33         3000.00          45.2
20       0.34         2970.15          46.1
...

🚀 JETSON NANO - PHASE 3: GPU-ACCELERATED (UMA)
════════════════════════════════════════════════

Frame    FPS          Latency (ms)     GPU Load (%)
───────────────────────────────────────────────────
10       0.55         1818.18          85.2
20       0.56         1785.71          86.5
...
```

### Step 7: Check Results

```bash
# On Jetson Nano
ls -lh results/

# Should show:
# jetson_phase1.json
# jetson_phase3.json
```

---

## Running Benchmarks

### Windows PC Only

```bash
# Navigate to project directory
cd C:\edge-ai-comparison

# Method 1: Double-click
run_comparison.bat

# Method 2: Command line
cmd /c run_comparison.bat
```

### Jetson Nano Only

```bash
# SSH to Jetson
ssh jetson@<jetson_ip>
cd ~/edge-ai-comparison

# Run the script
bash run_comparison.sh
```

### Both Simultaneously (Recommended!)

**This is where the magic happens - see real architectural differences:**

```bash
# Terminal 1 (Windows PC)
C:\edge-ai-comparison> run_comparison.bat

# Terminal 2 (Jetson Nano) - at same time
jetson@nano:~/edge-ai-comparison$ bash run_comparison.sh
```

**Why simultaneously?**
- See both systems working at the same time
- Compare real-time performance differences
- Understand practical deployment scenarios
- More educational and impressive!

---

## Generating Comparison

### After Both Benchmarks Complete

**Option 1: On Windows PC**

```bash
# Copy Jetson results to Windows
scp jetson@<jetson_ip>:~/edge-ai-comparison/results/jetson_phase3.json .\results\

# Generate comparison
python visual_dashboard.py ^
    --windows results/windows_phase3.json ^
    --jetson results/jetson_phase3.json ^
    --output comparison_report.html

# View report
start comparison_report.html
```

**Option 2: On Jetson Nano**

```bash
# Copy Windows results to Jetson
scp results/windows_phase3.json jetson@<jetson_ip>:~/edge-ai-comparison/results/

# SSH to Jetson
ssh jetson@<jetson_ip>
cd ~/edge-ai-comparison

# Generate comparison
python3 visual_dashboard.py \
    --windows results/windows_phase3.json \
    --jetson results/jetson_phase3.json \
    --output comparison_report.html

# Transfer report back to Windows
scp comparison_report.html <windows_user>@<windows_ip>:C:\edge-ai-comparison\
```

### View the Report

Open `comparison_report.html` in your browser:
- Beautiful interactive visualizations
- Side-by-side metrics
- Key insights explained
- Architecture diagrams
- Detailed comparison table

---

## Troubleshooting

### Windows PC Issues

#### ❌ "CUDA not available"
**Solution:**
```bash
# Check GPU
nvidia-smi

# If not found, install NVIDIA drivers
# Download from: https://www.nvidia.com/Download/driverDetails.aspx

# Verify CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

#### ❌ "ModuleNotFoundError: No module named 'ultralytics'"
**Solution:**
```bash
# Activate venv
venv_windows\Scripts\activate.bat

# Install missing package
pip install ultralytics
```

#### ❌ "Video file not found"
**Solution:**
```bash
# Script should auto-create test video
# If not, create manually:
python -c "
import cv2
import numpy as np

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_video.mp4', fourcc, 30.0, (640, 480))

for frame_num in range(300):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    x = (frame_num * 5) % 640
    cv2.circle(frame, (x, 240), 30, (0, 255, 0), -1)
    out.write(frame)

out.release()
print('✅ Test video created')
"
```

#### ❌ Low FPS on GPU (< 10 FPS)
**Possible causes:**
- Other GPU processes running
- Power saving mode enabled
- GPU drivers outdated

**Solutions:**
```bash
# Check GPU load
# Open Task Manager → GPU tab

# Close other GPU applications (Chrome, Discord, etc.)

# Update drivers
# https://www.nvidia.com/Download/driverDetails.aspx
```

---

### Jetson Nano Issues

#### ❌ "bash: run_comparison.sh: Permission denied"
**Solution:**
```bash
# Make executable
chmod +x run_comparison.sh

# Run again
bash run_comparison.sh
```

#### ❌ "torch: No module named 'torch'"
**Solution:**
```bash
# Activate venv
source venv_jetson/bin/activate

# Install PyTorch for Jetson
pip install torch torchvision torchaudio
```

#### ❌ "CUDA out of memory"
**Solution:**
```bash
# Jetson Nano has only 4GB shared memory
# Close other applications
ps aux | grep python
kill <pid>

# Run script again
bash run_comparison.sh
```

#### ❌ Thermal throttling (too hot)
**Check temperature:**
```bash
cat /sys/devices/virtual/thermal/thermal_zone0/temp
# Divide by 1000 for °C
```

**Solution:**
- Ensure good ventilation
- Use heatsink on SoM
- Add cooling fan
- Run during cooler time of day

#### ❌ "tegrastats not found"
**Solution:**
```bash
# tegrastats is usually in PATH
# If not, script uses fallback power estimation

# Check location
which tegrastats
# Usually: /usr/bin/tegrastats
```

---

### Network Issues (File Transfer)

#### ❌ "Cannot connect to Jetson IP"
**Solution:**
```bash
# Find Jetson IP
# From Jetson terminal:
hostname -I

# From Windows, test connection
ping <jetson_ip>

# If no ping, check network
# Ensure both connected to same network
```

#### ❌ "scp: command not found" (Windows)
**Solution:**
```bash
# Option 1: Use WinSCP (GUI tool)
# Download: https://winscp.net/

# Option 2: Use Powershell (Windows 10+)
scp -r jetson@<jetson_ip>:~/edge-ai-comparison/results/jetson_phase3.json .

# Option 3: Manual copy via USB drive
```

---

## Performance Tuning

### Windows PC

**Maximize GPU performance:**
```bash
# Close background applications
# Open Task Manager → Performance → GPU
# Close Chrome, Discord, etc.

# Disable GPU power saving
# NVIDIA Control Panel → Power Management Mode → Prefer maximum performance
```

**Expected Performance:**
- Phase 1 (CPU): 3-5 FPS
- Phase 3 (GPU): 25-30 FPS

### Jetson Nano

**Maximize performance:**
```bash
# Set max power mode
sudo nvpmodel -m 0

# Set max clock speeds
sudo jetson_clocks
```

**Expected Performance:**
- Phase 1 (CPU): 0.5-2 FPS
- Phase 3 (GPU+UMA): 8-15 FPS

---

## Next Steps

### After Successful Run

1. **Analyze Results**
   - Open `comparison_report.html` in browser
   - Review metrics and charts
   - Read key insights

2. **Share Findings**
   - Create GitHub repo
   - Write blog post
   - Present to team/class

3. **Extend Project**
   - Add more models (YOLOv8s, YOLOv8m)
   - Test with different video resolutions
   - Add multi-stream processing
   - Measure power consumption more accurately

4. **Use for Decisions**
   - Which platform for your use case?
   - What's the cost/performance trade-off?
   - When does edge AI make sense?

---

## Questions & Support

### Common Questions

**Q: Why is Jetson slower than Windows?**
A: Jetson has 128 CUDA cores vs RTX 2070's 2304. But UMA (zero-copy) makes it competitive for edge deployment.

**Q: Can I use a different video?**
A: Yes! Replace `test_video.mp4` with your own:
```bash
python windows_pc_phase3_gpu.py --video your_video.mp4 --duration 60
```

**Q: Can I use different models?**
A: Yes! YOLOv8n is the default, but try:
```bash
python windows_pc_phase3_gpu.py --model yolov8s.pt --video test_video.mp4
```

**Q: How do I interpret the results?**
A: See `ARCHITECTURAL_DIFFERENCES.md` for detailed explanation of metrics.

### Resources

- **NVIDIA Jetson:** https://developer.nvidia.com/embedded/jetson
- **CUDA Documentation:** https://docs.nvidia.com/cuda/
- **YOLOv8:** https://docs.ultralytics.com/
- **PyTorch:** https://pytorch.org/docs/

---

## Success Checklist

- [ ] Windows PC: Python 3.9+ installed
- [ ] Windows PC: NVIDIA GPU + CUDA drivers working
- [ ] Jetson Nano: JetPack 4.6+ installed
- [ ] Jetson Nano: SSH access working
- [ ] Windows PC: Project files downloaded
- [ ] Jetson Nano: Project files transferred
- [ ] Windows PC: `run_comparison.bat` completed successfully
- [ ] Jetson Nano: `bash run_comparison.sh` completed successfully
- [ ] Both: JSON results generated in `results/` directory
- [ ] Comparison: HTML report generated
- [ ] Report: Opened in browser and reviewed

✅ **If all checked: Project successful!**

---

## Conclusion

You now have a complete framework for comparing GPU architectures. This project demonstrates deep understanding of:
- GPU architecture fundamentals
- PCIe bottlenecks in practice
- Unified Memory Architecture benefits
- Edge AI deployment trade-offs
- Quantitative performance measurement

**Use this knowledge to make informed decisions about edge AI deployment!** 🚀

---

Generated: January 2026
Version: 1.0
