from datetime import datetime
from sqlite3 import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy import and_
import sqlalchemy
from database.db_access import get_session
from models.actuator_models import \
    EnvironmentValues as ev, \
    ActuatorStates as ast, \
    ActuatorGpioNo as agn, \
    DeviceControlTable as dct, \
    IrrigationSchedule as iscdl
from schemas.actuator_schemas import \
    DeviceSchemas as ds, \
    ActuatorsStateSchema as ass, \
    StateSchema as ss, \
    GpioNoSchema as gs, \
    ActuatorGpioNoSchema as ags, \
    StepValuesSchema as svs, \
    DeviceControlSchema as dcs, \
    ActuatorModeSchema as ams, \
    IrrigationTimeSchema as its, \
    IrrigationScheduleSchema as iss
    

class EnvironmentValuesService:
    def __init__(self, db):
        self.db = db

    def create_env_values(self, values: ds) -> ds:
        """environment_valuesテーブルにWatchOverから送信されてきた
        環境情報をenvironment_valuesテーブルへ登録する

        Args:
            values (DeviceSchemas): 環境情報

        Returns:
            ds: _description_
        """
        # 全データ削除
        self.db.query(ev).delete()
        
        # DeviceSchemasからEnvironmentValuesへデータ変換する
        vals = ev()
        vals.temperature = values.temp
        vals.humidity = values.hum
        vals.moisture = values.mstr_0
        vals.lux = values.lux
        vals.updated = values.now

        self.db.add(vals)
        self.db.commit()
        self.db.refresh(vals)

        return values

    def get_actuators_info(self) -> ass:
        """各制御装置の稼働状況を取得する。
        取得テーブル: actuator_states

        Returns:
            List[str]: 各制御装置の稼働状況リスト
        """
        actuators = self.db.query(ast.actuator_id,
                                ast.state, 
                                ast.aperture, 
                                ast.actuator_name, 
                                ast.adjust_value,
                                ast.group_no) \
                        .filter(
                            and_(
                                ast.class_name != "",
                                ast.class_name is not None
                            )
                        ).all()

        self.db.commit()
        list = [val for val in actuators]  #[(key,state, actuator_name),(key,state, actuator_name),...]

        list_ss = []
        for val in list:
            item = ss(actuator_id=val.actuator_id,
                    state=val.state,
                    aperture=val.aperture,
                    actuator_name=val.actuator_name, 
                    adjust_value=val.adjust_value,
                    group_no=val.group_no) # type: ignore
            # item = ss(actuator_id=val[0], state=val[1], aperture=val[2], actuator_name=val[3], adjust_value=val[4]) # type: ignore
            list_ss.append(item)

        return ass(actuators=list_ss)

    def get_actuator_info(self, id:str) -> ss:
        """指定したidをもつ制御装置の稼働状況を取得する。
        取得テーブル: actuator_states

        Returns:
            StateSchema: 制御装置の稼働状況
        """
        try:
            with get_session() as db:
                actuator = db.query(ast).filter(
                            and_(
                                ast.actuator_id == id,
                                ast.class_name != "",
                                ast.class_name is not None
                            )
                        ).first()

                ret = ss(actuator_id=actuator.actuator_id, 
                        state=actuator.state, 
                        aperture=actuator.aperture, 
                        actuator_name=actuator.actuator_name, 
                        adjust_value=actuator.adjust_value,
                        group_no=actuator.group_no)

            return ret
        except (
                # データベースに接続できないエラーOperationalError
                # テーブルが存在しないエラーOperationalError
                # データベースがロックされているエラーOperationalError
                # データベースのインデックスエラーsqlite3.ProgrammingError
                sqlalchemy.orm.exc.StaleDataError, \
                sqlalchemy.exc.ArgumentError, \
                OperationalError, \
                ProgrammingError
            ) as err:
            self.db.rollback()
            print(f'{err}')
            raise

    def get_actuators_gpiono(self, id) -> ags:
        """対象の制御器が使用するＧＰＩＯ番号を取得する

        Args:
            id (str): 制御機器ＩＤ

        Returns:
            ags: _description_
        """
        actuators = self.db.query(agn.actuator_id, agn.gpio_no, agn.state) \
                        .filter(agn.actuator_id == id).all()

        self.db.commit()
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
            item = gs(actuator_id=val.actuator_id, gpio_no=val.gpio_no, state=val.state) # type: ignore
            # item = gs(actuator_id=val[0], gpio_no=val[1], state=val[2]) # type: ignore
            list_gs.append(item)

        return ags(gpionos=list_gs)

    def get_device_step_values(self, id) -> dcs:
        """device_control_tableから、指定したidをもつデータを抽出する

        Args:
            id (_str_): 制御機器ID(actuator_id)

        Returns:
            dcs: class DeviceControlSchemaの内容をjsonに変換したデータ
        """
        step_values = self.db.query(dct) \
                        .filter(dct.actuator_id == id).all()

        self.db.commit()
        list = [val for val in step_values]

        print(f'step_values={str(step_values[0].actuator_id)}')
        list_svs = []
        for val in list:
            item = svs(
                actuator_id = val.actuator_id,         # 機器ID
                pattern_id = val.pattern_id,          # パターン№  0:温度、1:日射量、2:時間
                priority = int(val.priority or 1),            # 優先順位 1:現時点では意味なし
                min_value = float(val.min_value or 0.0),         # 最小値
                first_stage = float(val.first_stage or 0.0),       # 第1段階
                first_value = float(val.first_value or 0.0),       # 第1段階設定値
                secnd_stage = float(val.secnd_stage or 0.0),       # 第2段階
                secnd_value = float(val.secnd_value or 0.0),       # 第2段階設定値
                third_stage = float(val.third_stage or 0.0),       # 第3段階
                third_value = float(val.third_value or 0.0),       # 第3段階設定値
                forth_stage = float(val.forth_stage or 0.0),       # 第4段階
                forth_value = float(val.forth_value or 0.0),       # 第4段階設定値
                fifth_stage = float(val.fifth_stage or 0.0),       # 第5段階
                fifth_value = float(val.fifth_value or 0.0),       # 第5段階設定値
                daytime_start = str(val.daytime_start  or ''),       # 昼間_開始時間
                daytime_ending = str(val.daytime_ending or ''),      # 昼間_終了時間
                daytime_aperture = float(val.daytime_aperture or 0.0),  # 昼間_開度
                night_start = str(val.night_start or ''),         # 夜間_開始時間
                night_ending = str(val.night_ending or ''),        # 夜間_終了時間
                night_aperture = float(val.night_aperture or 0.0),    # 夜間_開度
                classify = float(val.classify or 0.0)          # 動作種別
            ) # type: ignore
            list_svs.append(item)

        return dcs(devctrls=list_svs)

    def update_actuator_mode(self, id: str, mode: int) -> ass:
        """対象の制御機器の稼働状態を更新する
        actuator_statesテーブル
        # mode (int): 1:自動運転中, 0:手動運転中, 9:停止中
        config.py
            ACTUATOR_AUTO: int = 1
            ACTUATOR_MANUAL: int = 0
            ACTUATOR_STOPPED: int = 9

        Args:
            id (str): 対象制御機器ID
            mode (int): 更新する稼働状態

        Returns:
            ss: actuator.stateを指定したmodeで更新した対象制御機器情報
            sqlalchemy.orm.exc.StaleDataError
        """
        try:
            with get_session() as db:
                actuator = db.query(ast).filter(ast.actuator_id == id).first()

                # ret = ams(actuator_id = id, mode=0)
                ret = ss(actuator_id=actuator.actuator_id, 
                        state=actuator.state, 
                        aperture=actuator.aperture, 
                        actuator_name=actuator.actuator_name, 
                        adjust_value=actuator.adjust_value,
                        group_no=actuator.adjust_value)

                if actuator is not None:
                    actuator.state = mode
                    db.commit()
                    ret.state = mode

            return ret
        except (
                # データベースに接続できないエラーOperationalError
                # テーブルが存在しないエラーOperationalError
                # データベースがロックされているエラーOperationalError
                # データベースのインデックスエラーsqlite3.ProgrammingError
                # データの挿入エラーIntegrityError
                sqlalchemy.orm.exc.StaleDataError, \
                sqlalchemy.exc.ArgumentError, \
                OperationalError, \
                IntegrityError, \
                ProgrammingError
            ) as err:
            self.db.rollback()
            print(f'{err}')
            raise
        # finally:
        #     self.db.close()

    def update_device_control(self, id: str, pattern:int, updateData: dict) -> bool:
        """段階別データ更新処理
            device_control_tableのデータを更新する

        Args:
            data (dict): 更新データ
            db (Session, optional): _description_. Defaults to Depends(get_db).

        Returns:
            StateSchema: 更新後のデータ
        """
        try:
            with get_session() as db:
                row = db.query(dct).filter(
                        and_( 
                            dct.actuator_id == id,
                            dct.pattern_id == pattern)
                    ).first()
                
                if row is not None:
                    row.first_stage = updateData.get('first_stage', 0)      # 第1段階
                    row.first_value = updateData.get('first_value', 0)      # 第1段階設定値
                    row.second_stage = updateData.get('second_stage', 0)    # 第2段階
                    row.second_value = updateData.get('second_value', 0)    # 第2段階設定値
                    row.third_stage = updateData.get('third_stage', 0)      # 第3段階
                    row.third_value = updateData.get('third_value', 0)      # 第3段階設定値
                    row.forth_stage = updateData.get('forth_stage', 0)      # 第4段階
                    row.forth_value = updateData.get('forth_value', 0)      # 第4段階設定値
                    row.fifth_stage = updateData.get('fifth_stage', 0)      # 第5段階
                    row.fifth_value = updateData.get('fifth_value', 0)      # 第5段階設定値
                    row.modified = datetime.now()                           # 更新年月日時刻
                    db.commit()
                    return True
                else:
                    return False
        except (
                # データベースに接続できないエラーOperationalError
                # テーブルが存在しないエラーOperationalError
                # データベースがロックされているエラーOperationalError
                # データベースのインデックスエラーsqlite3.ProgrammingError
                sqlalchemy.orm.exc.StaleDataError, \
                sqlalchemy.exc.ArgumentError, \
                OperationalError, \
                IntegrityError, \
                ProgrammingError
            ) as err:
            self.db.rollback()
            print(f'{err}')
            raise

