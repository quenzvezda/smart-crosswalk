# Smart Crosswalk Project

## Deskripsi
Proyek ini bertujuan untuk mendeteksi pejalan kaki dan mobil di penyeberangan jalan satu arah dengan menggunakan Raspberry Pi 4 Model B untuk mengontrol lampu LED, rambu, dan speaker, serta laptop untuk melakukan inferensi real-time menggunakan model deteksi objek seperti YOLO atau SSD.

## Persyaratan Sistem
- Raspberry Pi 4 Model B
- Laptop / Komputer dengan GPU yang mendukung CUDA
- Kamera untuk deteksi real-time
- Koneksi internet stabil untuk setup dan unduhan

## Instalasi

### Miniconda
Install Miniconda untuk Windows dengan langkah cepat berikut (jalankan per-baris):

```bash
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe -o miniconda.exe
start /wait "" miniconda.exe /S
del miniconda.exe
```
Setelah instalasi, buka `Anaconda Prompt (miniconda3)` untuk melanjutkan.

### Pembuatan dan Aktivasi Environment
Buat dan aktifkan environment Conda untuk proyek ini dengan menggunakan perintah berikut:

```bash
conda create -n smart-crosswalk python=3.9
conda activate smart-crosswalk
```

### Instalasi TensorFlow dengan Dukungan CUDA
Untuk menginstal TensorFlow dan komponen yang mendukung CUDA, gunakan perintah berikut di dalam environment Conda yang sudah aktif:
```bash
conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0
pip install "tensorflow<2.11"
```

Setelah instalasi, verifikasi bahwa TensorFlow telah terinstal dengan benar dan dapat mengakses GPU:
```bash
python -c "import tensorflow as tf; print('Num GPUs Available: ', len(tf.config.list_physical_devices('GPU')))"
```

### Instalasi PyTorch dengan Dukungan CUDA
Jika sudah terdapat instalasi PyTorch sebelumnya di environment Anda, disarankan untuk menguninstallnya terlebih dahulu:
```bash
pip uninstall torch torchvision torchaudio
```

Lanjutkan dengan instalasi PyTorch yang mendukung CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Verifikasi bahwa PyTorch telah terinstal dengan benar dan dapat menggunakan CUDA:
```bash
python -c "import torch; print('Is cuda available:', torch.cuda.is_available())"
```

## Sumber
- TensorFlow: [Panduan Instalasi TensorFlow](https://www.tensorflow.org/install/pip?hl=id#windows-native_1)
- PyTorch: [Panduan Memulai PyTorch](https://pytorch.org/get-started/locally/#anaconda)
- Miniconda: [Miniconda Download Site](https://docs.anaconda.com/free/miniconda/)
- cuDNN: [Nvidia cuDNN Download Site](https://developer.nvidia.com/cudnn-downloads)
- CUDA Toolkit: [Nvidia CUDA Toolkit Download Site](https://developer.nvidia.com/cuda-downloads)
