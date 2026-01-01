@echo off
REM 🎯 Automated Comparison Runner for Windows
REM Run this batch file to execute the full comparison workflow

setlocal enabledelayedexpansion

echo.
echo ════════════════════════════════════════════════════════════════
echo 🎯 Edge AI: Classical GPU vs Jetson Nano Comparison
echo ════════════════════════════════════════════════════════════════
echo.

REM Create results directory
if not exist "results" mkdir results

REM Check if venv exists
if not exist "venv_windows" (
    echo.
    echo ⚠️  Virtual environment not found. Creating...
    python -m venv venv_windows
)

REM Activate virtual environment
echo 📍 Activating virtual environment...
call venv_windows\Scripts\activate.bat

REM Check if PyTorch is installed
python -c "import torch" >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📥 Installing PyTorch with CUDA support...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
)

REM Check if YOLO model exists
if not exist "yolov8n.pt" (
    echo.
    echo 📥 Downloading YOLOv8 Nano model...
    python << 'EOF'
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
print("✅ Model downloaded: yolov8n.pt")
EOF
)

REM Create test video if needed
if not exist "test_video.mp4" (
    echo.
    echo 🎬 Creating test video...
    python << 'EOF'
import cv2
import numpy as np

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_video.mp4', fourcc, 30.0, (640, 480))

for frame_num in range(300):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    x = (frame_num * 5) %% 640
    cv2.circle(frame, (x, 240), 30, (0, 255, 0), -1)
    cv2.putText(frame, f'Frame {frame_num}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    out.write(frame)

out.release()
print("✅ Test video created: test_video.mp4")
EOF
)

echo.
echo.
echo ════════════════════════════════════════════════════════════════
echo ⭐ PHASE 1: CPU Baseline
echo ════════════════════════════════════════════════════════════════
echo.
python windows_pc_phase1.py --video test_video.mp4 --duration 30 --model yolov8n.pt

echo.
echo.
echo ════════════════════════════════════════════════════════════════
echo ⭐ PHASE 3: GPU Accelerated (with PCIe overhead)
echo ════════════════════════════════════════════════════════════════
echo.
python windows_pc_phase3_gpu.py --video test_video.mp4 --duration 30 --model yolov8n.pt

echo.
echo.
echo ════════════════════════════════════════════════════════════════
echo ✅ WINDOWS PC BENCHMARKS COMPLETE!
echo ════════════════════════════════════════════════════════════════
echo.

echo 📊 Results saved to:
dir /B results\

echo.
echo 💡 Next Steps:
echo    1. SSH to Jetson Nano and run: python3 run_comparison.sh
echo    2. Once Jetson benchmarks complete, run visual_dashboard.py:
echo.
echo    python visual_dashboard.py ^
echo        --windows results/windows_phase3.json ^
echo        --jetson results/jetson_phase3.json ^
echo        --output comparison_report.html
echo.
echo    3. Open comparison_report.html in your browser
echo.
echo ════════════════════════════════════════════════════════════════

pause