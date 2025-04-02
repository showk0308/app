import sqlalchemy
from datetime import datetime
from sqlite3 import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.db_access import get_session, MANUAL_IRRIGATION_TIME
from models.actuator_models import IrrigationSchedule
from schemas.actuator_schemas import IrrigationTimeSchema, IrrigationScheduleSchema

class IrrigationScheduleAdmin:
    def __init__(self, db: Session = None):
        self.db = db

    def get_irrigation_time_schedule(self, line_no: int) -> IrrigationScheduleSchema:
        """潅水スケジュールを取得する
        指定した潅水ライン番号をもつ潅水スケジュールを
        irrigation_scheduleテーブルから取得する

        Args:
            line_no (int): 潅水ライン番号

        Returns:
            iss: irrigation_scheduleリスト
        """
        try:
            with get_session() as db:
                rows = db.query(IrrigationSchedule).filter(
                        and_(
                            IrrigationSchedule.line_no == line_no,
                            IrrigationSchedule.start_time != MANUAL_IRRIGATION_TIME
                        )
                    ).all()

                source = [val for val in rows]

                list_its: IrrigationScheduleSchema = []

                for val in source:
                    item = IrrigationTimeSchema(
                        actuator_id = val.actuator_id,          # 制御機器ID
                        permission = val.permission,            # 潅水許可 0:不許可 1:許可
                        line_no = val.line_no,                  # 潅水ライン
                        start_time = val.start_time,            # 潅水時刻
                        irrigation_time = val.irrigation_time,  # 潅水時間
                        builder_cd = val.builder_cd if not None else "",    # 作成者コード
                        created = val.created,                  # 作成年月日時刻
                        updator_cd = val.updator_cd if not None else "",    # 更新者コード
                        modified = val.modified                 # 更新年月日時刻
                    ) # type: ignore
                    
                    list_its.append(item)

                return IrrigationScheduleSchema(schedules=list_its)

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
                Exception
            ) as err:
            self.db.rollback()
            print(f'{err}')
            raise

    def update_irrigation_table(self, data: dict) -> bool:
        """潅水スケジュールを更新する

        Args:
            data (dict): 更新スケジュールデータ
                ex.{'05:00': [0, 3], '06:00': [0, 0], '07:00': [0, 20], ..., '23:00': [0, 0]}

                actuator_id = Column(String, primary_key=True)  # 制御機器ID
                permission = Column(Integer, nullable=False)    # 潅水許可 0:不許可 1:許可
                line_no = Column(Integer)                       # 潅水ライン
                start_time = Column(String, primary_key=True)   # 潅水時刻
                irrigation_time = Column(Float, default=0.0)    # 潅水時間
                builder_cd = Column(String)                     # 作成者コード
                created = Column(DateTime(timezone=True), default = datetime.now) # 作成年月日時刻
                updator_cd = Column(String)                     # 更新者コード
                modified = Column(DateTime(timezone=True), default = datetime.now) # 更新年月日時刻

        Returns:
            bool: 更新が成功した場合はTrue、失敗した場合はFalse
        """
        try:
            id = data.get('id', '')
            if id is None or id == '':
                return False
            
            schedule = data.get('schedules', {})
            if schedule is None or len(schedule) == 0:
                return False
            
            with get_session() as db:
                for key, value in schedule.items():
                    # ex. '05:00': [0, 3] -> key:05:00, value:[0, 3]
                    row = db.query(IrrigationSchedule).filter(
                            and_(IrrigationSchedule.actuator_id == id,
                                 IrrigationSchedule.start_time == key)
                        ).first()

                    if row is not None:
                        row.permission, row.irrigation_time = value
                        
                        row.modified = datetime.now()
                        db.commit()
                    else:
                        return False

                return True

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
                Exception
            ) as err:
            self.db.rollback()
            print(f'{err}')
            raise

    def get_irrigation_line_no(self, id: str) -> int:
        """潅水ライン番号を取得する

        Args:
            id (str): 制御機器ID

        Returns:
            int: 潅水ライン番号
        """
        try:
            with get_session() as db:
                row = db.query(IrrigationSchedule).filter(IrrigationSchedule.actuator_id == id).first()
                if row is not None:
                    return row.line_no
                else:
                    return -1

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
                Exception
            ) as err:
            self.db.rollback()
            print(f'{err}')
            raise
    
    def set_manual_irrigtion_time(self, time:int):
        try:
            with get_session() as db:
                row = db.query(IrrigationSchedule).filter(IrrigationSchedule.actuator_id == id).first()
                if row is not None:
                    return row.line_no
                else:
                    return -1

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
                Exception
            ) as err:
            self.db.rollback()
            print(f'{err}')
            raise
    
    def set_manual_irrigtion_time(self, id: str, time: int ) -> bool:
        """手動潅水時刻を設定する

        Args:
            id (str): 制御機器ID
            time (int): 潅水時間

        Returns:
            bool: 更新が成功した場合はTrue、失敗した場合はFalse
        """
        try:
            with get_session() as db:
                row = db.query(IrrigationSchedule).filter(
                        and_(IrrigationSchedule.actuator_id == id,
                             IrrigationSchedule.start_time == MANUAL_IRRIGATION_TIME)
                    ).first()
                if row is not None:
                    row.irrigation_time = time
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
                ProgrammingError, \
                Exception
            ) as err:
            self.db.rollback()
            print(f'{err}')
            raise
    