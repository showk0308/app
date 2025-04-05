import inspect
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
        try:
            # GPIO番号17を使用
            nos = self.get_gpio_no(id)
            print(f'gpio_no: {nos.gpionos[0].gpio_no}')
            if len(nos.gpionos) != 1:
                raise Exception('Invalid GPIO number count.')

            gpio_no = int(nos.gpionos[0].gpio_no)
    
            super().__init__(id)
        
            self.current_line = IrrigationLine(
                line_no=2, 
                busy=False,
                gpio_no=gpio_no)

        except Exception as e:
            print(f'Error: {e} at {inspect.currentframe().f_code.co_name} in {inspect.getfile(inspect.currentframe())}')
            raise Exception('Failed to initialize IrrigatorLine1 class.')


