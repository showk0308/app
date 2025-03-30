import gpiod
from actuators.irrigation.irrigation_data import IrrigationLine
from actuators.irrigation.base_irrigator import Irrigator

class IrrigatorLine2(Irrigator):
    """潅水ライン２クラス

    Args:
        Irrigator (Irrigator): 潅水ラインベースクラス
    """
    def __init__(self, id) -> None:
        """初期化処理

        Args:
            id (str): 潅水ラインID
        """        
        super().__init__(id)

        self.current_line = IrrigationLine(
            line_no=2, 
            busy=False,
            gpio_no=22)
        
        # 潅水ライン2 ラズパイ 15番ピン(GPIO22) - SSR IN4
        # chip = gpiod.Chip('gpiochip4', gpiod.Chip.OPEN_BY_NAME)
        # self.current_line.target = chip.get_line(22)
        # self.current_line.target.request(consumer='in_4', type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
        # chip = gpiod.Chip('/dev/gpiochip4')
        # self.current_line.target = chip.get_line(27)
        # self.current_line.target = chip
        # self.current_line.gpio_no = 27


