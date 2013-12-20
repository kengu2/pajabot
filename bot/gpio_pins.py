import RPi.GPIO as GPIO

# RPi GPIO pin stuff (NOT USED ATM)

class GpioPins():
        def __init__(self):
                self.doorpin = 11
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.doorpin, GPIO.IN)
                self.doorStatus = GPIO.input(self.doorpin)

	def pollPins(self)
                newDs = GPIO.input(self.doorpin)
                if newDs is not self.doorStatus:
                    self.doorStatus = newDs
                    self.sayDoorStatus()

	def close(self):
		GPIO.cleanup()

