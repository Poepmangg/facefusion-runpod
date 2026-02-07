#!/usr/bin/env python3
"""
FaceFusion RunPod Ultimate Script
Author: Samuel Torenstra
Date: January 2026

This script automates FaceFusion face-swapping on RunPod for batch processing.
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACE = Path("/workspace")
INPUT_DIR = WORKSPACE / "inputmedia"
OUTPUT_DIR = WORKSPACE / "output"
REF_MODEL = INPUT_DIR / "refmodel.jpg"
FACEFUSION_DIR = WORKSPACE / "facefusion"

# Supported formats
VIDEO_EXT = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".webm"]
PHOTO_EXT = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]

class RunPodProcessor:
    def __init__(self):
        self.stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "start_time": datetime.now().isoformat(),
            "errors": []
        }
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_system(self):
        """Phase 1: System check"""
        self.log("=" * 60)
        self.log("ULTIMATE RUNPOD FACESWAP START")
        self.log("=" * 60)
        
        # Check Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.log(f"Python {py_version}")
        
        # Check GPU
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("NVIDIA GPU detected")
            else:
                self.log("No GPU detected - CPU mode (VERY SLOW)", "WARNING")
        except FileNotFoundError:
            self.log("nvidia-smi not found", "WARNING")
        
        # Check workspace
        self.log(f"Workspace: {WORKSPACE}")
        
        # Check input directory
        if not INPUT_DIR.exists():
            self.log(f"INPUT DIR NOT FOUND: {INPUT_DIR}", "ERROR")
            sys.exit(1)
        self.log("Input dir found")
        
        # Check reference model
        if not REF_MODEL.exists():
            self.log(f"REFMODEL NOT FOUND: {REF_MODEL}", "ERROR")
            sys.exit(1)
        
        # Validate refmodel is actual image
        try:
            from PIL import Image
            img = Image.open(REF_MODEL)
            w, h = img.size
            self.log(f"Reference image valid: {w}x{h}")
            if w < 100 or h < 100:
                self.log("Warning: Reference image is very small", "WARNING")
        except Exception as e:
            self.log(f"REFMODEL CORRUPTED: {e}", "ERROR")
            sys.exit(1)
        
        # Find media files
        self.media_files = self.find_media_files()
        if len(self.media_files) == 0:
            self.log(f"NO MEDIA FILES FOUND in {INPUT_DIR}", "ERROR")
            sys.exit(1)
        
        self.log(f"Found {len(self.media_files)} media files")
        self.stats["total"] = len(self.media_files)
        
    def find_media_files(self):
        """Recursively find all supported media files"""
        files = []
        for ext_list in [VIDEO_EXT, PHOTO_EXT]:
            for ext in ext_list:
                files.extend(INPUT_DIR.rglob(f"*{ext}"))
                files.extend(INPUT_DIR.rglob(f"*{ext.upper()}"))
        
        # Remove refmodel from list
        files = [f for f in files if f.name != "refmodel.jpg"]
        return sorted(files)
    
    def install_facefusion(self):
        """Phase 2: Install FaceFusion"""
        self.log("=" * 60)
        self.log("Phase 2: Installation")
        self.log("=" * 60)
        
        if FACEFUSION_DIR.exists():
            self.log("FaceFusion already installed, skipping...")
            return
        
        # Clone FaceFusion repo
        self.log("Clone FaceFusion repo...")
        subprocess.run([
            "git", "clone", "https://github.com/facefusion/facefusion",
            str(FACEFUSION_DIR)
        ], check=True)
        
        # Install FaceFusion
        self.log("Install FaceFusion package...")
        os.chdir(FACEFUSION_DIR)
        subprocess.run(["python", "install.py"], check=True)
        
        self.log("Installation complete")
    
    def process_media(self):
        """Phase 3: Process all media files"""
        self.log("=" * 60)
        self.log("Phase 3: Processing")
        self.log("=" * 60)
        
        # Create output directory
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        start_time = time.time()
        
        for idx, media_file in enumerate(self.media_files, 1):
            try:
                self.log(f"{idx}/{len(self.media_files)} Processing {media_file.name}")
                self.log(f"  Size: {media_file.stat().st_size / (1024*1024):.1f}MB")
                
                # Determine output filename
                output_name = media_file.stem + "_swapped" + media_file.suffix
                output_file = OUTPUT_DIR / output_name
                
                # Run FaceFusion
                cmd = [
                    "python", "run.py",
                    "-s", str(REF_MODEL),
                    "-t", str(media_file),
                    "-o", str(output_file),
                    "--execution-providers", "cuda"
                ]
                
                result = subprocess.run(
                    cmd,
                    cwd=FACEFUSION_DIR,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 min timeout
                )
                
                if result.returncode == 0 and output_file.exists():
                    self.log(f"  Output: {output_name}")
                    self.stats["successful"] += 1
                else:
                    raise Exception(f"Processing failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.log(f"  ERROR: Timeout (5 min) - {media_file.name}", "ERROR")
                self.stats["failed"] += 1
                self.stats["errors"].append({
                    "file": str(media_file),
                    "error": "Timeout"
                })
            except Exception as e:
                self.log(f"  ERROR: {media_file.name} - {str(e)}", "ERROR")
                self.stats["failed"] += 1
                self.stats["errors"].append({
                    "file": str(media_file),
                    "error": str(e)
                })
        
        duration = time.time() - start_time
        self.stats["duration_minutes"] = round(duration / 60, 1)
        self.stats["end_time"] = datetime.now().isoformat()
    
    def generate_report(self):
        """Phase 4: Generate report"""
        self.log("=" * 60)
        self.log("Phase 4: Report")
        self.log("=" * 60)
        
        self.log("PROCESSING COMPLETE")
        success_rate = (self.stats["successful"] / self.stats["total"]) * 100
        self.log(f"Successful: {self.stats['successful']}/{self.stats['total']} ({success_rate:.1f}%)")
        self.log(f"Failed: {self.stats['failed']}/{self.stats['total']}")
        self.log(f"Duration: {self.stats['duration_minutes']} minutes")
        self.log(f"Output: {OUTPUT_DIR}")
        
        # Save statistics
        stats_file = OUTPUT_DIR / "statistics.json"
        with open(stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)
        self.log(f"Statistics saved to {stats_file}")
        
        # Save full log
        # (In production, redirect stdout to file)
        
    def run(self):
        """Main execution"""
        try:
            self.check_system()
            self.install_facefusion()
            self.process_media()
            self.generate_report()
        except KeyboardInterrupt:
            self.log("\nProcess interrupted by user", "WARNING")
            sys.exit(1)
        except Exception as e:
            self.log(f"Fatal error: {e}", "ERROR")
            sys.exit(1)

if __name__ == "__main__":
    processor = RunPodProcessor()
    processor.run()
