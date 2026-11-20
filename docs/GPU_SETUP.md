# NVIDIA GPU Setup Guide (RTX 3050 Laptop 6GB)

## Prerequisites
- NVIDIA Graphics Driver version 535 or higher
- Windows 11 with WSL2 or Native Python 3.12

## Recommended PyTorch CUDA Installation
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## Verification
Run the SentinelEdge GPU diagnostic utility:
```bash
python scripts/check_gpu.py
```

Expected Output on NVIDIA RTX 3050:
- CUDA Available: True
- GPU Model: NVIDIA GeForce RTX 3050 Laptop GPU
- Total VRAM: ~6144 MB
- Active Inference Target: cuda:0
