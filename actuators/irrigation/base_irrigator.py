import asyncio
import sqlalchemy
import gpiod
from gpiod.line import Direction, Value
from time import sleep
from sqlalchemy import and_
from datetime import datetime
from sqlite3 import IntegrityError, OperationalError, ProgrammingError
from actuators.irrigation.irrigation_data import IrrigationLine
from schemas.actuator_schemas import IrrigationScheduleSchema, IrrigationTimeSchema
from actuators.base_actuators.base_actuator import Actuator
from database.db_access import MANUAL_IRRIGATION_TIME, get_session
from models.actuator_models import IrrigationSchedule
from config import settings

class Irrigator(Actuator):
    """_summary_

    Args:
        Actuator (_type_): _description_
    """
    def __init__(self, id) -> None:
        """初期化処理

        Args:
            id (_str_): 対象制御装置ID
        """
        super().__init__(id)

        self.current_line = None
        self.request_line = None

    def turn_on(self):
        """潅水ラインオン

        Args:
            sel (_type_): _description_
            target_line (object): 対象ライン self.line_1 or self.line_2
        """
        try:
            if not self.current_line.busy:
                print('line open...')
                # gpiod.Chip.target
                # self.current_line.target.set_value(1)
                super().request_lines(self.current_line.gpio_no).set_value(Value.ACTIVE)
                self.current_line.busy = True

        except OSError as ex:
            raise ex

    def turn_off(self):
        """潅水ラインオフ

        Args:
            sel (_type_): _description_
            target_line (object): 対象ライン self.line_1 or self.line_2
        """
        try:
            if self.current_line.busy:
                print('line close...')
                # self.current_line.target.set_value(0)
                super().request_lines(self.current_line.gpio_no).set_value(Value.INACTIVE)
                self.current_line.busy = False

        except OSError as ex:
            raise ex

    def get_irrigation_schedule(self, actuator_id: str, current_time:str) -> IrrigationScheduleSchema:
        """潅水スケジュールを取得する
        指定した潅水ライン番号をもつ潅水スケジュールを
        irrigation_scheduleテーブルから取得する

        Args:
            current_time (str): 検査対象時刻(hh:mm)

        Returns:
            iss: irrigation_scheduleリスト
        """
        try:
           with get_session() as db:
                value = db.query(IrrigationSchedule).filter(
                            and_( 
                                IrrigationSchedule.actuator_id == actuator_id,
                                IrrigationSchedule.start_time == current_time
                            )).first()

                schedule = None
                
                if value is not None:
                    schedule = IrrigationTimeSchema(
                        actuator_id = value.actuator_id,            # 制御機器ID
                        permission = value.permission,              # 潅水許可 0:不許可 1:許可
                        line_no = value.line_no,                    # 潅水ライン
                        start_time = value.start_time,              # 潅水時刻
                        irrigation_time = value.irrigation_time,    # 潅水時間
                        builder_cd = value.builder_cd,              # 作成者コード
                        created = value.created,                    # 作成年月日時刻
                        updator_cd = value.updator_cd,              # 更新者コード
                        modified =  value.modified                  # 更新年月日時刻
                        )

                return schedule

        except (
                # データベースに接続できないエラーOperationalError
                # テーブルが存在しないエラーOperationalError
                # データベースがロックされているエラーOperationalError
                # データベースのインデックスエラーsqlite3.ProgrammingError
                sqlalchemy.orm.exc.StaleDataError, \
                sqlalchemy.exc.ArgumentError, \
                OperationalError, \
                IntegrityError, \
                ProgrammingError, \
                OSError, \
                Exception
            ) as err:
            self.db.rollback()
            print(f'{err}')
            return None

    async def do_irrigation(self):
        """潅水時刻になったら、その時間に設定された潅水時間、潅水ポンプを作動させる
        """
        # 現在の時刻（hh:mm:dd）を文字列で取得
        try:
            current_time = datetime.now().strftime('%H:%M')
            # irrigation_scheduleテーブルから現在の時刻と一致するstart_timeをもつデータを取得する
            target = self.get_irrigation_schedule(self.id, current_time)
            # もしデータが取得出来たら、潅水を指定時間、実行する

            if target is not None and not self.current_line.is_done(str(target.start_time)) and target.permission:
                self.current_line.done_time = str(target.start_time)
                self.turn_on()
                await asyncio.sleep(target.irrigation_time)

        except (OSError, Exception) as ex:
            raise ex

        finally:
            if self.current_line.busy:
                print(f'sttoped_irrigation')
                self.turn_off()

    async def foreced_irrigation(self):
        """強制灌漑プロセスを開始する。

        この方法は、灌漑システムを手動で開始するためのものです。
        自動化されたスケジュールをバイパスする。
        これは即時灌漑が必要な場合に使用する。
        """
        try:
            # 潅水が実行中の場合、強制的に停止する 
            if self.current_line.busy:
                self.turn_off()

            target = self.get_irrigation_schedule(self.id, MANUAL_IRRIGATION_TIME)

            if target is not None:
                self.current_line.done_time = MANUAL_IRRIGATION_TIME
                self.turn_on()
                await asyncio.sleep(target.irrigation_time)
        except Exception as ex:
            raise ex
        finally:
            if self.current_line.busy:
                self.turn_off()

    async def forced_stopped_irrigation(self):
        """強制停止灌漑プロセスを開始する。

        Raises:
            ex: _description_
        """
        try:
            if self.current_line.busy:
                self.turn_off()
            await asyncio.sleep(1)
        except Exception as ex:
            raise ex
    
    async def task(self,  *args):
        """_summary_
        """
        print(f'irrigator task args:{args}')
        
        while True:
            try:
                self.actuator_state = await self.get_actuator_state()
                print(f'Line No>>>{self.current_line.line_no=}:irrigator state:{self.actuator_state=}')

                if self.actuator_state == settings.ACTUATOR_AUTO:
                    await self.do_irrigation()

                elif self.actuator_state == settings.ACTUATOR_FORCED_OPEN:
                    print('<<<Forced Irrigation>>>')
                    await self.foreced_irrigation()
                    #TODO 強制潅水が終わった時点で、もとの状態(actuator_states.state)に戻す処理を追加する必要がある
                
                elif self.actuator_state == settings.ACTUATOR_FORCED_CLOSE:
                    print('<<<Stopped Irrigation>>>')
                    await self.forced_stopped_irrigation()

                else:
                    await asyncio.sleep(1)

            except Exception as e:
                print(f"潅水処理で予期しないエラーが発生しました: {e}")

            sleep(1)
