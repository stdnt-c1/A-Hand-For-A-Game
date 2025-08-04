# Environment Setup Guide

This document provides detailed instructions for setting up the development and runtime environment for AzimuthControl.

> [!WARNING]
> This setup guide is optimized for the original author's development environment. Configuration may need adjustment for different hardware or system configurations.

## System Requirements

### Operating System
- **Windows 10/11** (Primary support)
- **Linux** (Ubuntu 20.04+ recommended)
- **macOS** (Limited support)

> [!IMPORTANT]
> Windows is the primary supported platform. Linux and macOS support is experimental and may require additional configuration.

### Hardware Requirements
- **CPU**: Intel i5 or AMD Ryzen 5 equivalent or better
- **RAM**: Minimum 8GB, 16GB recommended
- **Camera**: USB webcam or integrated camera with 720p+ resolution
- **Storage**: 2GB free space for installation and dependencies

> [!TIP]
> For optimal performance, use a dedicated USB webcam with good lighting conditions.

## Core Dependencies

### Python Environment
```bash
# Python 3.9+ required (3.11 recommended)
python --version  # Should show 3.9.x or higher

# Virtual environment (recommended)
python -m venv azimuth_env
# Windows
azimuth_env\Scripts\activate
# Linux/macOS
source azimuth_env/bin/activate
```

### Python Packages
Install via requirements.txt:
```bash
pip install -r requirements.txt
```

**Core packages include:**
- `opencv-python>=4.8.0` - Computer vision and camera handling
- `mediapipe>=0.10.0` - Hand landmark detection
- `numpy>=1.24.0` - Numerical computations
- `pillow>=9.5.0` - Image processing
- `screeninfo>=0.8.1` - Multi-monitor support

## C++ Compilation Environment (Optional but Recommended)

### Windows Setup

#### Option 1: MinGW-w64 (Recommended)
```powershell
# Install via winget
winget install BrechtSanders.WinLibs.POSIX.UCRT

# Verify installation
gcc --version
# Should show: gcc.exe (MinGW-W64 x86_64-ucrt-posix-seh, built by Brecht Sanders, r4) 15.1.0
```

#### Option 2: Microsoft Build Tools
```powershell
# Install Visual Studio Build Tools 2022
winget install Microsoft.VisualStudio.2022.BuildTools

# Components needed:
# - MSVC v143 compiler toolset
# - Windows 11 SDK (latest version)
# - CMake tools for C++
```

#### Option 3: Visual Studio Community
```powershell
# Full Visual Studio installation
winget install Microsoft.VisualStudio.2022.Community

# Workloads needed:
# - Desktop development with C++
# - Game development with C++
```

### Linux Setup
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential cmake git

# CentOS/RHEL/Fedora
sudo dnf groupinstall "Development Tools"
sudo dnf install cmake git

# Verify
gcc --version
make --version
cmake --version
```

### macOS Setup
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Or install Xcode from App Store

# Homebrew (recommended)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install cmake

# Verify
gcc --version
make --version
cmake --version
```

## Additional Tools and Libraries

### Development Tools
```bash
# Git (version control)
git --version  # Should be 2.30+ 

# Windows
winget install Git.Git

# Linux
sudo apt install git  # Ubuntu/Debian
sudo dnf install git  # Fedora

# macOS
brew install git
```

### Camera and Audio Libraries (System Level)

#### Windows
- **DirectShow**: Usually pre-installed
- **Windows Media Foundation**: Pre-installed on Windows 10+
- **Additional codecs**: Install K-Lite Codec Pack if needed

#### Linux
```bash
# Video4Linux and related libraries
sudo apt install v4l-utils ffmpeg

# Additional camera support
sudo apt install libv4l-dev libavcodec-dev libavformat-dev libswscale-dev
```

#### macOS
```bash
# Camera access permissions required
# System Preferences > Security & Privacy > Camera
```

## Environment Variables

### Required Environment Variables
```bash
# Windows (PowerShell)
$env:PYTHONPATH = "E:\AzimuthControl;$env:PYTHONPATH"

# Linux/macOS (Bash/Zsh)
export PYTHONPATH="/path/to/AzimuthControl:$PYTHONPATH"
```

### Optional Environment Variables
```bash
# Performance tuning
export OMP_NUM_THREADS=4  # Limit OpenMP threads
export OPENBLAS_NUM_THREADS=1  # Limit BLAS threads for better performance

# MediaPipe optimizations
export MEDIAPIPE_DISABLE_GPU=1  # Force CPU mode if GPU issues occur
```

## Building C++ Extensions

### Automatic Build (Recommended)
```bash
# Windows
scripts\build_dll.bat

# Linux/macOS
chmod +x scripts/build_dll.sh
./scripts/build_dll.sh
```

### Manual Build
```bash
# Navigate to C++ extension directory
cd resBalancer

# Windows with MinGW-w64
g++ -shared -O3 -o build\res_balancer.dll res_balancer.cpp -static-libgcc -static-libstdc++

# Linux
g++ -shared -fPIC -O3 -o build/res_balancer.so res_balancer.cpp

# macOS
g++ -shared -fPIC -O3 -o build/res_balancer.dylib res_balancer.cpp
```

## Verification Steps

### 1. Test Python Environment
```bash
cd /path/to/AzimuthControl
python -c "import cv2, mediapipe, numpy; print('Core dependencies OK')"
```

### 2. Test Camera Access
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Error'); cap.release()"
```

### 3. Test C++ Extensions
```bash
python tests/test_dll.py
```

### 4. Test Complete System
```bash
python tests/test_imports.py
python tests/test_performance.py
```

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError"
```bash
# Ensure virtual environment is activated
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

#### "Camera not found"
```bash
# Check camera permissions (especially macOS)
# Try different camera indices
python -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"
```

#### "C++ extension not loading"
```bash
# Verify architecture match
python -c "import platform; print(platform.architecture())"
file resBalancer/build/res_balancer.dll  # Should match Python architecture

# Rebuild with correct architecture
scripts\build_dll.bat
```

#### "Performance issues"
```bash
# Check CPU usage
# Reduce camera resolution
# Disable C++ extensions temporarily
# Check for memory leaks
```

### Platform-Specific Issues

#### Windows
- **DLL not found**: Ensure MinGW-w64 bin directory is in PATH
- **Access denied**: Run as administrator if needed
- **Antivirus blocking**: Add project directory to exclusions

#### Linux
- **Permission denied**: Use `sudo` for system package installation
- **Camera permissions**: Add user to `video` group: `sudo usermod -a -G video $USER`

#### macOS
- **Camera permissions**: Allow in System Preferences
- **Code signing**: May need to sign binaries for distribution

## Performance Optimization

### Recommended Settings
```bash
# Environment variables for optimal performance
export OMP_NUM_THREADS=$(nproc)  # Use all CPU cores
export OPENCV_OPENCL_RUNTIME=""  # Disable OpenCL if causing issues

# Python optimizations
export PYTHONOPTIMIZE=1  # Enable Python optimizations
```

### Hardware Acceleration
- **CUDA**: Install NVIDIA CUDA toolkit for GPU acceleration (optional)
- **OpenCL**: May improve MediaPipe performance on supported hardware
- **Intel MKL**: Can improve NumPy performance on Intel CPUs

## Next Steps

After completing environment setup:
1. Run the verification steps above
2. Execute `python tests/test_gesture_system.py` for full system test
3. Check documentation in `docs/` for usage instructions
4. Review `PROJECT_SUMMARY.md` for architecture overview

For issues not covered here, check:
- GitHub Issues: https://github.com/stdnt-c1/HandsFree-Gaming/issues
- Project documentation in `docs/` directory
- Community discussions and wiki
