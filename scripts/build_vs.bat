@echo off
echo 🔨 Visual Studio DLL Builder
echo ===========================

REM Find and setup Visual Studio environment
set "VSCMD_FOUND="

echo Looking for Visual Studio installations...

REM Try VS 2022 first
if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" (
    echo Found VS 2022 Build Tools
    call "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
    set "VSCMD_FOUND=2022 BuildTools"
    goto :build
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat" (
    echo Found VS 2022 Community
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
    set "VSCMD_FOUND=2022 Community"
    goto :build
)

REM Try VS 2019
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\Tools\VsDevCmd.bat" (
    echo Found VS 2019 Build Tools
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
    set "VSCMD_FOUND=2019 BuildTools"
    goto :build
)

if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\Tools\VsDevCmd.bat" (
    echo Found VS 2019 Community
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
    set "VSCMD_FOUND=2019 Community"
    goto :build
)

echo ❌ No Visual Studio installation found
echo.
echo Please install Visual Studio Build Tools:
echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
pause
exit /b 1

:build
echo ✅ Using Visual Studio %VSCMD_FOUND%
echo.

REM Change to resBalancer directory
cd /d "%~dp0..\resBalancer"

echo Current directory: %CD%
echo.

if not exist "res_balancer.cpp" (
    echo ❌ res_balancer.cpp not found
    pause
    exit /b 1
)

echo Building res_balancer.dll...
echo.

REM Create build directory
if not exist build mkdir build

REM Compile with detailed output
cl /LD /O2 /EHsc /DWIN32 /D_WINDOWS /D_USRDLL /I. res_balancer.cpp /Fe:build\res_balancer.dll /link /NOLOGO

echo.
if exist "build\res_balancer.dll" (
    echo ✅ SUCCESS! DLL built successfully
    echo.
    echo File: %CD%\build\res_balancer.dll
    dir build\res_balancer.dll
    echo.
    echo Size: 
    for %%A in (build\res_balancer.dll) do echo %%~zA bytes
    echo.
    echo You can now run: python hand_control.py
) else (
    echo ❌ Build failed
    echo.
    echo Trying with different compiler flags...
    cl /LD /O2 /DWIN32 /D_WINDOWS res_balancer.cpp /Fe:build\res_balancer.dll
    
    if exist "build\res_balancer.dll" (
        echo ✅ SUCCESS with alternative flags!
    ) else (
        echo ❌ Both attempts failed
        echo.
        echo This might be due to:
        echo 1. Missing Windows SDK
        echo 2. Incomplete Visual Studio installation
        echo 3. Source code issues
        echo.
        echo The system will work without the DLL (just slower)
    )
)

echo.
pause
