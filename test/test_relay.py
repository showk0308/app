from gpiozero import OutputDevice, DigitalOutputDevice, OutputDeviceError  # Import the class for controlling GPIO pins
from time import sleep  # Import the sleep function for delay

# Initialize the relay connected to GPIO pin 17, starting in the 'off' state
# relay_1 = OutputDevice(17, initial_value=False)
# relay_2 = OutputDevice(27, initial_value=False)
relay_1 = DigitalOutputDevice(pin=17)
relay_2 = DigitalOutputDevice(pin=27)

def test_relay():
    """gpiozeroを使うと、なぜかテンポラリファイルが作成されてしまう。
    このファイルを含んだまま、WinSCPでバックアップをとると、このファイルのところで通信切断してしまい、コピーに失敗する。
    そのため、このライブラリは使わないことにする
    """
    assert do_relay()

def do_relay() -> bool:
    try:
        # Loop to continuously toggle the relay's state every second
        print('Relay_1 open...')  # Inform that the relay is being activated
        relay_1.on()  # Turn on the relay (assuming active low configuration)
        sleep(1)   # Maintain the relay in the on state for 1 second

        print('Relay_2 open...')  # Inform that the relay is being activated
        relay_2.on()  # Turn on the relay (assuming active low configuration)
        sleep(1)   # Maintain the relay in the on state for 1 second

        print('...Relay_1 close')  # Inform that the relay is being deactivated
        relay_1.off()  # Turn off the relay
        sleep(1)   # Maintain the relay in the off state for 1 second

        print('...Relay_2 close')  # Inform that the relay is being deactivated
        relay_2.off()  # Turn off the relay
        sleep(1)   # Maintain the relay in the off state for 1 second

        return True

    except OutputDeviceError as e:
        print(f'exception msg:{e}')
    except KeyboardInterrupt:
        # Handle a keyboard interrupt (Ctrl+C) to exit the loop
        relay_1.off()  # Ensure the relay is turned off before exiting
        relay_2.off()  # Ensure the relay is turned off before exiting
        return False
    
