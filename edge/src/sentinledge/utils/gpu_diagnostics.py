import sys
from typing import Any

def run_gpu_diagnostic() -> dict[str, Any]:
    """Inspect local hardware and inference runtime for GPU/CUDA compatibility."""
    report = {
        "python_version": sys.version.split()[0],
        "pytorch_version": None,
        "cuda_available": False,
        "cuda_version": None,
        "gpu_name": None,
        "gpu_count": 0,
        "vram_total_mb": None,
        "vram_free_mb": None,
        "active_device": "cpu",
        "onnx_providers": [],
    }

    try:
        import torch
        report["pytorch_version"] = torch.__version__
        if torch.cuda.is_available():
            report["cuda_available"] = True
            report["cuda_version"] = torch.version.cuda
            report["gpu_count"] = torch.cuda.device_count()
            report["gpu_name"] = torch.cuda.get_device_name(0)
            report["active_device"] = "cuda:0"
            try:
                free_bytes, total_bytes = torch.cuda.mem_get_info(0)
                report["vram_total_mb"] = round(total_bytes / (1024 * 1024), 2)
                report["vram_free_mb"] = round(free_bytes / (1024 * 1024), 2)
            except Exception:
                pass
    except ImportError:
        pass

    try:
        import onnxruntime as ort
        report["onnx_providers"] = ort.get_available_providers()
    except ImportError:
        pass

    return report

def print_diagnostic_banner():
    diag = run_gpu_diagnostic()
    print("=" * 65)
    print("  SENTINEL-EDGE GPU & INFERENCE RUNTIME DIAGNOSTIC")
    print("=" * 65)
    print(f"  PyTorch Version:         {diag['pytorch_version'] or 'Not Installed'}")
    print(f"  CUDA Available:          {diag['cuda_available']}")
    if diag["cuda_available"]:
        print(f"  NVIDIA GPU Model:        {diag['gpu_name']}")
        print(f"  CUDA Runtime Version:    {diag['cuda_version']}")
        print(f"  Total VRAM:              {diag['vram_total_mb']} MB")
        print(f"  Free VRAM:               {diag['vram_free_mb']} MB")
        print(f"  Active Inference Target: {diag['active_device']}")
    else:
        print("  Active Inference Target: CPU (Safe Fallback Mode)")
    if diag["onnx_providers"]:
        print(f"  ONNX Providers:          {', '.join(diag['onnx_providers'])}")
    print("=" * 65)
