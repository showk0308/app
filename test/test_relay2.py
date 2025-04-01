import gpiod
from time import sleep
 
chip = gpiod.Chip('gpiochip4', gpiod.Chip.OPEN_BY_NAME)

# relay_1 = OutputDevice(17, initial_value=False)
# relay_2 = OutputDevice(27, initial_value=False)
relay_1 = chip.get_line(17)
# relay_2 = chip.get_line(27)
relay_1.request(consumer='relay_1', type=gpiod.LINE_REQ_DIR_OUT)
# relay_2.request(consumer='relay_2', type=gpiod.LINE_REQ_DIR_OUT)

def test_relay():
    assert do_relay()

def do_relay() -> bool:
    try:
        print('Relay_1 open...')
        relay_1.set_value(1)
        sleep(20)

        print('relay_1 close...')
        relay_1.set_value(0)
        sleep(1)

        # print('...relay_2 open')
        # relay_2.set_value(1)
        # sleep(1)

        # print('...relay_2 close')
        # relay_2.set_value(0)
        # sleep(1)

        return True

    except KeyboardInterrupt:
        # Handle a keyboard interrupt (Ctrl+C) to exit the loop
        relay_1.release()
        # relay_2.release()

        return False
    
