import subprocess
import time
import pyautogui

# pyautogui.hotkey("win")
# time.sleep(2)
# pyautogui.write("camera")
# time.sleep(2)
# pyautogui.press("f7")
# Wait for the camera app to open (adjust the sleep duration if needed)
time.sleep(5)

# Capture an image (assuming the camera app supports taking photos)
# Mengambil screenshot seluruh layar
screenshot = pyautogui.screenshot()

# Simpan screenshot dengan nama file tertentu
file_name = "screenshot.png"
screenshot.save(file_name)

exit()