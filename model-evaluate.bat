@echo off
CALL C:\Users\trisa\miniconda3\Scripts\activate.bat
CALL conda activate smart-crosswalk
cd src/evaluate
python ssd_map.py