import pyautogui
import subprocess
import time
import psutil

while True:
    # Membuka Notepad
    
    subprocess.Popen(['notepad'])

    # Tunggu sebentar untuk memastikan Notepad terbuka sepenuhnya
    time.sleep(2)

    # Menulis "biofarma fase 2" di Notepad
    pyautogui.write("biofarma fase 2")

    # Tunggu sebentar sebelum menutup Notepad
    time.sleep(2)

    # Menutup Notepad
    # pyautogui.hotkey('ctrl', 'w')

    # Tunggu hingga Notepad tertutup
    while True:
        notepad_closed = not any("notepad.exe" in p.name().lower() for p in psutil.process_iter())
        if notepad_closed:
            time.sleep(3)
            break

    # Mengulangi proses dari awal
