#!/bin/bash

# 🎯 Automated Comparison Runner for Jetson Nano
# Run this script to execute the full comparison workflow
# Usage: bash run_comparison.sh

set -e  # Exit on error

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🎯 Edge AI: Classical GPU vs Jetson Nano Comparison"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Create results directory
mkdir -p results

# Check if virtual environment exists
if [ ! -d "venv_jetson" ]; then
    echo ""
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv_jetson
fi

# Activate virtual environment
echo "📍 Activating virtual environment..."
source venv_jetson/bin/activate

# Install/upgrade pip
echo ""
echo "📥 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install PyTorch for Jetson (ARM64)
echo ""
python3 -c "import torch" 2>/dev/null || {
    echo "📥 Installing PyTorch for Jetson (ARM)..."
    # Official NVIDIA PyTorch wheel for Jetson
    pip install torch torchvision torchaudio
}

# Install other dependencies
echo ""
echo "📥 Installing required packages..."
pip install -q ultralytics opencv-python numpy

# Check if YOLO model exists
if [ ! -f "yolov8n.pt" ]; then
    echo ""
    echo "📥 Downloading YOLOv8 Nano model..."
    python3 << 'EOF'
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
print("✅ Model downloaded: yolov8n.pt")
EOF
fi

# Create test video if needed
if [ ! -f "test_video.mp4" ]; then
    echo ""
    echo "🎬 Creating test video..."
    python3 << 'EOF'
import cv2
import numpy as np

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_video.mp4', fourcc, 30.0, (640, 480))

for frame_num in range(300):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    x = (frame_num * 5) % 640
    cv2.circle(frame, (x, 240), 30, (0, 255, 0), -1)
    cv2.putText(frame, f'Frame {frame_num}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    out.write(frame)

out.release()
print("✅ Test video created: test_video.mp4")
EOF
fi

echo ""
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "⭐ PHASE 1: CPU Baseline (ARM Processor)"
echo "════════════════════════════════════════════════════════════════"
echo ""
python3 jetson_nano_phase1.py --video test_video.mp4 --duration 30 --model yolov8n.pt

echo ""
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "⭐ PHASE 3: GPU Accelerated (with UMA - Zero-Copy)"
echo "════════════════════════════════════════════════════════════════"
echo ""
python3 jetson_nano_phase3_uma.py --video test_video.mp4 --duration 30 --model yolov8n.pt

echo ""
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ JETSON NANO BENCHMARKS COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "📊 Results saved to:"
ls -lh results/

echo ""
echo "💡 Next Steps:"
echo "   1. Transfer Windows results to this machine (scp or SCP)"
echo "   2. Run visual_dashboard.py on either machine:"
echo ""
echo "   python3 visual_dashboard.py \\"
echo "       --windows /path/to/windows_phase3.json \\"
echo "       --jetson results/jetson_phase3.json \\"
echo "       --output comparison_report.html"
echo ""
echo "   3. Open comparison_report.html in your browser"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Deactivate virtual environment
deactivate

echo "✅ Script completed successfully!"
