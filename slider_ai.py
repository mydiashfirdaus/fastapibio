import RPi.GPIO as GPIO
from time import sleep
from RpiMotorLib import RpiMotorLib
import requests
import json

dirr, step = 20, 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(dirr, GPIO.OUT)
GPIO.setup(step, GPIO.OUT)
GPIO.setup(23, GPIO.IN)
GPIO.setup(24, GPIO.IN)

i, pos_max, pos_min, direction = 0, 0, 0, 0

limit_r = GPIO.input(23)
limit_l = GPIO.input(24)

setting_API = ''

current_pos = 0
prev_pos = 0

### Kalibrasi Slider

for i in range(100000):
    if (limit_l == 0):
        GPIO.output(dirr, direction) # set value untuk pin dir
        GPIO.output(step, 1) # set value high untuk pin step
        GPIO.output(step, 0) # set value low untuk pin step
        i += 1
    else:
        i = 100001

i, direction = 0, 1

for i in range(100000):
    if (limit_r == 0):
        GPIO.output(dirr, direction) # set value untuk pin dir
        GPIO.output(step, 1) # set value high untuk pin step
        GPIO.output(step, 0) # set value low untuk pin step
        i += 1
        pos_max = i
    else:
        i = 100001

ranges = pos_max - pos_min
distance = ranges / 2
t = distance / 2

reg_1 = pos_min + t
reg_2 = reg_1 + distance
reg_3 = reg_2 + distance
reg_4 = reg_3 + distance
reg_5 = reg_4 + distance
regions = [reg_1, reg_2, reg_3, reg_4, reg_5]

## Flow 
while True:
    ## Request API
    get_data = requests.get(setting_API)
    datas = json.loads(get_data)

    ## Parsing Data
    run_status = datas['run']
    steps = datas['step']
    delays = datas['delay']
    reg = datas['regions']
    modes = datas['mode']
    multiregion = datas['multiregion']

    direction = 0
    temp = 1

    if (run_status == 1):   ## Jika ada perintah run dari Web
        if (modes == 1): ## Jika Mode Auto
            if (multiregion == 0): ## Jika setting tidak multiregion
                i = 0
                ## Motor jalan 1 step
                if (limit_l == 0 or limit_r == 0): ## Jika limit switch kanan atau kiri tidak ter-trigger
                    GPIO.output(dirr, direction) # set value untuk pin dir
                    GPIO.output(step, 1) # set value high untuk pin step
                    GPIO.output(step, 0) # set value low untuk pin step
                    i += 1
                else:   ## Jika Limit Switch ter-Trigger
                    ## Mengubah direction
                    b = direction
                    direction = temp
                    temp = b
                if (direction == 0):
                    i = i*(-1)
                current_pos = prev_pos + i
                run_status = 0
                ## Tambahkan coding untuk sending posisi slider ke DB
            else:   ## Jika setting multiregion
                z = current_pos
                for y in range(5): ## Akan melakukan pergeseran ke setiap region
                    z = z - regions[y]
                    if (z < 0):
                        direction = 0
                    else:
                        direction = 1
                    i = 0
                    for i in range(z):
                        GPIO.output(dirr, direction) # set value untuk pin dir
                        GPIO.output(step, 1) # set value high untuk pin step
                        GPIO.output(step, 0) # set value low untuk pin step
                        i += 1
                    time.sleep() # waktu delay untuk focusing gambar dan capture gambar
        else: ## Jika mode manual atau region yang ditentukan Web setting
            steps = regions[reg] - current_pos # Mengetahui ke arah mana region yang dituju
            if (steps < 0):
                direction = 0
                steps = steps *(-1)
            else:
                direction = 1
            i = 0
            for i in range(steps):
                GPIO.output(dirr, direction) # set value untuk pin dir
                GPIO.output(step, 1) # set value high untuk pin step
                GPIO.output(step, 0) # set value low untuk pin step
                i += 1
            # tambahkan coding send flag
