
class GPIODriverBase:
    OUT = None
    IN = None
    HIGH = None
    LOW = None

    @staticmethod
    def output(pin, state):
        raise NotImplementedError

    @staticmethod
    def cleanup():
        raise NotImplementedError

    @staticmethod
    def set_mode(pin, mode, initial=None):
        raise NotImplementedError

    @staticmethod
    def initialize():
        raise NotImplementedError

def get_gpio_driver(platform):
    if platform == 'rpi':
        import RPi.GPIO as GPIO
        class GPIODriver(GPIODriverBase):
            OUT = GPIO.OUT
            IN = GPIO.IN
            HIGH = GPIO.HIGH
            LOW = GPIO.LOW

            @staticmethod
            def output(pin, state):
                GPIO.output(pin, state)

            @staticmethod
            def cleanup():
                GPIO.cleanup()

            @staticmethod
            def set_mode(pin, mode, initial=None):
                GPIO.setup(pin, mode, initial=initial)

            @staticmethod
            def initialize():
                GPIO.setmode(GPIO.BCM)

    elif platform == 'opi':
        import wiringpi
        class GPIODriver(GPIODriverBase):
            OUT = 1
            IN = 0
            HIGH = 1
            LOW = 0

            @staticmethod
            def output(pin, state):
                wiringpi.digitalWrite(pin, state)

            @staticmethod
            def cleanup():
                pass  # No cleanup required for wiringpi

            @staticmethod
            def set_mode(pin, mode, initial=None):
                wiringpi.pinMode(pin, mode)
                if initial is not None:
                    wiringpi.digitalWrite(pin, initial)

            @staticmethod
            def initialize():
                wiringpi.wiringPiSetup()

    elif platform == 'jetson':
        import Jetson.GPIO as GPIO
        class GPIODriver(GPIODriverBase):
            OUT = GPIO.OUT
            IN = GPIO.IN
            HIGH = GPIO.HIGH
            LOW = GPIO.LOW

            @staticmethod
            def output(pin, state):
                GPIO.output(pin, state)

            @staticmethod
            def cleanup():
                GPIO.cleanup()

            @staticmethod
            def set_mode(pin, mode, initial=None):
                GPIO.setup(pin, mode, initial=initial)

            @staticmethod
            def initialize():
                GPIO.setmode(GPIO.BOARD)

    else:
        raise ValueError("Unsupported platform")

    return GPIODriver
