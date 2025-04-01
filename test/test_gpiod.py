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

def ptest_request_lines():
    """Test function to request GPIO lines."""

    request = request_lines(LINE)

    request.set_value(LINE, Value.ACTIVE)
    time.sleep(10)
    request.set_value(LINE, Value.INACTIVE)

    assert True


GPIO_NO = 21

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
        request.set_value(GPIO_NO, Value.ACTIVE)
        time.sleep(10)
        request.set_value(GPIO_NO, Value.INACTIVE)

curtain_busy = False
def forward_rotation_state(gpio_no: int, action: int):
    """順回転方向モータ設定

    Args:
        action (int): モータードライバーの状態
            Value.ACTIVE:順回転作動
            Value.INACTIVE:順回転停止
    """
    # self.in_1.set_value(1)
    global curtain_busy
    if not curtain_busy:
        curtain_busy = True

        with gpiod.request_lines(
            "/dev/gpiochip4",
            consumer="curtains-no",
            config={
                gpio_no: gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=Value.ACTIVE
                )
            },
        ) as request:
            request.set_value(gpio_no, action)

        # with self.in_1 as request:
        #     request.set_value(self.motor_1_gpio, action)

def reverse_rotation_state(gpio_no: int, action: int):
    """逆回転方向モータ設定
    Args:
        action (int): モータードライバーの状態
            Value.ACTIVE:逆回転作動
            Value.INACTIVE:逆回転停止
    """
    # self.in_1.set_value(1)
    global curtain_busy
    if not curtain_busy:
        curtain_busy = True

        with gpiod.request_lines(
            "/dev/gpiochip4",
            consumer="curtains-no",
            config={
                gpio_no: gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=Value.ACTIVE
                )
            },
        ) as request:
            request.set_value(gpio_no, action)

def   request_line():
    # GPIOチップのインスタンス作成
    chip = gpiod.Chip("/dev/gpiochip0")  # ファイルパスで指定

    # ラインを取得（複数ラインが必要でない場合もチェック）
    # lines = chip.get_info()
    lines = chip.get_line_info(20)
    print(lines)
    assert True

def get_line(gpio_no:int) -> object:
    chip = gpiod.Chip('/dev/gpiochip0') #GPIOチップの指定
    return chip, chip.request_lines(config={
        gpio_no: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.ACTIVE
        )
    })
    
def test_request_line():
# ラインのリクエスト※Version1.6.3のAPI
    chip, line = get_line(20) #ラインの取得
    line.set_value( 20, Value.INACTIVE) #出力=1(電源ON)
    line.set_value( 20, Value.ACTIVE) #出力=1(電源ON)
    time.sleep(5) #5秒待つ
    line.set_value(20, Value.INACTIVE) #出力=0(電源OFF)
    # print(f'{chip.watch_line_info(20)}')
 
    # line.request(
    #         consumer="my-gpiod-app", #アプリケーション名
    #         type=gpiod.LINE_REQ_DIR_OUT, #出力
    #         flags=0 #フラグ
    #     )

    # line.set_value(1) #出力=1(電源ON)
    # time.sleep(1) #1秒待つ
    # line.set_value(0) #出力=0(電源OFF)

    # line.release() #ラインのリリース
    # chip.close() #チップのクローズ

    """Test function to request GPIO line."""
    # forward_rotation_state(20, Value.ACTIVE)
    # time.sleep(5)
    # forward_rotation_state(20, Value.INACTIVE)
    # reverse_rotation_state(21, Value.INACTIVE)

    # forward_rotation_state(20, Value.ACTIVE)
    # time.sleep(5)
    # forward_rotation_state(20, Value.INACTIVE)
    # reverse_rotation_state(20, Value.INACTIVE)

    # request_lines_1()
    assert True
