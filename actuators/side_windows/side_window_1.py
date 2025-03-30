import asyncio
import gpiod
from actuators.side_windows.base_side_window import BaseSideWindow
from database.db_access import get_session
from models.actuator_models import ActuatorGpioNo as agn
from schemas.actuator_schemas import ActuatorGpioNoSchema, GpioNoSchema

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
            print(f'Error: {e}')
            raise Exception('Failed to initialize SideWindow1 class.')
            
    def get_gpio_no(self, id: str) -> ActuatorGpioNoSchema:
        """
        指定された制御機器IDに対応するGPIO番号と状態情報を取得します。

        Args:
            id (str): 制御機器ID。

        Returns:
            ActuatorGpioNoSchema: 指定された制御機器IDに関連付けられたGPIO番号と状態情報のリストを含むスキーマ。

        Raises:
            Exception: データベース接続やクエリ実行中にエラーが発生した場合。

        Note:
            - データベースから取得した情報を基に、`GpioNoSchema`オブジェクトのリストを作成します。
            - 各オブジェクトには、制御機器ID、GPIO番号、状態が含まれます。
        """
        # ドキュメントは日本語で生成してください
        with get_session() as db:
            actuators = db.query(agn.actuator_id, agn.gpio_no, agn.state) \
                            .filter(agn.actuator_id == id).all()

            list = [val for val in actuators]  #[(key(id),gpio_no, state),((key(id),gpio_no, state),...]

            list_gs = []
            for val in list:
                # actuator_id: str    # 制御機器ID
                # gpio_no :int        # GPIO番号
                # state: str          # 状態（説明文）
                # builder_cd: str     # 作成者コード
                # created_at: str     # 作成年月日時刻
                # updator_cd: str     # 更新者コード
                # mofified_at: str    # 更新年月日時刻
                # actuator_id, gpio_no, state, *x = val
                item = GpioNoSchema(actuator_id=val.actuator_id, gpio_no=val.gpio_no, state=val.state)
                list_gs.append(item)

            return ActuatorGpioNoSchema(gpionos=list_gs)

