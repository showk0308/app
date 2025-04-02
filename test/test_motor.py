import gpiod
from time import sleep
# import gpiozero
# pin = gpiozero.DigitalOutputDevice(pin=23)
# try:
#     while True:
#         pin.on()
#         sleep(1)
#         pin.off()
#         sleep(1)
# finally:
#     pin.close() 
chip = gpiod.Chip('gpiochip4', gpiod.Chip.OPEN_BY_NAME)

# ラズパイ 16番ピン(GPIO23) - モータードライバー 5番(IN1)
# ラズパイ 18番ピン(GPIO24) - モータードライバー 6番(IN2)
in_1 = chip.get_line(23)
in_1.request(consumer='in_1', type=gpiod.LINE_REQ_DIR_OUT)
in_2 = chip.get_line(24)
in_2.request(consumer='in_2', type=gpiod.LINE_REQ_DIR_OUT)

def test_relay():
    assert do_relay()

def do_relay() -> bool:
    try:
        print('rotation on...')
        in_1.set_value(1)
        in_2.set_value(0)
        sleep(3)

        print('stop rotation...')
        in_1.set_value(0)
        in_2.set_value(0)
        sleep(5)

        print('rotation reverse...')
        in_1.set_value(0)
        in_2.set_value(1)
        sleep(2)

        print('stop rotation...')
        in_1.set_value(0)
        in_2.set_value(0)
        sleep(1)

        in_1.release()
        in_2.release()

        return True

    except KeyboardInterrupt:
        # Handle a keyboard interrupt (Ctrl+C) to exit the loop
        in_1.release()
        in_2.release()

        return False
    
