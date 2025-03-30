import gpiod
import time

from gpiod.line import Direction, Value

def chips_info():
    """List all GPIO chips and their lines."""
    # List all GPIO chips
    for chip in gpiod.ChipIter():
        print(chip.name())
        chip.close()
    # for chip in gpiod.list_chips():
    #     print(f"Chip Name: {chip.name}")
    #     print(f"Chip Number: {chip.number}")
    #     print(f"Number of Lines: {chip.num_lines}")
    #     print("Lines:")
    #     for line in chip.get_lines():
    #         print(f"  Line Number: {line.offset}")
    #         print(f"  Line Name: {line.name}")
    #         print(f"  Line Flags: {line.flags}")
    #         print(f"  Line Consumer: {line.consumer}")
    #         print()

def get_chip_info(chip_path):
    with gpiod.Chip(chip_path) as chip:
        info = chip.get_info()
        print("{} [{}] ({} lines)".format(info.name, info.label, info.num_lines))

def toggle_value(value):
    if value == Value.INACTIVE:
        return Value.ACTIVE
    return Value.INACTIVE


def toggle_line_value(chip_path, line_offset):
    value_str = {Value.ACTIVE: "Active", Value.INACTIVE: "Inactive"}
    value = Value.ACTIVE

    with gpiod.request_lines(
        chip_path,
        consumer="toggle-line-value",
        config={
            line_offset: gpiod.LineSettings(
                direction=Direction.OUTPUT, output_value=value
            )
        },
    ) as request:
        while True:
            print("{}={}".format(line_offset, value_str[value]))
            time.sleep(1)
            value = toggle_value(value)
            request.set_value(line_offset, value)




# if __name__ == "__main__":
#     try:
#         get_chip_info("/dev/gpiochip0")
#     except OSError as ex:
#         print(ex, "\nCustomise the example configuration to suit your situation")
def ptest_chips_info():
    """Test function to print GPIO chips information."""
    get_chip_info("/dev/gpiochip4")
    assert True
    
def ptest_toggle_line_value():
    """Test function to toggle GPIO line value."""
    toggle_line_value("/dev/gpiochip0", 14)
    assert True

LINE = 21

def request_lines_1():
    with gpiod.request_lines(
        "/dev/gpiochip4",
        consumer="blink-example",
        config={
            LINE: gpiod.LineSettings(
                # direction=Direction.OUTPUT, output_value=Value.INACTIVE
                direction=Direction.OUTPUT, output_value=Value.ACTIVE
            )
        },
    ) as request:
        request.set_value(LINE, Value.ACTIVE)
        time.sleep(10)
        request.set_value(LINE, Value.INACTIVE)
        # while True:
        #     request.set_value(LINE, Value.ACTIVE)
        #     time.sleep(1)
        #     request.set_value(LINE, Value.INACTIVE)
        #     time.sleep(1)

def request_lines(line_no: int) -> object:
    return gpiod.request_lines(
        "/dev/gpiochip4",
        consumer="blink-example",
        config={
            line_no: gpiod.LineSettings(
                # direction=Direction.OUTPUT, output_value=Value.INACTIVE
                direction=Direction.OUTPUT, output_value=Value.ACTIVE
            )
        },
    )

def test_request_lines():
    """Test function to request GPIO lines."""

    request = request_lines(LINE)

    request.set_value(LINE, Value.ACTIVE)
    time.sleep(10)
    request.set_value(LINE, Value.INACTIVE)

    assert True
