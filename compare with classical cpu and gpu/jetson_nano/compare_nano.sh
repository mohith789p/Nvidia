#!/bin/bash

# 🎯 Jetson Nano Benchmark: Video PRIMARY
# Priority: test_video.mp4 → /dev/video0 → CSI
# Usage: bash compare_nano.sh

set -e

clear
echo "════════════════════════════════════════════════════════════════"
echo "🎯 Jetson Nano: Video Benchmark"
echo "Priority: test_video.mp4"
echo "══════════════════════════════════════════════════════════════=="

# Colors
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

mkdir -p results

# Virtual env
[ ! -d venv_jetson ] && python3 -m venv venv_jetson
source venv_jetson/bin/activate

# Dependencies
pip install --quiet --upgrade pip ultralytics opencv-python numpy

# Model
[ ! -f yolov8n.pt ] && python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt'); echo ✅ Model"

# PRIORITY 1: Create test video (consistent benchmarking)
if [ ! -f test_video.mp4 ]; then
    echo -e "${YELLOW}🎬 Creating test_video.mp4 (priority source)...${NC}"
    python3 -c "
import cv2,numpy
fourcc=cv2.VideoWriter_fourcc(*'mp4v')
out=cv2.VideoWriter('test_video.mp4',fourcc,30,(640,480))
for i in range(300):
    f=numpy.zeros((480,640,3),numpy.uint8)
    cv2.circle(f,(int(i*2%640),240),30,(0,255,0),-1)
    out.write(f)
out.release()
print('✅ test_video.mp4 ready - PREFERRED SOURCE')
"
fi

echo -e "${GREEN}✅ test_video.mp4 ready (PRIMARY SOURCE)${NC}"
echo "📹 USB fallback ready (/dev/video0)"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "⭐ PHASE 1: CPU (nano_phase1.py)"
echo "════════════════════════════════════════════════════════════════"
python3 nano_phase1.py --duration 20 --model yolov8n.pt

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "⭐ PHASE 3: GPU UMA (nano_phase3.py)"  
echo "════════════════════════════════════════════════════════════════"
python3 nano_phase3.py --duration 20 --model yolov8n.pt

echo ""
echo "${GREEN}✅ COMPLETE! Results:${NC}"
ls -lh results/*.json

echo ""
echo "${YELLOW}💡 Priority used:${NC}"
echo "1️⃣ test_video.mp4 (always created/used)"
echo "2️⃣ USB camera /dev/video0 (fallback)"
echo "3️⃣ CSI camera (last resort)"

deactivate
