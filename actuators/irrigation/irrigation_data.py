import gpiod
from dataclasses import dataclass

@dataclass
class IrrigationLine:
    line_no: int = -1       # 潅水ライン番号
    chip_path: str = '/dev/gpiochip4'   # gpiod.Chip.path
    busy: bool = False      # ライン使用中フラグ
    done_time: str = ''     # 直近潅水完了時刻
    gpio_no: int = -1       # GPIO番号

    def is_done(self, done_time: str) -> bool:
        return self.done_time == done_time

