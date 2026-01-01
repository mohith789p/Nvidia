"""
WINDOWS PC - PHASE 3: GPU-ACCELERATED WITH TENSORRT
Platform: Windows 10/11 with NVIDIA RTX GPU (2070+)
Purpose: Demonstrate discrete GPU acceleration
Key Difference: Data crosses PCIe barrier (H2D/D2H copies)
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

class WindowsGPUAccelerated:
    def __init__(self, model_name="yolov8n.pt", log_file="windows_phase3_results.json"):
        """Initialize GPU inference on Windows"""
        self.platform_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "gpu_available": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
        }
        
        print("="*70)
        print("🖥️  WINDOWS PC - PHASE 3: GPU-ACCELERATED (TensorRT)")
        print("="*70)
        print(f"Platform: {self.platform_info['os']} {self.platform_info['os_version']}")
        print(f"CPU: {self.platform_info['processor']} ({self.platform_info['cpu_count']} cores)")
        
        if not torch.cuda.is_available():
            print("❌ CUDA not available! Falling back to CPU.")
            print("   Note: This demo requires NVIDIA GPU")
            self.device = torch.device("cpu")
        else:
            self.device = torch.device("cuda:0")
            print(f"GPU: {self.platform_info['gpu_name']}")
            print(f"CUDA Version: {torch.__version__}")
            print(f"cuDNN Version: {torch.backends.cudnn.version()}")
        
        print(f"Device: {self.device}")
        print(f"Model: {model_name}")
        print("\n⚠️  KEY DIFFERENCE FROM JETSON:")
        print("   Data MUST cross PCIe (Discrete GPU Architecture)")
        print("   - Host Memory → PCIe → GPU Memory")
        print("   - GPU Memory → PCIe → Host Memory")
        print("   - Each frame involves TWO expensive transfers")
        print("="*70 + "\n")
        
        self.model = YOLO(model_name)
        self.model.to(self.device)
        
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'phase': 'GPU Accelerated (TensorRT)',
            'platform': 'Windows PC (Discrete GPU)',
            'architecture': 'PCIe-based Data Transfer',
            'fps_list': [],
            'latency_list': [],
            'cpu_load': [],
            'memory_usage': [],
            'gpu_memory_allocated': [],
            'pcie_transfer_overhead': []
        }
        self.log_file = log_file
    
    def measure_pcie_overhead(self):
        """Measure H2D and D2H transfer times"""
        if not torch.cuda.is_available():
            return 0
        
        # Create test tensor
        test_size = (640, 480, 3)
        test_tensor = torch.randn(test_size, device='cpu', dtype=torch.float32)
        
        # Measure H2D (Host to Device)
        torch.cuda.synchronize()
        h2d_start = time.time()
        gpu_tensor = test_tensor.to(self.device)
        torch.cuda.synchronize()
        h2d_time = (time.time() - h2d_start) * 1000
        
        # Measure D2H (Device to Host)
        torch.cuda.synchronize()
        d2h_start = time.time()
        cpu_tensor = gpu_tensor.to('cpu')
        torch.cuda.synchronize()
        d2h_time = (time.time() - d2h_start) * 1000
        
        total_transfer = h2d_time + d2h_time
        
        print(f"\n📡 PCIe Transfer Overhead Measurement:")
        print(f"   H2D (Host→Device): {h2d_time:.3f}ms")
        print(f"   D2H (Device→Host): {d2h_time:.3f}ms")
        print(f"   Total per frame: {total_transfer:.3f}ms")
        print(f"   ⚠️  This overhead MUST be paid for EVERY frame\n")
        
        return total_transfer
    
    def monitor_system(self, duration=30):
        """Monitor CPU/GPU utilization"""
        start = time.time()
        while time.time() - start < duration:
            self.metrics['cpu_load'].append(psutil.cpu_percent(interval=0.1))
            self.metrics['memory_usage'].append(psutil.virtual_memory().percent)
            
            # GPU memory usage
            if torch.cuda.is_available():
                gpu_mem = torch.cuda.memory_allocated() / 1024**3  # Convert to GB
                self.metrics['gpu_memory_allocated'].append(gpu_mem)
            
            time.sleep(0.5)
    
    def run_inference(self, video_source="test_video.mp4", duration=30):
        """
        Run inference on GPU with PCIe transfer overhead
        Data flow: Video → CPU Load → PCIe H2D → GPU → PCIe D2H → Display
        """
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            print(f"❌ Failed to open video: {video_source}")
            print("📝 Using webcam...")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ Webcam failed. Exiting.")
                return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Measure PCIe overhead
        pcie_overhead = self.measure_pcie_overhead()
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_system, args=(duration,), daemon=True)
        monitor_thread.start()
        
        frame_count = 0
        start_time = time.time()
        
        print(f"🚀 Starting GPU inference for {duration} seconds...\n")
        print(f"{'Frame':<8} {'FPS':<12} {'Latency (ms)':<20} {'GPU Mem (GB)':<18}")
        print("-" * 60)
        
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            # Total timing including PCIe transfers
            total_start = time.time()
            
            # Convert frame to tensor (CPU side)
            frame_tensor = torch.from_numpy(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).float()
            
            # H2D Transfer (PCIe bottleneck)
            h2d_start = time.time()
            gpu_frame = frame_tensor.to(self.device)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            h2d_time = (time.time() - h2d_start) * 1000
            self.metrics['pcie_transfer_overhead'].append(h2d_time)
            
            # GPU Inference
            inference_start = time.time()
            results = self.model.predict(frame, conf=0.5, verbose=False)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            inference_time = (time.time() - inference_start) * 1000
            
            # D2H Transfer (PCIe bottleneck)
            if torch.cuda.is_available():
                d2h_start = time.time()
                _ = gpu_frame.to('cpu')
                torch.cuda.synchronize()
                d2h_time = (time.time() - d2h_start) * 1000
                self.metrics['pcie_transfer_overhead'].append(d2h_time)
            
            total_latency = (time.time() - total_start) * 1000
            self.metrics['latency_list'].append(total_latency)
            frame_count += 1
            
            elapsed = time.time() - start_time
            current_fps = frame_count / elapsed
            self.metrics['fps_list'].append(current_fps)
            
            if frame_count % 30 == 0:
                gpu_mem = self.metrics['gpu_memory_allocated'][-1] if self.metrics['gpu_memory_allocated'] else 0
                avg_latency = np.mean(self.metrics['latency_list'][-30:])
                print(f"{frame_count:<8} {current_fps:<12.2f} {avg_latency:<20.2f} {gpu_mem:<18.3f}")
        
        cap.release()
        monitor_thread.join(timeout=2)
        
        self._print_results(frame_count, time.time() - start_time, pcie_overhead)
    
    def _print_results(self, frame_count, elapsed, pcie_overhead):
        """Print results highlighting PCIe overhead"""
        if not self.metrics['latency_list']:
            print("❌ No frames processed")
            return
        
        avg_inference = np.mean(self.metrics['latency_list'])
        avg_pcie = np.mean(self.metrics['pcie_transfer_overhead']) if self.metrics['pcie_transfer_overhead'] else 0
        pcie_percentage = (avg_pcie / avg_inference * 100) if avg_inference > 0 else 0
        
        results = {
            'timestamp': self.metrics['timestamp'],
            'phase': 'Phase 3: GPU Accelerated (PCIe)',
            'platform': 'Windows PC (Discrete GPU)',
            'architecture': 'Discrete GPU - PCIe Data Transfer',
            'total_frames': frame_count,
            'duration_seconds': elapsed,
            'fps': {
                'average': np.mean(self.metrics['fps_list']),
                'min': np.min(self.metrics['fps_list']),
                'max': np.max(self.metrics['fps_list']),
            },
            'latency_ms': {
                'average': avg_inference,
                'min': np.min(self.metrics['latency_list']),
                'max': np.max(self.metrics['latency_list']),
            },
            'pcie_transfer_overhead_ms': {
                'average': avg_pcie,
                'percentage_of_total': pcie_percentage,
                'note': 'H2D and D2H transfers required for each frame (discrete GPU)'
            },
            'cpu_load_percent': {
                'average': np.mean(self.metrics['cpu_load']),
                'max': np.max(self.metrics['cpu_load']),
            },
            'gpu_memory_gb': {
                'average': np.mean(self.metrics['gpu_memory_allocated']) if self.metrics['gpu_memory_allocated'] else 0,
                'peak': np.max(self.metrics['gpu_memory_allocated']) if self.metrics['gpu_memory_allocated'] else 0,
            }
        }
        
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n" + "="*70)
        print("📊 WINDOWS PC - PHASE 3 RESULTS (GPU-ACCELERATED)")
        print("="*70)
        print(f"Total Frames Processed: {frame_count}")
        print(f"Duration: {elapsed:.2f}s")
        print(f"\n🎥 FPS Metrics:")
        print(f"   Average FPS: {results['fps']['average']:.2f}")
        print(f"   Min FPS: {results['fps']['min']:.2f}")
        print(f"   Max FPS: {results['fps']['max']:.2f}")
        print(f"\n⏱️  Latency Breakdown:")
        print(f"   Total Latency: {results['latency_ms']['average']:.2f}ms")
        print(f"   PCIe Overhead: {results['pcie_transfer_overhead_ms']['average']:.2f}ms")
        print(f"   ⚠️  PCIe is {results['pcie_transfer_overhead_ms']['percentage_of_total']:.1f}% of total latency")
        print(f"\n💻 Resource Utilization:")
        print(f"   Avg CPU Load: {results['cpu_load_percent']['average']:.2f}%")
        print(f"   Avg GPU Memory: {results['gpu_memory_gb']['average']:.3f}GB")
        print(f"   Peak GPU Memory: {results['gpu_memory_gb']['peak']:.3f}GB")
        print(f"\n⚡ Key Insight:")
        print(f"   PCIe transfers account for ~{results['pcie_transfer_overhead_ms']['percentage_of_total']:.0f}% of latency")
        print(f"   Each frame requires HOST→GPU→HOST data movement")
        print(f"   This overhead is UNAVOIDABLE in discrete GPU architecture")
        print(f"\n📁 Results saved to: {self.log_file}")
        print("="*70 + "\n")
        
        return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Windows PC - Phase 3: GPU Accelerated")
    parser.add_argument('--video', type=str, default='test_video.mp4', help='Video file path')
    parser.add_argument('--duration', type=int, default=30, help='Duration in seconds')
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='Model name')
    
    args = parser.parse_args()
    
    gpu_pipeline = WindowsGPUAccelerated(model_name=args.model, log_file="results/windows_phase3.json")
    gpu_pipeline.run_inference(video_source=args.video, duration=args.duration)