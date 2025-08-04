# System Requirements and Dependencies

## Python Dependencies

All Python dependencies are managed through `requirements.txt`:

> [!NOTE]
> Version numbers represent minimum requirements. Newer versions are generally compatible unless otherwise noted.

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

## System-Level Dependencies

### Windows

#### Required System Components
- **DirectShow**: Camera access framework (pre-installed Windows 10+)
- **Windows Media Foundation**: Media processing pipeline (pre-installed)
- **Visual C++ Redistributable**: Runtime libraries for compiled extensions

#### C++ Development Environment (Optional but Recommended)
```powershell
# Option 1: MinGW-w64 (Recommended for open-source)
winget install BrechtSanders.WinLibs.POSIX.UCRT

# Option 2: Microsoft Build Tools 2022
winget install Microsoft.VisualStudio.2022.BuildTools

# Option 3: Visual Studio Community (Full IDE)
winget install Microsoft.VisualStudio.2022.Community
```

**Build Tools Components Needed:**
- MSVC v143 compiler toolset for x64
- Windows 11 SDK (latest version)
- CMake tools for Visual Studio

### Linux (Ubuntu/Debian)

#### Essential System Packages
```bash
# Core development tools
sudo apt update
sudo apt install build-essential cmake git pkg-config

# Video and camera support
sudo apt install libv4l-dev v4l-utils ffmpeg

# OpenCV system dependencies
sudo apt install libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev
sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev

# Python development headers
sudo apt install python3-dev python3-pip

# Optional: Hardware acceleration
sudo apt install libva-dev libvdpau-dev  # Video acceleration
```

#### CentOS/RHEL/Fedora
```bash
# Development tools
sudo dnf groupinstall "Development Tools"
sudo dnf install cmake git pkg-config

# Media libraries
sudo dnf install v4l-utils ffmpeg-devel

# Python development
sudo dnf install python3-devel python3-pip
```

### macOS

#### Required Components
```bash
# Xcode Command Line Tools (Essential)
xcode-select --install

# Homebrew package manager
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Development tools via Homebrew
brew install cmake git pkg-config

# Optional: Additional media libraries
brew install ffmpeg
```

## Hardware Requirements

### Camera Requirements
- **Resolution**: Minimum 640x480, recommended 1280x720 or higher
- **Frame Rate**: Minimum 15 FPS, recommended 30 FPS
- **Interface**: USB 2.0+ or built-in webcam
- **Lighting**: Adequate lighting for hand detection (natural or artificial)

### Performance Requirements

#### Minimum System Specs
- **CPU**: Intel Core i3-8100 / AMD Ryzen 3 2200G
- **RAM**: 8GB DDR4
- **Storage**: 2GB available space
- **OS**: Windows 10 v1909+ / Ubuntu 20.04+ / macOS 11+

#### Recommended System Specs
- **CPU**: Intel Core i5-10400 / AMD Ryzen 5 3600
- **RAM**: 16GB DDR4
- **Storage**: 4GB available space (SSD recommended)
- **GPU**: Integrated graphics sufficient, dedicated GPU optional for acceleration

#### High-Performance Setup
- **CPU**: Intel Core i7-12700 / AMD Ryzen 7 5700X
- **RAM**: 32GB DDR4
- **GPU**: NVIDIA GTX 1660+ or AMD RX 580+ (for CUDA/OpenCL acceleration)
- **Storage**: NVMe SSD

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
export PYTHONPATH="/path/to/AzimuthControl:$PYTHONPATH"

# Optional performance tuning
export OMP_NUM_THREADS=4              # Limit OpenMP threads
export OPENBLAS_NUM_THREADS=1         # Limit BLAS threads
export MEDIAPIPE_DISABLE_GPU=1        # Force CPU mode if needed

# Windows PowerShell equivalent
$env:PYTHONPATH = "E:\AzimuthControl;$env:PYTHONPATH"
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
