from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Float
from database.db_access import Base
from datetime import datetime

class EnvironmentValues(Base):
    __tablename__ = "environment_values"

    id = Column(Integer, primary_key=True)  # default autoincrement 
    temperature = Column(Float)
    humidity = Column(Float)
    moisture = Column(Float)
    lux = Column(Float)
    updated = Column(String(20))
    #updated = Column(DateTime(timezone=True))

#{'mstr_0': 0.96, 'temp': 26.3, 'hum': 71.9, 'lux': 90, 'now': '2024-06-27 20:48:30'}

class ActuatorStates(Base):
    __tablename__ = "actuator_states"

    actuator_id = Column(String, autoincrement=False, primary_key=True)
    actuator_name = Column(String)              # 機器名
    state = Column(Integer)                     # 稼働状態 0:自動運転中 1:手動運転中 9:停止中
    aperture = Column(Float)                    # 開度
    interval = Column(Integer, nullable=True)   # 計測間隔
    class_name = Column(String, nullable=True)  # クラス名
    adjust_value = Column(Float, nullable=True) # 調整値　モータの場合は、完全開放時間
    group_no = Column(Integer, nullable=True)   # 器機グループ番号 1:開閉系, 2:潅水系,3:その他
    memo = Column(String, nullable=True)        # 備考
    created = Column(DateTime(timezone=True), nullable=True)   # 作成年月日時刻
    version = Column(BigInteger, nullable=False)
    # 楽観的排他制御
    __mapper_args__ = {'version_id_col': version}
    
class ActuatorGpioNo(Base):
    __tablename__ = "actuator_gpiono"

    actuator_id = Column(String, autoincrement=False, primary_key=True)    # 制御機器ID
    gpio_no = Column(Float, nullable=True)  # GPIO番号
    state = Column(String)  # 状態（説明文）
    builder_cd = Column(String, nullable=True)     # 作成者コード
    created_at = Column(DateTime(timezone=True))   # 作成年月日時刻
    updator_cd = Column(String, nullable=True)     # 更新者コード
    modified_at = Column(DateTime(timezone=True))  # 更新年月日時刻

class DeviceControlTable(Base):
    """device_control_tableテーブルからデータを取得する

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "device_control_table"

    actuator_id	= Column(String, autoincrement=False, primary_key=True) # 機器ID
    pattern_id	= Column(Integer, autoincrement=False, primary_key=True) # パターン№  0:温度、1:日射量、2:時間
    priority	= Column(Integer)           # 優先順位
    min_value	= Column(Float)             # 最小値
    first_stage	= Column(Float)             # 第1段階
    first_value	= Column(Float)             # 第1段階設定値
    secnd_stage	= Column(Float)             # 第2段階
    secnd_value	= Column(Float)             # 第2段階設定値
    third_stage	= Column(Float)             # 第3段階
    third_value	= Column(Float)             # 第3段階設定値
    forth_stage	= Column(Float)             # 第4段階
    forth_value	= Column(Float)             # 第4段階設定値
    fifth_stage	= Column(Float)             # 第5段階
    fifth_value	= Column(Float)             # 第5段階設定値
    daytime_start	= Column(String)        # 昼間_開始時間
    daytime_ending	= Column(String)        # 昼間_終了時間
    daytime_aperture	= Column(Float)     # 昼間_開度
    night_start	= Column(String)            # 夜間_開始時間
    night_ending	= Column(String)        # 夜間_終了時間
    night_aperture	= Column(Float)         # 夜間_開度
    classify	= Column(Float)             # 動作種別
    builder_cd	= Column(String, nullable=True) # 作成者コード
    created = Column(DateTime(timezone=True))   # 作成年月日時刻
    updator_cd	= Column(String, nullable=True) # 更新者コード
    modified = Column(DateTime(timezone=True))  # 更新年月日時刻

class ActuatorGroups(Base):
    __tablename__ = "actuator_groups"

    group_no = Column(Integer, autoincrement=False, primary_key=True)                    # グループ番号
    group_name = Column(String)                 # グループ名
    builder_cd = Column(String, nullable=True)  # 作成者コード
    created = Column(DateTime(timezone=True))   # 作成年月日時刻
    updator_cd = Column(String, nullable=True)  # 更新者コード
    modified = Column(DateTime(timezone=True))  # 更新年月日時刻


class IrrigationSchedule(Base):
    """自動潅水スケジュール
        CREATE TABLE "irrigation_schedule" (
            "actuator_id"	TEXT,
            "permission"	INTEGER NOT NULL,
            "line_no"	INTEGER,
            "start_time"	text,
            "irrigation_time"	REAL,
            "builder_cd"	TEXT,
            "created"	TIMESTAMP DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
            "updator_cd"	TEXT,
            "modified"	TIMESTAMP DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
            PRIMARY KEY("actuator_id","start_time")
        )
    Args:
        Base (_type_): _description_
    """
    __tablename__ = "irrigation_schedule"
    
    actuator_id = Column(String, primary_key=True)  # 制御機器ID
    permission = Column(Integer, nullable=False)    # 潅水許可 0:不許可 1:許可
    line_no = Column(Integer)                       # 潅水ライン
    start_time = Column(String, primary_key=True)   # 潅水時刻
    irrigation_time = Column(Float, default=0.0)    # 潅水時間
    builder_cd = Column(String, nullable=True)      # 作成者コード
    created = Column(DateTime(timezone=True), default = datetime.now) # 作成年月日時刻
    updator_cd = Column(String, nullable=True)      # 更新者コード
    modified = Column(DateTime(timezone=True), default = datetime.now) # 更新年月日時刻
