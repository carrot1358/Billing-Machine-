from hx711_gpiozero import HX711
from time import sleep

class Calibration:
    def __init__(self,CALIBRATION_FILE = None, init_reading=None, scale_ratio=None):
        self.spi = HX711()

        if(CALIBRATION_FILE is None):
            pass
        else:
            if(isinstance(CALIBRATION_FILE, str)):
                self.CALIBRATION_FILE = CALIBRATION_FILE
            else:
                raise ValueError("Invalid file name")

        if(init_reading is None and scale_ratio is None):
            pass
        else:
           if(isinstance(init_reading, float) and isinstance(scale_ratio, float)):
               self.init_reading = init_reading
               self.scale_ratio = scale_ratio
               self.save_calibration_data(init_reading, scale_ratio)
           else:
               raise ValueError("Invalid calibration data")

        try:
            self.init_reading, self.scale_ratio = self.load_calibration_data()
            print("Calibration data loaded successfully.")
        except FileNotFoundError:
            self.perform_calibration(self.spi)
            self.init_reading, self.scale_ratio = self.load_calibration_data()

    def save_calibration_data(self,init_reading, scale_ratio):
        with open(self.CALIBRATION_FILE, "w") as file:
            file.write(f"Init Reading: {init_reading}\n")
            file.write(f"Scale Ratio: {scale_ratio}\n")

    def load_calibration_data(self):
        try:
            with open(self.CALIBRATION_FILE, "r") as file:
                lines = file.readlines()
                init_reading = float(lines[0].split(":")[1])
                scale_ratio = float(lines[1].split(":")[1])
                return init_reading, scale_ratio
        except FileNotFoundError:
            print("Calibration file not found. Please calibrate first.")
            raise FileNotFoundError

    def perform_calibration(self,spi):
        print("Initiating calibration...")
        init_reading = spi.value
        print("Initial reading:", init_reading)

        sleep(1)
        input("Put a known mass on the scale, then press `enter`.")

        try:
            rel_weight = float(input("What is the weight of the known mass?\n"))
        except ValueError as err:
            print(err)
            print("(The input of weight can only be numbers)")
            exit(1)

        rel_reading = spi.value
        print(f"Relative Weight: {rel_weight}, Relative Reading: {rel_reading}")

        scale_ratio = rel_weight / (rel_reading - init_reading)
        print("Scale Ratio:", scale_ratio)

        self.save_calibration_data(init_reading, scale_ratio)
        print("Calibration data saved successfully.")

    def get_weight(self):
        weight = (self.spi.value - self.init_reading) * self.scale_ratio
        return weight



