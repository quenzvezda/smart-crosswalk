import cv2
import numpy as np

# Variabel global untuk koordinat bounding box
ref_point = []
cropping = False

# Hardcode parameter
focal = 502  # Panjang fokus berdasarkan kalibrasi sebelumnya
width = 3.5  # Lebar nyata objek dalam cm (di-hardcode)
dist = 0  # Estimasi jarak yang akan dihitung
pixels = 0  # Placeholder untuk jumlah piksel (akan dihitung dari bounding box)

def click_and_crop(event, x, y, flags, param):
    global ref_point, cropping, img_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
        cropping = True

    elif event == cv2.EVENT_LBUTTONUP:
        ref_point.append((x, y))
        cropping = False

        # Gambar rectangle
        cv2.rectangle(img_copy, ref_point[0], ref_point[1], (0, 255, 0), 2)
        cv2.imshow("Image", img_copy)

        # Cetak koordinat untuk memastikan mereka terekam
        print(f"Koordinat bounding box: {ref_point}")

# Fungsi untuk menangkap gambar
def capture_image(cap):
    print("Tekan 'p' untuk mengambil gambar.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Gagal mengambil gambar.")
            break

        cv2.imshow("Webcam Feed", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            # Simpan frame saat ini dan hentikan feed
            img = frame.copy()
            break
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return None

    return img

# Fungsi utama
def main():
    global img_copy, dist, pixels, ref_point

    # Inisialisasi video capture
    cap = cv2.VideoCapture(0)

    while True:
        img = capture_image(cap)

        if img is None:
            break  # Jika user menekan 'q', keluar dari program

        # Proses gambar setelah di-capture
        img_copy = img.copy()
        clone = img.copy()
        cv2.namedWindow("Image")
        cv2.setMouseCallback("Image", click_and_crop)

        print("Gambar bounding box di sekitar objek dan tekan 'c' ketika selesai.")
        while True:
            cv2.imshow("Image", img_copy)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('r'):
                # Reset dan kembali ke pengambilan gambar
                print("Reset! Mengambil gambar baru...")
                break  # Keluar dari loop untuk mengambil gambar baru
            elif key == ord('c'):
                if len(ref_point) == 2:
                    # Menghitung lebar objek dalam piksel
                    x1, y1 = ref_point[0]
                    x2, y2 = ref_point[1]
                    pixels = abs(x2 - x1)  # Lebar dalam piksel
                    print(f"Lebar objek dalam citra (piksel): {pixels}")

                    if pixels > 0:
                        # Menghitung estimasi jarak
                        dist = (width * focal) / pixels
                        print(f"Estimasi jarak (cm): {dist}")

                        # Menampilkan hasil estimasi jarak pada gambar
                        cv2.putText(img_copy, f"Jarak: {dist:.2f} cm", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.imshow("Image", img_copy)
                    else:
                        print("Lebar bounding box dalam piksel tidak valid, ulangi proses.")
                else:
                    print("Silakan gambar bounding box terlebih dahulu.")
            elif key == ord('q'):
                # Jika user menekan 'q', keluar dari program
                cap.release()
                cv2.destroyAllWindows()
                return

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
