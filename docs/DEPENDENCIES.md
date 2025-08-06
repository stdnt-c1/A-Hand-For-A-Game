# System Requirements and Dependencies

## Python Dependencies

All Python dependencies are managed through `requirements.txt`:

**Note**: Version numbers represent minimum requirements. Newer versions are generally compatible unless otherwise noted.

```
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
pillow>=9.5.0
screeninfo>=0.8.1
numba>=0.57.0
psutil>=5.9.0
```

### Core Dependencies Breakdown

#### Computer Vision & AI
- **opencv-python (4.8.0+)**: Camera capture, image processing, computer vision operations
- **mediapipe (0.10.0+)**: Google's ML framework for hand landmark detection
- **numpy (1.24.0+)**: Numerical computations, array operations, linear algebra

#### Image Processing & Display
- **pillow (9.5.0+)**: Image format support, image manipulation
- **screeninfo (0.8.1+)**: Multi-monitor detection and resolution management

#### Performance & Optimization
- **numba (0.57.0+)**: Just-in-time compilation for performance-critical functions
- **psutil (5.9.0+)**: System resource monitoring (CPU, memory, processes)

> [!WARNING]
> MediaPipe version compatibility is critical. Use the specified version or newer to ensure proper hand landmark detection functionality.

## Enhanced GPU Acceleration Dependencies

### NVIDIA CUDA Toolkit (Required for Maximum Performance)
- **CUDA 12.8+**: Full GPU acceleration with NVIDIA GPUs
- **Compatible NVIDIA Driver**: 545.84+ for optimal performance
- **Supported GPU Architectures**: 
  - Maxwell (GTX 900 series)
  - Pascal (GTX 10 series) 
  - Turing (RTX 20 series)
  - Ampere (RTX 30 series)
  - Ada Lovelace (RTX 40 series)

#### CUDA Installation
```powershell
# Download from: https://developer.nvidia.com/cuda-downloads
# Install CUDA 12.8 with VS Integration
# Verify installation:
nvcc --version
nvidia-smi
```

### Enhanced C++ Build Environment
```powershell
# Visual Studio 2022 Build Tools (Required)
winget install Microsoft.VisualStudio.2022.BuildTools

# Required Components:
# - MSVC v143 compiler toolset for x64
# - Windows 11 SDK (latest)
# - CMake tools for Visual Studio
```

## System-Level Dependencies

### Windows (Enhanced Requirements)

#### Required System Components
- **DirectShow**: Camera access framework (pre-installed Windows 10+)
- **Windows Media Foundation**: Media processing pipeline (pre-installed)
- **Visual C++ Redistributable 2022**: Runtime libraries for CUDA extensions
- **NVIDIA Graphics Driver**: 545.84+ for CUDA 12.8 compatibility

#### Enhanced Performance Libraries
- **CUDA Runtime (cudart64_12.dll)**: Automatically deployed with build
- **CUBLAS**: CUDA Basic Linear Algebra Subroutines
- **CURAND**: CUDA Random Number Generation
- **CUFFT**: CUDA Fast Fourier Transform

### Hardware Requirements (Updated for CUDA)

#### Minimum System Specs (CPU Fallback)
- **CPU**: Intel Core i3-8100 / AMD Ryzen 3 2200G
- **RAM**: 8GB DDR4
- **Storage**: 2GB available space
- **OS**: Windows 10 v1909+ / Ubuntu 20.04+ / macOS 11+

#### Recommended System Specs (CUDA Accelerated)
- **CPU**: Intel Core i5-10400 / AMD Ryzen 5 3600
- **RAM**: 16GB DDR4
- **GPU**: NVIDIA GTX 1660+ with 4GB+ VRAM
- **Storage**: 4GB available space (NVMe SSD recommended)

#### High-Performance Setup (Maximum CUDA Performance)
- **CPU**: Intel Core i7-12700 / AMD Ryzen 7 5700X
- **RAM**: 32GB DDR4
- **GPU**: NVIDIA RTX 3060+ with 8GB+ VRAM
- **Storage**: NVMe SSD with 10GB+ available space
- **Cooling**: Adequate GPU cooling for sustained performance

## Compilation Dependencies

### C++ Extension Requirements

The project includes optional C++ extensions for performance optimization. These require:

#### Compiler Requirements
- **GCC/G++**: Version 9.0+ (Linux/MinGW)
- **MSVC**: Visual Studio 2019+ (Windows)
- **Clang**: Version 10+ (macOS)

#### Build System Requirements
- **Make**: GNU Make 4.0+
- **CMake**: 3.16+ (optional, for advanced builds)
- **Git**: 2.30+ (for version control and submodules)

### Library Dependencies for C++ Extensions
```cpp
// Standard libraries used
#include <cmath>        // Mathematical functions
#include <vector>       // Dynamic arrays
#include <algorithm>    // STL algorithms
#include <chrono>       // Time measurements
```

No external C++ libraries are required - the extensions use only standard library components.

## Runtime Environment

### Environment Variables
```bash
# Required for Python module resolution
export PYTHONPATH="/path/to/A-Hand-For-A-Game:$PYTHONPATH"

# Optional performance tuning
export OMP_NUM_THREADS=4              # Limit OpenMP threads
export OPENBLAS_NUM_THREADS=1         # Limit BLAS threads
export MEDIAPIPE_DISABLE_GPU=1        # Force CPU mode if needed

# Windows PowerShell equivalent
$env:PYTHONPATH = "C:\path\to\A-Hand-For-A-Game;$env:PYTHONPATH"
```

### Camera Permissions

#### Windows
- Automatic camera access prompt on first run
- Check Privacy Settings > Camera if issues occur

#### Linux
- Add user to video group: `sudo usermod -a -G video $USER`
- Ensure camera device permissions: `ls -l /dev/video*`

#### macOS
- Allow camera access in System Preferences > Security & Privacy > Camera
- Grant permission when prompted by the application

## Optional Acceleration Libraries

### NVIDIA CUDA (Optional)
```bash
# For NVIDIA GPU acceleration
# Download from: https://developer.nvidia.com/cuda-downloads
# Supports: CUDA 11.0+ with compatible NVIDIA drivers
```

### Intel OpenVINO (Optional)
```bash
# For Intel CPU/GPU optimization
# Download from: https://docs.openvino.ai/latest/openvino_docs_install_guides_overview.html
```

### Apple Metal Performance Shaders (macOS)
- Automatically available on macOS 10.13+
- Used by MediaPipe for acceleration when available

## Verification Commands

### Test System Dependencies
```bash
# Check Python version
python --version

# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera:', cap.isOpened()); cap.release()"

# Test core libraries
python -c "import cv2, mediapipe, numpy, numba; print('All core libraries imported successfully')"

# Test C++ compiler (if available)
gcc --version || g++ --version || cl.exe

# Check system resources
python -c "import psutil; print(f'CPU: {psutil.cpu_count()}, RAM: {psutil.virtual_memory().total//1024**3}GB')"
```

### Performance Verification
```bash
# Run comprehensive tests
python tests/test_performance.py

# Check C++ extension availability
python -c "from src.performance.optimized_engine import OptimizedGestureEngine; e = OptimizedGestureEngine(); print('C++ Extensions:', e.cpp_available)"
```

## Troubleshooting Common Dependency Issues

### ModuleNotFoundError
```bash
# Ensure virtual environment is activated
# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### Camera Access Issues
```bash
# List available cameras
python -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"

# Check camera permissions (Linux)
ls -l /dev/video*
```

### C++ Compilation Issues
```bash
# Verify compiler architecture matches Python
python -c "import platform; print('Python arch:', platform.architecture())"
gcc -dumpmachine  # Should match Python architecture

# Clean and rebuild
rm -rf resBalancer/build/*
scripts/build_dll.sh  # or .bat on Windows
```

### Performance Issues
```bash
# Check system resources
python -c "import psutil; print('CPU:', psutil.cpu_percent(), 'Memory:', psutil.virtual_memory().percent)"

# Run with reduced settings
export MEDIAPIPE_DISABLE_GPU=1
python hand_control.py
```
