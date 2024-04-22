from hx711_calibrate import Calibration
import time

calibration = Calibration(CALIBRATION_FILE='calibration_data.txt')
while True:
    print(f" weight: {calibration.get_weight()} grams")
    time.sleep(0.8)