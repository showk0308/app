import asyncio
import gpiod
from time import sleep
from contextlib import contextmanager
from models.actuator_models import EnvironmentValues as ev
from database.db_access import get_session
from actuators.base_actuators.base_actuator import Actuator
from actuators.base_actuators.calc_aperture import \
    get_degrees_apertures, \
    condition_judgement, \
    on_off_condition_judgement
from config import settings
from gpiod.line import Value

class CirculatorFan(Actuator):
    def __init__(self, id) -> None:
        """初期化処理

        Args:
            id (_str_): 対象制御装置ID
        """
        super().__init__(id)
        self.actuator_state=self.PAUSED
        self.circulator_busy = True    # 循環扇稼働状態 True-> 回転中

    def init_gpio(self):
        """gpio初期化
        """
        # chip = gpiod.Chip('gpiochip4', gpiod.Chip.OPEN_BY_NAME)
        # # ラズパイ 17番ピン(GPIO17) IN1
        # self.relay_1 = chip.get_line(17)
        # self.relay_1.request(consumer='relay_1', type=gpiod.LINE_REQ_DIR_OUT)
        self.circulator = super().request_lines(17, Value.INACTIVE)

    def rotation_state(self, action: int):
        """循環扇の回転状態を設定する
        Args:
            action (int): Value.ACTIVE:ON, Value.INACTIVE:OFF
        """
        self.circulator.set_value(17, action)

    async def turn_on(self):
        """循環扇オン

        Args:
            rotation_time (float): 回転時間
        """
        try:
            if not self.circulator_busy:
                print('Relay_1 open...')
                # self.relay_1.set_value(1)
                self.rotation_state(Value.ACTIVE)
                self.circulator_busy = True

            await asyncio.sleep(1)

        except OSError as ex:
            print(f'{ex}')

    async def turn_off(self):
        """循環扇オフ
        """
        try:
            if self.circulator_busy:
                print('Relay_1 close...')
                # self.relay_1.set_value(0)
                self.rotation_state(Value.INACTIVE)
                self.circulator_busy = False

            await asyncio.sleep(1)

        except OSError as ex:
            print(ex)

    def get_environment_values(self) -> float:
        """environment_valuesテーブルから、
        現在の環境計測値（温度）を取得する

        Returns:
            float: 現在計測温度
        """
        with get_session() as db:
            environments = db.query(ev).first()

        return environments.temperature

    def get_toggle_mode(self, now_temp: float) -> bool:
        """循環扇オンオフ状態を取得する

        Args:
            now_temp (float): 現在の温度

        Returns:
            bool: True:オン, False:オフ
        """
        stg = []
        aptr = []
        for _, stages, apertures in get_degrees_apertures(self.id):
            stg = [x for x in stages if (x is not None) and (x != '')]
            aptr = [x for x in apertures if (x is not None) and (x != '')]

        # stg:[28.0, 30.0]
        # aptr:[1.0, 1.0]
        return on_off_condition_judgement(now_temp, stg, 0, aptr)
        # return not condition_judgement(temp, stg, 0, aptr, 1)

    async def task(self,  *args):
        """循環扇の制御を実行する
        """
        print(f'circulator task args:{args}')

        self.init_gpio()

        while True:
            try:
                # environment_valuesテーブルから、現在の環境計測値（温度）を取得する
                temp = self.get_environment_values()
                print(f'circulator task / now temperature:{temp}')

                self.actuator_state = await self.get_actuator_state()
                print(f'circulator state:{self.actuator_state=}')

                # 循環扇オンオフ状態を取得する
                turn_mode = self.get_toggle_mode(temp)
                print(f'{turn_mode =}')
                if turn_mode and self.actuator_state == settings.ACTUATOR_AUTO:
                    await self.turn_on()

                elif not turn_mode and self.actuator_state == settings.ACTUATOR_AUTO:
                    await self.turn_off()

                elif self.actuator_state == settings.ACTUATOR_FORCED_OPEN:
                    await self.turn_on()

                elif self.actuator_state == settings.ACTUATOR_FORCED_CLOSE:
                    await self.turn_off()

                elif self.actuator_state == settings.ACTUATOR_STOPPED:
                    await self.turn_off()

                else:
                    await asyncio.sleep(1)

            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")

            sleep(1)
