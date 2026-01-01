"""
JETSON NANO - PHASE 1: CPU BASELINE
Platform: Jetson Nano with ARM Processor (Quad-core A57)
Purpose: Establish CPU-only baseline on edge device
Key Metrics: FPS, Latency, Thermal Temperature
Note: ARM CPU is much slower than x86 (expect 0.5-2 FPS vs 3-5 on Windows)
"""

import cv2
import torch
import time
import numpy as np
from ultralytics import YOLO
import threading
import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path

class JetsonCPUBaseline:
    def __init__(self, model_name="yolov8n.pt", log_file="jetson_phase1_results.json"):
        """Initialize CPU-only inference on Jetson Nano"""
        self.platform_info = {
            "os": platform.system(),
            "processor": platform.processor(),
            "device": self._get_jetson_info(),
        }
        
        print("="*70)
        print("🚀 JETSON NANO - PHASE 1: CPU BASELINE")
        print("="*70)
        print(f"Platform: {self.platform_info['os']} ({self.platform_info['device']})")
        print(f"CPU: {self.platform_info['processor']}")
        
        # Force CPU execution (don't use GPU yet)
        self.device = torch.device("cpu")
        self.model = YOLO(model_name)
        self.model.to(self.device)
        
        print(f"Device: {self.device}")
        print(f"Model: {model_name}")
        print("\n⚠️  ARM CPU PERFORMANCE NOTE:")
        print("   Jetson Nano uses ARM Cortex-A57 (4 cores)")
        print("   Much slower than x86 processors")
        print("   Expected FPS: 0.5-2 (vs 3-5 on Windows)")
        print("="*70 + "\n")
        
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'phase': 'CPU Baseline',
            'platform': 'Jetson Nano (ARM)',
            'fps_list': [],
            'latency_list': [],
            'temperature': [],
            'gpu_available': torch.cuda.is_available(),
        }
        self.log_file = log_file
    
    def _get_jetson_info(self):
        """Get Jetson device information"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                return f.read().strip()
        except:
            return "Jetson Device (model not readable)"
    
    def _read_tegra_temp(self):
        """Read thermal sensor temperature from Jetson"""
        try:
            result = subprocess.run(
                ['cat', '/sys/devices/virtual/thermal/thermal_zone0/temp'],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode == 0:
                temp_millic = int(result.stdout.strip())
                return temp_millic / 1000.0
        except:
            pass
        return None
    
    def monitor_system(self, duration=30):
        """Background thread: Monitor temperature and system state"""
        start = time.time()
        while time.time() - start < duration:
            temp = self._read_tegra_temp()
            if temp is not None:
                self.metrics['temperature'].append(temp)
            time.sleep(0.5)
    
    def run_inference(self, video_source="test_video.mp4", duration=30):
        """
        Run inference on Jetson CPU only (GPU not used)
        Purpose: Show ARM CPU performance baseline
        """
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            print(f"❌ Failed to open video: {video_source}")
            print("📝 Fallback: Using camera (0)")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ Camera also failed. Exiting.")
                return
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_system, args=(duration,), daemon=True)
        monitor_thread.start()
        
        frame_count = 0
        start_time = time.time()
        
        print(f"🚀 Starting inference on ARM CPU for {duration} seconds...\n")
        print(f"{'Frame':<8} {'FPS':<12} {'Latency (ms)':<20} {'Temp (°C)':<15}")
        print("-" * 60)
        
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                print("⚠️  End of video reached, looping...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            # Inference timing
            inference_start = time.time()
            results = self.model.predict(frame, conf=0.5, verbose=False)
            inference_time = (time.time() - inference_start) * 1000  # ms
            
            self.metrics['latency_list'].append(inference_time)
            frame_count += 1
            
            # Calculate metrics
            elapsed = time.time() - start_time
            current_fps = frame_count / elapsed
            self.metrics['fps_list'].append(current_fps)
            
            # Print every 10 frames (slower output for slow CPU)
            if frame_count % 10 == 0:
                avg_latency = np.mean(self.metrics['latency_list'][-10:])
                avg_temp = np.mean(self.metrics['temperature'][-10:]) if self.metrics['temperature'] else 0
                print(f"{frame_count:<8} {current_fps:<12.2f} {avg_latency:<20.2f} {avg_temp:<15.1f}")
        
        cap.release()
        monitor_thread.join(timeout=2)
        
        self._print_results(frame_count, time.time() - start_time)
    
    def _print_results(self, frame_count, elapsed):
        """Print comprehensive results and save to JSON"""
        if not self.metrics['latency_list']:
            print("❌ No frames processed")
            return
        
        results = {
            'timestamp': self.metrics['timestamp'],
            'phase': 'Phase 1: CPU Baseline',
            'platform': 'Jetson Nano (ARM Processor)',
            'architecture': 'ARM Cortex-A57 (4 cores)',
            'total_frames': frame_count,
            'duration_seconds': elapsed,
            'fps': {
                'average': np.mean(self.metrics['fps_list']),
                'min': np.min(self.metrics['fps_list']),
                'max': np.max(self.metrics['fps_list']),
                'std_dev': np.std(self.metrics['fps_list'])
            },
            'latency_ms': {
                'average': np.mean(self.metrics['latency_list']),
                'min': np.min(self.metrics['latency_list']),
                'max': np.max(self.metrics['latency_list']),
                'std_dev': np.std(self.metrics['latency_list'])
            },
            'thermal': {
                'average_temp_c': np.mean(self.metrics['temperature']) if self.metrics['temperature'] else None,
                'max_temp_c': np.max(self.metrics['temperature']) if self.metrics['temperature'] else None,
                'min_temp_c': np.min(self.metrics['temperature']) if self.metrics['temperature'] else None,
            },
            'power_metrics': {
                'estimated_power_w': 1.5,
                'power_per_fps': 1.5 / np.mean(self.metrics['fps_list']) if self.metrics['fps_list'] else 0
            },
            'system_info': self.platform_info
        }
        
        # Save to file
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print("\n" + "="*70)
        print("📊 JETSON NANO - PHASE 1 RESULTS (CPU BASELINE)")
        print("="*70)
        print(f"Total Frames Processed: {frame_count}")
        print(f"Duration: {elapsed:.2f}s")
        print(f"\n🎥 FPS Metrics:")
        print(f"   Average FPS: {results['fps']['average']:.2f}")
        print(f"   Min FPS: {results['fps']['min']:.2f}")
        print(f"   Max FPS: {results['fps']['max']:.2f}")
        print(f"\n⏱️  Latency Metrics:")
        print(f"   Average Latency: {results['latency_ms']['average']:.2f}ms")
        print(f"   Min Latency: {results['latency_ms']['min']:.2f}ms")
        print(f"   Max Latency: {results['latency_ms']['max']:.2f}ms")
        
        if results['thermal']['average_temp_c']:
            print(f"\n🌡️  Thermal Metrics:")
            print(f"   Average Temp: {results['thermal']['average_temp_c']:.1f}°C")
            print(f"   Max Temp: {results['thermal']['max_temp_c']:.1f}°C")
            print(f"   Min Temp: {results['thermal']['min_temp_c']:.1f}°C")
        
        print(f"\n💡 Performance Note:")
        print(f"   ARM CPU is much slower than x86")
        print(f"   FPS: {results['fps']['average']:.2f} (vs 3-5 on Windows)")
        print(f"   This is expected and normal for ARM processors")
        print(f"\n📁 Results saved to: {self.log_file}")
        print("="*70 + "\n")
        
        return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Jetson Nano - Phase 1: CPU Baseline")
    parser.add_argument('--video', type=str, default='test_video.mp4', help='Video file path')
    parser.add_argument('--duration', type=int, default=30, help='Duration in seconds')
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='Model name')
    
    args = parser.parse_args()
    
    baseline = JetsonCPUBaseline(model_name=args.model, log_file="results/jetson_phase1.json")
    baseline.run_inference(video_source=args.video, duration=args.duration)