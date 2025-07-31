@echo off
echo 🔍 DLL Build Diagnostics
echo ========================

echo Current directory: %CD%
echo.

echo 📁 Checking source files...
if exist "resBalancer\res_balancer.cpp" (
    echo ✅ res_balancer.cpp found
) else (
    echo ❌ res_balancer.cpp NOT found
    dir resBalancer 2>nul
)

if exist "resBalancer\res_balancer.h" (
    echo ✅ res_balancer.h found
) else (
    echo ❌ res_balancer.h NOT found
)
echo.

echo 🔧 Checking compilers...
echo.

REM Check Visual Studio
echo [Visual Studio Locations]
if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools" (
    echo ✅ VS 2022 BuildTools found
    dir "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars*.bat" 2>nul
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community" (
    echo ✅ VS 2022 Community found
    dir "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars*.bat" 2>nul
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools" (
    echo ✅ VS 2019 BuildTools found
    dir "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars*.bat" 2>nul
)
echo.

REM Check MinGW
echo [MinGW Locations]
if exist "C:\mingw64\bin\g++.exe" (
    echo ✅ MinGW64 found at C:\mingw64\bin\g++.exe
    C:\mingw64\bin\g++.exe --version 2>nul
)
if exist "C:\msys64\mingw64\bin\g++.exe" (
    echo ✅ MSYS2 MinGW64 found at C:\msys64\mingw64\bin\g++.exe
    C:\msys64\mingw64\bin\g++.exe --version 2>nul
)
echo.

REM Check PATH
echo [PATH Check]
where cl 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ cl.exe found in PATH
    cl 2>&1 | findstr "Version"
) else (
    echo ❌ cl.exe not in PATH
)

where g++ 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ g++.exe found in PATH
    g++ --version 2>nul | findstr "g++"
) else (
    echo ❌ g++.exe not in PATH
)
echo.

echo 🐍 Checking Python tools...
python -c "import setuptools; print('✅ setuptools available')" 2>nul || echo "❌ setuptools not available"
python -c "import distutils; print('✅ distutils available')" 2>nul || echo "❌ distutils not available"
echo.

echo 📋 Recommendations:
echo.
if not exist "resBalancer\res_balancer.cpp" (
    echo ❌ Source file missing - this is the main problem
    echo.
)

where cl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 💡 To use Visual Studio:
    echo    1. Open "Developer Command Prompt for VS 2022" or "Developer Command Prompt for VS 2019"
    echo    2. Navigate to: %CD%
    echo    3. Run: scripts\build_dll_advanced.bat
    echo.
)

where g++ >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 💡 To use MinGW:
    echo    1. Add MinGW bin directory to PATH
    echo    2. Or run with full path: C:\mingw64\bin\g++.exe
    echo.
)

pause
