"""Standalone diagnostic tool for NVIDIA CUDA & PyTorch runtime verification."""
import sys

def main():
    print("=" * 65)
    print("  SENTINEL-EDGE GPU & INFERENCE RUNTIME DIAGNOSTIC")
    print("=" * 65)
    print(f"  Python Version:     {sys.version.split()[0]}")

    try:
        import torch
        print(f"  PyTorch Version:    {torch.__version__}")
        cuda_ok = torch.cuda.is_available()
        print(f"  CUDA Available:     {cuda_ok}")
        if cuda_ok:
            print(f"  CUDA Version:       {torch.version.cuda}")
            print(f"  GPU Device Name:    {torch.cuda.get_device_name(0)}")
            free_b, total_b = torch.cuda.mem_get_info(0)
            print(f"  Total VRAM:         {round(total_b / (1024**2), 1)} MB")
            print(f"  Free VRAM:          {round(free_b / (1024**2), 1)} MB")
            print(f"  Inference Target:   CUDA (Hardware Accelerated)")
        else:
            print("  Inference Target:   CPU (Safe Fallback Mode)")
    except ImportError:
        print("  PyTorch:            Not Installed")

    try:
        import onnxruntime as ort
        print(f"  ONNX Providers:     {', '.join(ort.get_available_providers())}")
    except ImportError:
        print("  ONNX Runtime:       Optional / Not Installed")

    print("=" * 65)

if __name__ == "__main__":
    main()
