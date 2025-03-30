import asyncio
import gpiod
from time import sleep

import requests
# from contextlib import contextmanager
# from fastapi import Depends
# import requests
# from sqlalchemy import select, insert, update, delete
# from sqlalchemy.engine import Result
from actuators.base_actuators.calc_aperture import get_aperture
from actuators.base_actuators.base_actuator import Actuator
from config import settings
from gpiod.line import Value


class BlackoutCurtain(Actuator):
    """遮光カーテン制御

    Base Class:
        Actuator (base_actuator.py)
    """
    def __init__(self, id: str) -> None:
        super().__init__(id)

        self.actuator_state = settings.ACTUATOR_STOPPED
        self.newest_aperture = 0
        self.curtain_busy = False   # 光の強弱にかかわらず起動直後カーテン制御する

    def init_gpio(self):
        # chip = gpiod.Chip('gpiochip4', gpiod.Chip.OPEN_BY_NAME)

        # # ラズパイ 16番ピン(GPIO23) - モータードライバー 5番(IN1)
        self.in_1 = super().request_lines(23)
        # self.in_1 = chip.get_line(23)
        # self.in_1.request(consumer='in_1', type=gpiod.LINE_REQ_DIR_OUT, default_val=0)

        # # ラズパイ 18番ピン(GPIO24) - モータードライバー 6番(IN2)
        self.in_2 = super().request_lines(24)
        # self.in_2 = chip.get_line(24)
        # self.in_2.request(consumer='in_2', type=gpiod.LINE_REQ_DIR_OUT)

    def forward_rotation_state(self, action: int):
        """順回転方向モータ設定

        Args:
            action (int): モータードライバーの状態
                Value.ACTIVE:順回転作動
                Value.INACTIVE:順回転停止
        """
        # self.in_1.set_value(1)
        print(f'forward_rotation_state.....')
        self.in_1.set_value(23, action)
        
    def reverse_rotation_state(self, action: int):
        """逆回転方向モータ設定
        Args:
            action (int): モータードライバーの状態
                Value.ACTIVE:逆回転作動
                Value.INACTIVE:逆回転停止
        """
        # self.in_1.set_value(1)
        print(f'reverse_rotation_state.....')
        self.in_2.set_value(24, action)
        
    def stop_curtain(self):
        """回転を停止する
        """
        print('stop rotation...')
        self.curtain_busy = False

        # self.in_1.set_value(0)
        self.forward_rotation_state(Value.INACTIVE)
        # self.in_2.set_value(0)
        self.reverse_rotation_state(Value.INACTIVE)

        # self.in_1.release()
        # self.in_2.release()
    
    def forced_stop(self):
        """カーテンが回転していれば、強制的に停止させる
        """
        if self.curtain_busy:
            self.stop_curtain()
    
    async def open_curtain(self, unit_time: float, new_aperture: float, aperture: float):
        """  遮光カーテンを開ける
            new_aperture > aperture

        Args:
            unit_time (float): 開度１％増やすための単位時間
            new_aperture (float): 最終的に設定する開度
            aperture (float): 現在の開度
        """
        try:
            self.init_gpio()
            # openning_time = (new_aperture - aperture) * unit_time
            # print(f'open_curtain... rot time:{openning_time}')
            # self.in_1.set_value(1)
            # self.in_2.set_value(0)
            self.forward_rotation_state(Value.ACTIVE)
            self.reverse_rotation_state(Value.INACTIVE)

            await self.increase_aperture(new_aperture, aperture, unit_time)
        except OSError as ex:
            print(f'{ex}')
        finally:
            self.stop_curtain()
    
    async def increase_aperture(self, new_aperture: float, aperture: float, unit_time: float) -> float:
        """自動運転での、遮光カーテンオープン

        Args:
            unit_time (float): 開度１％を減じるための単位時間
            new_aperture (float): 最終的に設定する開度
            aperture (float): 現在の開度

        Returns:
            float: _description_
        """
        print(f'before: now:{aperture=}, new:{new_aperture}')
        while aperture < new_aperture:
            self.actuator_state = await self.get_actuator_state()
            if self.actuator_state != settings.ACTUATOR_AUTO:
                # print(f'increase updated:{aperture}')
                break;

            lux = self.get_environment_values()
            # 現在の照度から、更新すべき新しい開度を取得する
            new_aperture = get_aperture(self.id, lux, aperture)

            aperture += 1
            self.newest_aperture = aperture
            # print(f'increase:{aperture=}')
            self.update_aperture(aperture)
            await asyncio.sleep(int(unit_time))

    async def close_curtain(self, unit_time: float, new_aperture: float, aperture: float):
        """  遮光カーテンを閉じる
            new_aperture < aperture

        Args:
            unit_time (float): 開度１％を減じるための単位時間
            new_aperture (float): 最終的に設定する開度
            aperture (float): 現在の開度
        """
        closing_time = (aperture - new_aperture) * unit_time
        try:
            self.init_gpio()
            # print(f'close_curtain... rot time:{closing_time}')
            # self.in_1.set_value(0)
            # self.in_2.set_value(1)

            self.forward_rotation_state(Value.INACTIVE)
            self.reverse_rotation_state(Value.ACTIVE)

            await self.decrease_aperture( new_aperture, aperture, unit_time)
        except OSError as ex:
            print(f'{ex}')
        finally:
            self.stop_curtain()

    async def decrease_aperture(self, new_aperture:float, aperture: float, unit_time: float):
        """自動運転での、遮光カーテンクローズ

        Args:
            aperture (float): 現在開度
            new_aperture (float): 設定開度
            full_opening_times (float): 全開時間
        """
        print(f'before: now:{aperture=}, new:{new_aperture}')
        # url = 'http://192.168.10.4:5000/aperture_steps'

        while aperture > new_aperture:
            self.actuator_state = await self.get_actuator_state()
            if self.actuator_state != settings.ACTUATOR_AUTO:
                # print(f'decrease updated:{aperture}')
                break;

            lux = self.get_environment_values()
            # 現在の照度から、更新すべき新しい開度を取得する
            new_aperture = get_aperture(self.id, lux, aperture)

            aperture -= 1
            self.newest_aperture = aperture
            # response = requests.get(url, params={'step':str(aperture)})

            # print(f'decrease:{aperture=}')
            self.update_aperture(aperture)
            await asyncio.sleep(int(unit_time))

    async def execute_forced_open(self, aperture: float, full_opening_times: float):
        """強制的に遮光カーテンを開く

        Args:
            aperture (float): _description_
            full_opening_times (float): _description_
        """
        # print(f'forced open before: now:{aperture=}')
        if aperture == 100:
            return

        # 開度１％時間
        unit_time = full_opening_times / 100

        try:
            if not self.curtain_busy:
                self.curtain_busy = True
                self.init_gpio()
                # print(f'forced open_curtain')
                # self.in_1.set_value(1)
                # self.in_2.set_value(0)
                self.forward_rotation_state(Value.ACTIVE)
                self.reverse_rotation_state(Value.INACTIVE)

            await self.forced_open(aperture, unit_time)
            
        except OSError as ex:
            print(f'{ex}')
        finally:
            if self.curtain_busy:
                self.stop_curtain()

    async def forced_open(self, aperture: float, unit_time: float):
        """開度が100%になるまで、開度を増やし、その値をaperture_statesテーブルへ
        更新する

        Args:
            aperture (float): 現在の開度
            unit_time (float): 開度１％あたりの秒数
        """
        while aperture < 100:
            self.actuator_state = await self.get_actuator_state()
            if self.actuator_state != settings.ACTUATOR_FORCED_OPEN:
                self.forced_stop()
                # print(f'forced open stopped:{aperture}')
                break;

            aperture += 1
            self.newest_aperture = aperture

            # print(f'forced increase:{aperture=}')
            self.update_aperture(aperture)
            await asyncio.sleep(int(unit_time))

    async def execute_forced_close(self, aperture: float, full_opening_times: float):
        """強制的に遮光カーテンを閉じる

        Args:
            aperture (float): _description_
            full_opening_times (float): _description_
        """
        # print(f'forced close before: now:{aperture=}')
        if aperture == 0:
            return

        # 開度１％時間
        unit_time = full_opening_times / 100

        try:
            if not self.curtain_busy:
                self.curtain_busy = True
                self.init_gpio()
                # print(f'forced close_curtain')
                # self.in_1.set_value(0)
                # self.in_2.set_value(1)
                self.in_2.set_value(Value.ACTIVE)
                self.forward_rotation_state(Value.INACTIVE)
                self.reverse_rotation_state(Value.ACTIVE)
            
            await self.forced_close(aperture, unit_time)
            
        except OSError as ex:
            print(f'{ex}')
        finally:
            if self.curtain_busy:
                self.stop_curtain()

    async def forced_close(self, aperture: float, unit_time: float):
        """開度が０％になるまで、開度を減じ、その値をaperture_statesテーブルへ
        更新する

        Args:
            aperture (float): 現在の開度
            unit_time (float): 開度１％あたりの秒数
        """
        while aperture > 0:
            self.actuator_state = await self.get_actuator_state()
            if self.actuator_state != settings.ACTUATOR_FORCED_CLOSE:
                self.forced_stop()
                # print(f'forced close stopped:{aperture}')
                break;

            aperture -= 1
            self.newest_aperture = aperture

            # print(f'forced decrease:{aperture=}')
            self.update_aperture(aperture)
            await asyncio.sleep(int(unit_time))

    async def execute(self, aperture: float, new_aperture: float, full_opening_times: float):
        """遮光カーテンの開閉を実行する

        Args:
            aperture (float): 現在開度
            new_aperture (float): 設定開度
            full_opening_times (float): 全開時間
        """
        # 開度１％時間
        unit_open_time = full_opening_times / 100

        self.curtain_busy = True

        if aperture > new_aperture:
            # カーテンを閉める
            # 現在開度から指定開度までの差分 Θ = 現在開度-指定開度	
            # 閉鎖時間: Θ ＊ 開度１％時間
            await self.close_curtain(unit_open_time, new_aperture, aperture)

        elif aperture < new_aperture:
            # カーテンを開く
            await self.open_curtain(unit_open_time, new_aperture, aperture)

        else: # aperture == new_aperture
            self.curtain_busy = False
            await asyncio.sleep(1)

    async def task(self, *args):
        """遮光カーテン実行
        設定条件に従って、遮光カーテンの開閉をおこなう

        Args:
            args[0] aperture (float): 現時点での開度
            args[1] adjust_value (float): 全開時間
        """
        aperture = args[0]              # actuator_states table.aperture
        full_opening_times = args[1]    # actuator_states table.adjust_value
        self.newest_aperture = aperture
        
        print(f'start aperture:{aperture=}')
        while True:
            print(f"blackout curtains task:{self.curtain_busy=} ")
            # environment_valuesテーブルから、現在の環境計測値（照度）を取得する
            try:
                # mode (int): 1:自動運転中, 0:手動運転中, 9:停止中
                # ACTUATOR_AUTO: int = 1
                # ACTUATOR_MANUAL: int = 0
                # ACTUATOR_STOPPED: int = 9
                # ACTUATOR_FORCED_OPEN: int = 11
                # ACTUATOR_FORCED_CLOSE:: int = 19
                self.actuator_state = await self.get_actuator_state()
                
                print(f'{self.actuator_state=}')
                lux = self.get_environment_values()

                # 現在の照度から、更新すべき新しい開度を取得する
                new_aperture = get_aperture(self.id, lux, aperture)
                
                if not self.curtain_busy and self.actuator_state == settings.ACTUATOR_AUTO:
                    await self.execute(aperture, new_aperture, full_opening_times)
                    # print(f'{aperture =} : {new_aperture=}')
                    aperture = self.newest_aperture
                    # self.update_aperture(aperture)

                elif self.actuator_state == settings.ACTUATOR_FORCED_OPEN:
                    await self.execute_forced_open(aperture, full_opening_times)
                    # print(f'forced open :{aperture =} : {new_aperture=}')
                    aperture = self.newest_aperture

                elif self.actuator_state == settings.ACTUATOR_FORCED_CLOSE:
                    await self.execute_forced_close(aperture, full_opening_times)
                    # print(f'forced close :{aperture =} : {new_aperture=}')
                    aperture = self.newest_aperture

                elif self.actuator_state == settings.ACTUATOR_STOPPED:
                    self.forced_stop()

                else:
                    await asyncio.sleep(1)

            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")

            sleep(1)
