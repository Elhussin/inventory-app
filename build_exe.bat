@echo off
chcp 65001 >nul
color 0A
title Building Inventory Management System

echo.
echo ============================================================
echo     🚀 Building Inventory Management System EXE
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python is installed
echo.

:: Check if inventory_system.py exists
if not exist "inventory_system.py" (
    color 0C
    echo ❌ ERROR: inventory_system.py not found!
    echo.
    echo Please make sure inventory_system.py is in the same folder as this batch file.
    echo.
    pause
    exit /b 1
)

echo ✅ inventory_system.py found
echo.

echo ============================================================
echo     Step 1/5: Cleaning old build files...
echo ============================================================
if exist build (
    echo Removing old build folder...
    rmdir /s /q build
)
if exist dist (
    echo Removing old dist folder...
    rmdir /s /q dist
)
if exist InventorySystem.spec (
    echo Removing old spec file...
    del InventorySystem.spec
)
echo ✅ Cleanup completed
echo.

echo ============================================================
echo     Step 2/5: Installing/Updating required packages...
echo ============================================================
echo Installing reportlab...
pip install reportlab --quiet --disable-pip-version-check
echo Installing pyinstaller...
pip install pyinstaller --quiet --disable-pip-version-check
echo ✅ Packages installed
echo.

echo ============================================================
echo     Step 3/5: Building executable (This may take a while)...
echo ============================================================

:: Check if icon exists
if exist "icon.ico" (
    echo Using custom icon: icon.ico
    pyinstaller --onefile ^
                --windowed ^
                --noconsole ^
                --name="InventorySystem" ^
                --icon=icon.ico ^
                --hidden-import=reportlab.pdfgen.canvas ^
                --hidden-import=reportlab.lib.pagesizes ^
                --hidden-import=reportlab.platypus ^
                inventory_system.py
) else (
    echo No icon.ico found, building without custom icon...
    pyinstaller --onefile ^
                --windowed ^
                --noconsole ^
                --name="InventorySystem" ^
                --hidden-import=reportlab.pdfgen.canvas ^
                --hidden-import=reportlab.lib.pagesizes ^
                --hidden-import=reportlab.platypus ^
                inventory_system.py
)

if errorlevel 1 (
    color 0C
    echo.
    echo ❌ ERROR: Build failed!
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo ✅ Build completed successfully
echo.

echo ============================================================
echo     Step 4/5: Cleaning up temporary files...
echo ============================================================
if exist build (
    rmdir /s /q build
    echo ✅ Removed build folder
)
if exist InventorySystem.spec (
    del InventorySystem.spec
    echo ✅ Removed spec file
)
echo.

echo ============================================================
echo     Step 5/5: Verifying output...
echo ============================================================
if exist "dist\InventorySystem.exe" (
    echo ✅ SUCCESS! Executable created successfully!
    echo.
    echo 📁 Location: dist\InventorySystem.exe
    
    :: Get file size
    for %%A in ("dist\InventorySystem.exe") do (
        set size=%%~zA
    )
    set /a sizeMB=!size! / 1048576
    echo 📊 File size: !sizeMB! MB
    echo.
    
    :: Create a readme file
    echo Creating README.txt...
    (
        echo ============================================================
        echo    Inventory Management System - Executable Package
        echo ============================================================
        echo.
        echo ✅ Installation: No installation required!
        echo.
        echo 🚀 How to Run:
        echo    1. Double-click InventorySystem.exe
        echo    2. The program will create inventory.db automatically
        echo    3. Start managing your inventory!
        echo.
        echo 📋 Features:
        echo    ✓ Add/Edit/Delete Products
        echo    ✓ Search and Filter
        echo    ✓ Add Stock to existing products
        echo    ✓ Export to CSV and PDF
        echo    ✓ Mismatch Reports
        echo    ✓ Live Statistics
        echo.
        echo 💾 Database:
        echo    - File: inventory.db (created automatically)
        echo    - Location: Same folder as the EXE
        echo.
        echo ⚠️ Important Notes:
        echo    - Keep inventory.db in the same folder as the EXE
        echo    - Make sure you have write permissions in the folder
        echo    - The first run might be slower (Windows Defender scan)
        echo.
        echo 🔧 System Requirements:
        echo    - Windows 7/8/10/11 (32-bit or 64-bit)
        echo    - No Python installation needed
        echo    - Approximately 50MB free space
        echo.
        echo 📞 Troubleshooting:
        echo    - If Windows Defender blocks the app, click "More info" 
        echo      then "Run anyway"
        echo    - Make sure antivirus doesn't quarantine the file
        echo    - Run as Administrator if you face permission issues
        echo.
        echo ============================================================
        echo    © 2025 Inventory Management System
        echo ============================================================
    ) > "dist\README.txt"
    echo ✅ README.txt created
    echo.
    
    color 0A
    echo ============================================================
    echo     🎉 BUILD SUCCESSFUL! 🎉
    echo ============================================================
    echo.
    echo 📦 Your executable is ready to use!
    echo 📁 Find it in: dist\InventorySystem.exe
    echo.
    echo 📝 Next Steps:
    echo    1. Go to the 'dist' folder
    echo    2. Copy InventorySystem.exe to any Windows PC
    echo    3. Run it directly - No Python needed!
    echo.
    echo 💡 Tip: Read dist\README.txt for more information
    echo.
    
    :: Ask if user wants to open the dist folder
    echo Would you like to open the dist folder now? (Y/N)
    set /p openFolder=
    if /i "!openFolder!"=="Y" (
        start explorer "dist"
    )
    
) else (
    color 0C
    echo ❌ ERROR: InventorySystem.exe was not created!
    echo Please check the error messages above.
)

echo.
echo ============================================================
echo Press any key to exit...
pause >nul


