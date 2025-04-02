import asyncio
import gpiod
from contextlib import contextmanager
from requests import Session
from database.db_access import get_session
from models.actuator_models import EnvironmentValues as ev, ActuatorStates as ast
from gpiod.line import Direction, Value


class Actuator:
    def __init__(self, id) -> None:
        self.PAUSED = "_pause_"   # 停止中
        self.state = self.PAUSED
        self.id = id  # 自分自身のID

    # プロパティの値を取り出すメソッドを定義する
    @property
    def actuator_state(self):
        return self.state

    # プロパティの値を設定
    @actuator_state.setter
    def actuator_state(self, value):
        self.state = value

    def task(self, *args):
        """クラス独自の動作をおこなう
        継承先でこの関数をoverrideする
        """
        pass

    def get_interval(self):
        """計測間隔を取得する
        ActuatorStates(actuator_states)テーブルから取得する
        """
        pass

    def execute(self, *args):
        """制御装置（デバイス）を作動させる
        継承先でこの関数をoverrideする
        """
        pass

    def get_environment_values(self) -> float:
        """environment_valuesテーブルから、
        現在の環境計測値（温度、湿度等）を取得する

        Returns:
            float: 現在計測照度
        """
        with get_session() as db:
            environments = db.query(ev).first()

        return environments.lux
    
    def get_environment_temperature(self) -> float:
        """environment_valuesテーブルから、
        現在の環境計測値（温度）を取得する

        Returns:
            float: 現在計測温度
        """
        with get_session() as db:
            environments = db.query(ev).first()

        return environments.temperature
    
    def update_aperture(self, aperture = 0) :
        """指定した開度をactuator_statesテーブルへ更新する
        テーブル:actuator_states

        Args:
            aperture (int, optional): 開度. 0 to 100.
        """
        with get_session() as db:
            filtered = db.query(ast).filter(ast.actuator_id == self.id).first()

            if filtered is not None:
                #print(f'update_aperture.new aperture:{aperture}')
                filtered.aperture = aperture
                #db.flush() 
                db.commit()

        # await asyncio.sleep(1)

    async def get_actuator_state(self):
        with get_session() as db:
            filtered = db.query(ast).filter(ast.actuator_id == self.id).first()
            await asyncio.sleep(1)
            
            if filtered is not None:
                return filtered.state
            else:
                raise ValueError('指定したIDを持つ制御機器はactuator_statesテーブルには登録されていません。')

    def request_lines(self, gpio_no: int) -> object:
        """
        GPIOライン(gpioinfoコマンドで表示されるline番号：GPIO番号に1対1で対応)をリクエストするためのメソッド。

        指定されたGPIO番号に基づいて、GPIOラインをリクエストし、
        出力方向とアクティブな出力値を設定します。

        Args:
            gpio_no (int): リクエストするGPIOラインの番号。

        Returns:
            object: リクエストされたGPIOラインのオブジェクト。

        Note:
            このメソッドは、/dev/gpiochip4 デバイスを使用してGPIOラインをリクエストします。
        """
        chip = gpiod.Chip('/dev/gpiochip0') #GPIOチップの指定
        
        return chip.request_lines(config={
            gpio_no: gpiod.LineSettings(
                direction=Direction.OUTPUT, output_value=Value.ACTIVE
            )
        })

        # return gpiod.request_lines(
        #     "/dev/gpiochip4",
        #     consumer="curtains-no",
        #     config={
        #         gpio_no: gpiod.LineSettings(
        #             direction=Direction.OUTPUT, output_value=state
        #         )
        #     },
        # )

    def set_line(self, gpio_no: int, action: Value) -> object:
        """
        指定されたGPIOピンに対してアクションを設定します。

        Args:
            gpio_no (int): 操作対象のGPIOピン番号。
            action (Value): 設定するアクションの値。通常はValue.ACTIVEまたはValue.INACTIVE。

        Returns:
            object: 操作の結果を表すオブジェクト。

        使用例:
            set_line(17, Value.ACTIVE)

        注意:
            この関数は/dev/gpiochip4を使用してGPIOピンを操作します。
            適切な権限が必要です。
        """

        with gpiod.request_lines(
            "/dev/gpiochip4",
            consumer="action-motor",
            config={
                gpio_no: 
                gpiod.LineSettings(
                    direction=Direction.OUTPUT, 
                    output_value=Value.ACTIVE)},
        ) as request:
            request.set_value(gpio_no, action)

