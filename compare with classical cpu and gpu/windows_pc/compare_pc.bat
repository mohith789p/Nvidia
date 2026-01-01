@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Edge AI GPU Benchmark

echo ════════════════════════════════════════════════════════════════
echo 🎯 Edge AI GPU Benchmark - Windows PC
echo ════════════════════════════════════════════════════════════════
echo.
echo Files found: windows_cpu.py + windows_gpu.py + yolov8n.pt
pause

if not exist results mkdir results

REM Virtual environment
if not exist venv_windows python -m venv venv_windows
call venv_windows\Scripts\activate.bat

REM Install (single commands)
pip install --quiet torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install --quiet ultralytics opencv-python

REM CPU Phase 1
echo.
echo ═══════ PHASE 1: CPU (windows_cpu.py) ═══════
python windows_cpu.py --video test_video.mp4 --duration 20
if errorlevel 1 pause & exit /b 1

REM GPU Phase 3
echo.
echo ═══════ PHASE 3: GPU PCIe (windows_gpu.py) ═══════
python windows_gpu.py --video test_video.mp4 --duration 20
if errorlevel 1 pause & exit /b 1

echo.
echo ✅ SUCCESS! Check results/
dir results
echo.
pause
