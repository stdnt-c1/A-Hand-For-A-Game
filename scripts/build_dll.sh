#!/bin/bash
echo "Building res_balancer.dll for Linux/macOS..."

# Check if g++ is available
if ! command -v g++ &> /dev/null; then
    echo "ERROR: g++ not found!"
    echo "Please install build-essential (Ubuntu/Debian) or equivalent"
    echo "Ubuntu/Debian: sudo apt install build-essential"
    echo "CentOS/RHEL: sudo yum groupinstall 'Development Tools'"
    echo "macOS: Install Xcode Command Line Tools"
    exit 1
fi

# Create build directory if it doesn't exist
mkdir -p build

# Build the shared library
echo "Compiling with g++..."
g++ -shared -fPIC -O3 -o build/res_balancer.so resBalancer/res_balancer.cpp

# Check if build was successful
if [ -f "build/res_balancer.so" ]; then
    echo ""
    echo "✅ Successfully built res_balancer.so"
    echo "Location: $(pwd)/build/res_balancer.so"
    echo ""
    echo "You can now copy this library to your project root or add the build directory to your LD_LIBRARY_PATH"
else
    echo ""
    echo "❌ Build failed!"
    echo "Please check the error messages above"
fi

echo ""
