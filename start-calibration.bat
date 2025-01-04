@echo off
REM Coba cari lokasi conda.bat di direktori user
set "USER_CONDA=%USERPROFILE%\miniconda3\condabin\conda.bat"
set "USER_ANACONDA=%USERPROFILE%\anaconda3\condabin\conda.bat"

REM Cek apakah conda.bat ada di lokasi standar
if exist "%USER_CONDA%" (
    set CONDA_BAT=%USER_CONDA%
) else if exist "%USER_ANACONDA%" (
    set CONDA_BAT=%USER_ANACONDA%
) else (
    REM Jika tidak ditemukan, coba cari conda secara otomatis di PATH
    for /f "delims=" %%i in ('where conda') do set CONDA_BAT=%%i
)

REM Jika conda masih tidak ditemukan, berikan pesan error
if not defined CONDA_BAT (
    echo "Conda tidak ditemukan di PATH atau di lokasi standar (miniconda3/anaconda3)."
    echo "Tambahkan conda ke PATH atau periksa lokasi instalasi Conda."
    pause
    exit /b 1
)

REM Aktifkan environment Conda
call "%CONDA_BAT%" activate smart-crosswalk

REM Pindah ke direktori app-yolo
cd /d "%~dp0src/distance"

REM Tambahkan root proyek ke PYTHONPATH
set PYTHONPATH=%~dp0

REM Jalankan script get-focals.py
python get-focals.py

REM Cek jika ada error
if errorlevel 1 (
    echo "Error terjadi saat menjalankan main.py. Periksa konfigurasi dan jalur proyek."
    pause
)
