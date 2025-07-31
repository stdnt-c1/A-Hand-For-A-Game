@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   AzimuthControl DLL Builder v2.0
echo ========================================
echo.

REM Change to resBalancer directory
cd /d "%~dp0..\resBalancer"
if not exist "res_balancer.cpp" (
    echo ERROR: res_balancer.cpp not found in resBalancer directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Source file found: res_balancer.cpp
echo.

REM Create build directory
if not exist "build" mkdir build

REM ===========================================
REM Try Method 1: Visual Studio Build Tools
REM ===========================================
echo [Method 1] Trying Visual Studio Build Tools...

REM Look for Visual Studio installations
set "VS_FOUND="
set "VCVARS_PATH="

REM Check VS 2022
if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
    set "VCVARS_PATH=C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
    set "VS_FOUND=2022 BuildTools"
) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    set "VCVARS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
    set "VS_FOUND=2022 Community"
) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat" (
    set "VCVARS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat"
    set "VS_FOUND=2022 Professional"
)

REM Check VS 2019 if 2022 not found
if not defined VS_FOUND (
    if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
        set "VCVARS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
        set "VS_FOUND=2019 BuildTools"
    ) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" (
        set "VCVARS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
        set "VS_FOUND=2019 Community"
    )
)

if defined VS_FOUND (
    echo Found Visual Studio: !VS_FOUND!
    echo Setting up environment...
    
    REM Setup VS environment and compile
    call "!VCVARS_PATH!" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo Compiling with MSVC...
        cl /LD /O2 /EHsc /DWIN32 /D_WINDOWS /D_USRDLL res_balancer.cpp /Fe:build\res_balancer.dll 2>build_error.log
        
        if exist "build\res_balancer.dll" (
            echo.
            echo ✅ SUCCESS: Built res_balancer.dll with Visual Studio !VS_FOUND!
            echo Location: %CD%\build\res_balancer.dll
            del build_error.log 2>nul
            goto :success
        ) else (
            echo ❌ MSVC compilation failed
            if exist build_error.log (
                echo Error details:
                type build_error.log
            )
        )
    ) else (
        echo ❌ Failed to setup VS environment
    )
) else (
    echo Visual Studio not found in standard locations
)

REM ===========================================
REM Try Method 2: MinGW-w64
REM ===========================================
echo.
echo [Method 2] Trying MinGW-w64...

REM Look for MinGW installations
set "MINGW_FOUND="
set "GCC_PATH="

REM Common MinGW installation paths
set "PATHS[0]=C:\mingw64\bin\g++.exe"
set "PATHS[1]=C:\msys64\mingw64\bin\g++.exe"
set "PATHS[2]=C:\msys64\ucrt64\bin\g++.exe"
set "PATHS[3]=C:\TDM-GCC-64\bin\g++.exe"
set "PATHS[4]=C:\MinGW\bin\g++.exe"

for /L %%i in (0,1,4) do (
    if exist "!PATHS[%%i]!" (
        set "GCC_PATH=!PATHS[%%i]!"
        set "MINGW_FOUND=%%i"
        goto :mingw_found
    )
)

REM Try g++ in PATH
g++ --version >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set "GCC_PATH=g++"
    set "MINGW_FOUND=PATH"
)

:mingw_found
if defined MINGW_FOUND (
    echo Found MinGW: !GCC_PATH!
    echo Compiling with MinGW...
    
    "!GCC_PATH!" -shared -fPIC -O3 -std=c++11 -o build\res_balancer.dll res_balancer.cpp 2>mingw_error.log
    
    if exist "build\res_balancer.dll" (
        echo.
        echo ✅ SUCCESS: Built res_balancer.dll with MinGW
        echo Location: %CD%\build\res_balancer.dll
        del mingw_error.log 2>nul
        goto :success
    ) else (
        echo ❌ MinGW compilation failed
        if exist mingw_error.log (
            echo Error details:
            type mingw_error.log
        )
    )
) else (
    echo MinGW not found in standard locations or PATH
)

REM ===========================================
REM Try Method 3: Python setuptools
REM ===========================================
echo.
echo [Method 3] Trying Python setuptools...

cd /d "%~dp0.."
python -c "import setuptools" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo Found setuptools, attempting build...
    python setup.py build_ext --inplace 2>setup_error.log
    
    if exist "res_balancer*.pyd" (
        echo ✅ SUCCESS: Built Python extension with setuptools
        dir res_balancer*.pyd
        goto :success
    ) else if exist "resBalancer\build\res_balancer.dll" (
        echo ✅ SUCCESS: Built DLL with setuptools
        echo Location: %CD%\resBalancer\build\res_balancer.dll
        goto :success
    ) else (
        echo ❌ Setuptools build failed
        if exist setup_error.log (
            echo Error details:
            type setup_error.log
        )
    )
) else (
    echo Setuptools not available
)

REM ===========================================
REM All methods failed
REM ===========================================
echo.
echo ❌ ALL BUILD METHODS FAILED
echo.
echo 📋 Troubleshooting Steps:
echo.
echo 1. Visual Studio Build Tools:
echo    - Install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo    - Make sure "C++ build tools" workload is installed
echo    - Try running from "Developer Command Prompt"
echo.
echo 2. MinGW-w64:
echo    - Install from: https://www.mingw-w64.org/downloads/
echo    - Or use MSYS2: https://www.msys2.org/
echo    - Add MinGW bin directory to PATH
echo.
echo 3. Alternative: The system works without the DLL
echo    - Run: python hand_control.py
echo    - Performance will be slightly slower but fully functional
echo.

goto :end

:success
echo.
echo 🎉 BUILD SUCCESSFUL!
echo.
echo The DLL is ready to use. The application will now use optimized C++ calculations.
echo.
echo To test: python hand_control.py
echo.

:end
pause
