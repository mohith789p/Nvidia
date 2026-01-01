"""
WINDOWS PC - PHASE 1: CPU BASELINE
Platform: Windows 10/11 with NVIDIA GPU (RTX 2070+)
Purpose: Establish CPU-only performance baseline
Key Metrics: FPS, Latency, GPU Utilization (should be ~0%)
"""

import cv2
import torch
import time
import numpy as np
from ultralytics import YOLO
import psutil
import threading
import json
import platform
from datetime import datetime
from pathlib import Path

class WindowsCPUBaseline:
    def __init__(self, model_name="yolov8n.pt", log_file="windows_phase1_results.json"):
        """Initialize CPU-only inference on Windows"""
        self.platform_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
        }
        
        print("="*70)
        print("🖥️  WINDOWS PC - PHASE 1: CPU BASELINE")
        print("="*70)
        print(f"Platform: {self.platform_info['os']} {self.platform_info['os_version']}")
        print(f"CPU: {self.platform_info['processor']} ({self.platform_info['cpu_count']} cores)")
        
        # Force CPU execution
        self.device = torch.device("cpu")
        self.model = YOLO(model_name)
        self.model.to(self.device)
        
        print(f"Device: {self.device}")
        print(f"Model: {model_name}")
        print("="*70 + "\n")
        
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'phase': 'CPU Baseline',
            'platform': 'Windows PC',
            'fps_list': [],
            'latency_list': [],
            'cpu_load': [],
            'memory_usage': [],
            'gpu_available': torch.cuda.is_available(),
            'gpu_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
        }
        self.log_file = log_file
    
    def monitor_system(self, duration=30):
        """Background thread: Monitor CPU/GPU utilization"""
        start = time.time()
        while time.time() - start < duration:
            self.metrics['cpu_load'].append(psutil.cpu_percent(interval=0.1))
            
            # Memory usage in MB
            memory_percent = psutil.virtual_memory().percent
            self.metrics['memory_usage'].append(memory_percent)
            
            time.sleep(0.5)
    
    def run_inference(self, video_source="test_video.mp4", duration=30):
        """
        Run inference on CPU only
        Data flow: Video → CPU Process → (PCIe sends to GPU but GPU not used)
        """
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            print(f"❌ Failed to open video: {video_source}")
            print("📝 Fallback: Using webcam (0)")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ Webcam also failed. Exiting.")
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
        
        print(f"🚀 Starting inference on CPU for {duration} seconds...\n")
        print(f"{'Frame':<8} {'FPS':<12} {'Latency (ms)':<20} {'CPU Load (%)':<15}")
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
            
            # Print every 30 frames
            if frame_count % 30 == 0:
                avg_cpu = np.mean(self.metrics['cpu_load'][-30:]) if self.metrics['cpu_load'] else 0
                avg_latency = np.mean(self.metrics['latency_list'][-30:])
                print(f"{frame_count:<8} {current_fps:<12.2f} {avg_latency:<20.2f} {avg_cpu:<15.1f}")
        
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
            'platform': 'Windows PC (Discrete GPU)',
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
            'cpu_load_percent': {
                'average': np.mean(self.metrics['cpu_load']),
                'min': np.min(self.metrics['cpu_load']),
                'max': np.max(self.metrics['cpu_load']),
                'std_dev': np.std(self.metrics['cpu_load'])
            },
            'memory_percent': {
                'average': np.mean(self.metrics['memory_usage']),
                'min': np.min(self.metrics['memory_usage']),
                'max': np.max(self.metrics['memory_usage'])
            },
            'power_metrics': {
                'estimated_power_w': np.mean(self.metrics['cpu_load']) * 0.15,
                'power_per_fps': (np.mean(self.metrics['cpu_load']) * 0.15) / np.mean(self.metrics['fps_list'])
            },
            'system_info': self.platform_info
        }
        
        # Save to file
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print("\n" + "="*70)
        print("📊 WINDOWS PC - PHASE 1 RESULTS (CPU BASELINE)")
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
        print(f"\n💻 Resource Utilization:")
        print(f"   Avg CPU Load: {results['cpu_load_percent']['average']:.2f}%")
        print(f"   Avg Memory: {results['memory_percent']['average']:.2f}%")
        print(f"   Est. Power: {results['power_metrics']['estimated_power_w']:.2f}W")
        print(f"   Power/FPS: {results['power_metrics']['power_per_fps']:.3f}W/FPS")
        print(f"\n📁 Results saved to: {self.log_file}")
        print("="*70 + "\n")
        
        return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Windows PC - Phase 1: CPU Baseline")
    parser.add_argument('--video', type=str, default='test_video.mp4', help='Video file path')
    parser.add_argument('--duration', type=int, default=30, help='Duration in seconds')
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='Model name')
    
    args = parser.parse_args()
    
    baseline = WindowsCPUBaseline(model_name=args.model, log_file="results/windows_phase1.json")
    baseline.run_inference(video_source=args.video, duration=args.duration)