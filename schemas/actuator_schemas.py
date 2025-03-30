from datetime import datetime
from pydantic import BaseModel, Field

# リクエストbodyを定義
#{'mstr_0': 0.96, 'temp': 26.3, 'hum': 71.9, 'lux': 90, 'now': '2024-06-27 20:48:30'}
class DeviceSchemas(BaseModel):
    mstr_0: float
    temp: float
    hum: float
    lux: float
    now: str
    # temperature: float
    # humidity: float
    # moisture: float
    # lux: float
    # updated: str

    class Config:
        orm_mode = True

class StateSchema(BaseModel):
    """actuator_statesテーブルスキーマクラス

    Args:
        BaseModel (_type_): _description_
    """
    actuator_id: str
    state: int
    aperture: float
    actuator_name: str
    adjust_value: float
    group_no: int

class ActuatorsStateSchema(BaseModel):
    """StateSchema辞書スキーマ

    Args:
        BaseModel (_type_): _description_
    """
    #{'irrgtn_01': 1, 'blkcrtn_01': 1, 'sdwn_01': 1, 'skylght_01': 1, 'crcltn_01': 1}
    #items: list[ItemResponse] = []
    actuators: list[StateSchema] = []

    class Config:
        orm_mode = True

class GpioNoSchema(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    actuator_id: str    # 制御機器ID
    gpio_no :float        # GPIO番号
    state: str          # 状態（説明文）

class ActuatorGpioNoSchema(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    gpionos: list[GpioNoSchema] = []

    class Config:
        orm_mode = True

class StepValuesSchema(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    actuator_id:str         # 機器ID
    pattern_id:int          # パターン№  0:温度、1:日射量、2:時間
    priority:int            # 優先順位
    min_value:float         # 最小値
    first_stage:float       # 第1段階
    first_value:float       # 第1段階設定値
    secnd_stage:float       # 第2段階
    secnd_value:float       # 第2段階設定値
    third_stage:float       # 第3段階
    third_value:float       # 第3段階設定値
    forth_stage:float       # 第4段階
    forth_value:float       # 第4段階設定値
    fifth_stage:float       # 第5段階
    fifth_value:float       # 第5段階設定値
    daytime_start:str       # 昼間_開始時間
    daytime_ending:str      # 昼間_終了時間
    daytime_aperture:float  # 昼間_開度
    night_start:str         # 夜間_開始時間
    night_ending:str        # 夜間_終了時間
    night_aperture:float    # 夜間_開度
    classify:float          # 動作種別

class DeviceControlSchema(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    devctrls: list[StepValuesSchema] = []

    class Config:
        orm_mode = True

class ActuatorModeSchema(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    actuator_id: str
    mode: int    # 制御機器稼働状況

class ActuatorGroupSchema(BaseModel):
    """actuator_groupsテーブルスキーマクラス

    Args:
        BaseModel (_type_): _description_
    """
    group_no : int    # グループ番号
    group_name : str  # グループ名

class ActuatorGroupsSchema(BaseModel):
    """actuator_groupsリスト

    Args:
        BaseModel (_type_): _description_
    """
    actrgrps: list[ActuatorGroupSchema] = []

    class Config:
        orm_mode = True

class IrrigationTimeSchema(BaseModel):
    """irrigation_scheduleテーブルスキーマクラス

    Args:
        BaseModel (_type_): _description_
    """
    actuator_id: str        # 制御機器ID
    permission: int         # 潅水許可 0:不許可 1:許可
    line_no: int            # 潅水ライン
    start_time: str         # 潅水時刻
    irrigation_time: float  # 潅水時間
    builder_cd: str         # 作成者コード
    created: datetime       # 作成年月日時刻
    updator_cd: str         # 更新者コード
    modified: datetime      # 更新年月日時刻

class IrrigationScheduleSchema(BaseModel):
    """irrigation_scheduleリスト

    Args:
        BaseModel (_list_): IrrigationScheduleSchema list
    """
    schedules: list[IrrigationTimeSchema] = []
    
    class Config:
        orm_mode = True
