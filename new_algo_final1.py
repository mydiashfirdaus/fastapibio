import requests
import cv2
import numpy as np
import time
import subprocess

cap = None
# Fungsi untuk mengirim flag ke server FastAPI
def kirim_flag_fokus_rendah(direction, last_send_time, interval=1):
    current_time = time.time()
    if current_time - last_send_time >= interval:
        response = requests.get(f"http://localhost:8000/set_flag/{direction}")
        if response.status_code != 200:
            print(f"Gagal mengirim flag {direction} ke server FastAPI")
        last_send_time = current_time
    return last_send_time

def kirim_flag_fokus_tinggi(direction1, last_send_time, interval1=1):
    current_time1 = time.time()
    if current_time1 - last_send_time >= interval1:
        response1 = requests.get(f"http://localhost:8000/set_flag1/{direction1}")
        if response1.status_code != 200:
            print(f"Gagal mengirim flag {direction1} ke server FastAPI")
        last_send_time = current_time1
    return last_send_time

def reset_flag(flag_main, last_send_time, interval=1):
    current_time = time.time()
    if current_time - last_send_time >= interval:
        response = requests.get(f"http://localhost:8000/selesai/{flag_main}")
        if response.status_code != 200:
            print(f"Gagal mengirim flag {flag_main} ke server FastAPI")
        last_send_time = current_time
    return last_send_time

def Fokus_rendah(Cur_blur, Prev_blur):
    if Prev_blur > Cur_blur:
        action_text = 'Putar ke kanan'
        direction = 1  # Putar ke kanan.
    elif Prev_blur < Cur_blur * 0.5:  # Toleransi di atas ambang batas.
        action_text = 'Putar ke kiri'
        direction = 2  # Putar ke kiri.
    else:
        action_text = 'optimum'
        direction = 0  # Tidak bergerak.
    Prev_blur = Cur_blur
    return action_text, direction, Prev_blur

def Fokus_tinggi(Cur_blur1, Prev_blur1):
    if Prev_blur1 > Cur_blur1:
        action_text1 = 'Putar ke kanan'
        direction1 = 1  # Putar ke kanan.
    elif Prev_blur1 < Cur_blur1 * 0.01:  # Toleransi di atas ambang batas.
        action_text1 = 'Putar ke kiri'
        direction1 = 2  # Putar ke kiri.
    else:
        action_text1 = 'optimum'
        direction1 = 0  # Tidak bergerak.
    Prev_blur1 = Cur_blur1
    return action_text1, direction1, Prev_blur1

def detect_blur_live_stream_laplacian(frame):
    grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(grayscale_frame, cv2.CV_64F)
    blur_level = np.mean(np.abs(laplacian))
    return blur_level

def main():
    interval = 1
    interval1 = 1
    last_send_time = time.time() - interval
    Prev_blur = 0
    Prev_blur1 = 0
    camera_opened = False  # Menandai apakah kamera sedang dibuka

    while True:
        # cek flag untuk dari slider
        response = requests.get("http://localhost:8000/get_flag_slider")

        if response.status_code == 200:
            data = response.json()
            flag_main = data.get("flag")

            if flag_main == 1 and not camera_opened:
                # Buka kamera hanya jika belum dibuka
                cap = cv2.VideoCapture(0)
                camera_opened = True

            if flag_main == 0 and camera_opened:
                # Tutup kamera hanya jika sudah dibuka
                cap.release()
                camera_opened = False

            if flag_main == 1:
                while True:
                    response_get = requests.get("http://localhost:8000/get_flag_rendah")
                    data_get = response_get.json()
                    get_flag = data_get.get("flag")

                    ret, frame = cap.read()

                    Cur_blur = detect_blur_live_stream_laplacian(frame)
                    cv2.putText(frame, "Tingkat ketajaman: {0:.2f}".format(Cur_blur), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    print("Fokus rendah sedang berjalan")

                    action_text, direction, Prev_blur = Fokus_rendah(Cur_blur, Prev_blur)
                    last_send_time = kirim_flag_fokus_rendah(direction, last_send_time, interval)

                    cv2.putText(frame, action_text, (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                    cv2.imshow("Live stream", frame)
                    print("nilai flag :", get_flag)

                    if get_flag == 0:
                        while True:
                            ret, frame = cap.read()
                            response1_get = requests.get("http://localhost:8000/get_flag_tinggi")

                            data_get1 = response1_get.json()
                            get_flag1 = data_get1.get("flag")

                            Cur_blur1 = detect_blur_live_stream_laplacian(frame)
                            cv2.putText(frame, "Tingkat ketajaman: {0:.2f}".format(Cur_blur1), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                            print("Fokus tinggi sedang berjalan")
                            action_text1, direction1, Prev_blur1 = Fokus_tinggi(Cur_blur1, Prev_blur1)
                            last_send = kirim_flag_fokus_tinggi(direction1, last_send_time, interval1)
                            cv2.putText(frame, action_text1, (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                            cv2.imshow("Live stream", frame)
                            print("nilai flag :", get_flag1)

                            if get_flag1 == 0:
                                #reset flag slider kembali ke 0
                                subprocess.run(["coba.bat"])
                                flag_main = 0
                                reset_flag_result = reset_flag(flag_main, last_send_time, interval=1)
                                cap.release()
                                cv2.destroyAllWindows()
                                break
                    break
            else:
                print("Menunggu perintah")

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()