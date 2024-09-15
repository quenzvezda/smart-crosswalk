import cv2
import numpy as np

# Variabel global untuk koordinat bounding box
ref_point = []
cropping = False


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


# Fungsi utama
def main():
    global img_copy

    # Inisialisasi video capture
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Webcam Feed")

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
            return

    cap.release()
    cv2.destroyAllWindows()

    # Meminta input jarak dan lebar nyata objek
    jarak = float(input("Masukkan jarak antara kamera dan objek (cm): "))
    lebar_nyata = float(input("Masukkan lebar nyata objek (cm): "))

    img_copy = img.copy()
    clone = img.copy()
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", click_and_crop)

    print("Gambar bounding box di sekitar objek dan tekan 'c' ketika selesai.")

    while True:
        cv2.imshow("Image", img_copy)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('r'):
            img_copy = clone.copy()
        elif key == ord('c'):
            if len(ref_point) == 2:
                # Menghitung lebar objek dalam piksel
                x1, y1 = ref_point[0]
                x2, y2 = ref_point[1]
                lebar_piksel = abs(x2 - x1)
                print(f"Lebar objek dalam citra (piksel): {lebar_piksel}")

                # Menghitung panjang fokus
                focal = (lebar_piksel * jarak) / lebar_nyata
                print(f"Nilai focal length (piksel): {focal}")

                # Menampilkan hasil pada gambar
                cv2.putText(img_copy, f"Focal Length: {focal:.2f} px", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("Image", img_copy)
            else:
                print("Silakan gambar bounding box terlebih dahulu.")
        elif key == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
