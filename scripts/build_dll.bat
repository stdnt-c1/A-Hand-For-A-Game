@echo off
echo Building res_balancer.dll for Windows...

REM Change to resBalancer directory
cd /d "%~dp0..\resBalancer"
if not exist "res_balancer.cpp" (
    echo ERROR: res_balancer.cpp not found in resBalancer directory
    pause
    exit /b 1
)

REM Create build directory if it doesn't exist
if not exist "build" mkdir build

REM Check for MinGW first (since it's more reliable)
where g++ >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Found MinGW g++, compiling...
    g++ --version
    echo.
    echo Compiling with MinGW g++...
    g++ -shared -O3 -o build\res_balancer.dll res_balancer.cpp -static-libgcc -static-libstdc++
    
    if exist "build\res_balancer.dll" (
        echo.
        echo ✅ Successfully built res_balancer.dll with MinGW
        echo Location: %CD%\build\res_balancer.dll
        echo File size: 
        dir build\res_balancer.dll | find "res_balancer.dll"
    ) else (
        echo ❌ MinGW build failed
        echo Trying without static linking...
        g++ -shared -O3 -o build\res_balancer.dll res_balancer.cpp
        if exist "build\res_balancer.dll" (
            echo ✅ Successfully built res_balancer.dll with MinGW (dynamic linking)
        ) else (
            echo ❌ Both MinGW approaches failed
        )
    )
    goto :end
)

REM Fallback to MSVC if MinGW not found
where cl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Neither MinGW nor Visual Studio Build Tools found!
    echo Please ensure g++ or cl is in your PATH
    pause
    exit /b 1
)

REM Build the DLL using MSVC
echo Compiling with MSVC...
cl /LD /O2 /DWIN32 /D_WINDOWS /D_USRDLL res_balancer.cpp /Fe:build\res_balancer.dll

REM Check if build was successful
if exist "build\res_balancer.dll" (
    echo.
    echo ✅ Successfully built res_balancer.dll with MSVC
    echo Location: %CD%\build\res_balancer.dll
) else (
    echo ❌ MSVC build failed
)

:end
echo.
pause
