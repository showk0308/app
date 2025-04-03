import inspect
from actuators.side_windows.base_side_window import BaseSideWindow
from database.db_access import get_session

class SideWindow1(BaseSideWindow):
    """側窓制御クラス

    Args:
        BaseSideWindow (base_class): 側窓制御基本クラス
    """
    def __init__(self, id: str) -> None:
        """初期化処理

        Args:
            id (str): 側窓ID
        """
        # 側窓はモータードライバを使って制御している
        # モータードライバは2つのGPIOを使って制御する
        # このため、GPIO番号は2つ必要である
        GPIO_NUMBER_COUNT = 2   # GPIO番号の数
        
        try:
            # GPIO番号14, 16を使用
            nos = self.get_gpio_no(id)
            
            if len(nos.gpionos) != GPIO_NUMBER_COUNT:
                raise Exception('Invalid GPIO number count.')
            
            print(f'gpio_no: {nos.gpionos[0].gpio_no}, {nos.gpionos[1].gpio_no}')
            motor_1 = nos.gpionos[0].gpio_no
            motor_2 = nos.gpionos[1].gpio_no

            # get_gpio_no関数で取得したGPIO番号はfloat型なのでint型に変換する必要がある
            # これは、継承元のBaseSideWindowクラスの__init__メソッドの引数がint型であるため
            super().__init__(id, int(motor_1), int(motor_2))
        except Exception as e:
            print(f'Error: {e} at {inspect.currentframe().f_code.co_name} in {inspect.getfile(inspect.currentframe())}')
            raise Exception('Failed to initialize SideWindow1 class.')
            

