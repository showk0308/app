from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.irrigation_schedule_admin import IrrigationScheduleAdmin
from database.db_access import get_db
from services.actuator_services import EnvironmentValuesService
from config import settings
from schemas.actuator_schemas import \
    ActuatorGpioNoSchema, \
    ActuatorModeSchema, \
    ActuatorsStateSchema, \
    DeviceControlSchema, \
    DeviceSchemas, \
    IrrigationScheduleSchema, \
    StateSchema

router = APIRouter()

@router.post("/env_values/", response_model=ActuatorsStateSchema)
def get_actuators_state(values: DeviceSchemas, db: Session = Depends(get_db)):
    """現在稼働中の制御機器の稼働状態を取得する
    取得情報は、この問い合わせ先（flskr.views.py/get_controllers_monitor()へ返す

    Args:
        values (DeviceSchemas): _description_
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _json_: 制御機器の稼働状態を取得する
                {'actuators': [{'actuator_id': 'irrgtn_01', 'state': 1, 'aperture': 0.0}, 
                {'actuator_id': 'blkcrtn_01', 'state': 1, 'aperture': 20.0}, 
                {'actuator_id': 'sdwn_01', 'state': 1, 'aperture': 50.0}]}
    """
    # if values is None:
    #     raise HTTPException(status_code=404, detail="values is None")

    ev = EnvironmentValuesService(db)

    ev.create_env_values(values)
    
    states = ev.get_actuators_info()
    # states = ev.get_actuators_states()

    return states

@router.get("/actuators_state/", response_model=ActuatorsStateSchema)
def get_actuators_operating_status(db: Session = Depends(get_db)):
    """現在稼働中の制御機器の稼働状態を取得する
    取得情報は、この問い合わせ先（flskr.views.py/get_controllers_monitor()へ返す

    Args:
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _json_: 制御機器の稼働状態を取得する
                {'actuators': [{'actuator_id': 'irrgtn_01', 'state': 1, 'aperture': 0.0}, 
                {'actuator_id': 'blkcrtn_01', 'state': 1, 'aperture': 20.0}, 
                {'actuator_id': 'sdwn_01', 'state': 1, 'aperture': 50.0}]}
    """
    ev = EnvironmentValuesService(db)

    states = ev.get_actuators_info()

    return states

@router.get("/actuator_state/", response_model=StateSchema)
def get_actuators_operating_status(id:str, db: Session = Depends(get_db)):
    """指定した制御機器の稼働状態を取得する
    取得情報は、この問い合わせ先（flskr.views.py/get_controllers_monitor()へ返す

    Args:
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _json_: 制御機器の稼働状態を取得する
            {actuator_id:"str", state: "int", aperture: "float", actuator_name: "str", adjust_value: "float"}
    """
    ev = EnvironmentValuesService(db)

    state = ev.get_actuator_info(id)

    return state

@router.get("/actuators_gpiono/", response_model=ActuatorGpioNoSchema)
def get_actuators_operating_status(id: str, db: Session = Depends(get_db)):
    """対象制御機器に設定するGPIO番号を取得する

    Args:
        id (str): 対象制御機器ID
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        ActuatorGpioNoSchema: GpioNoSchema辞書
    """
    ev = EnvironmentValuesService(db)

    states = ev.get_actuators_gpiono(id)

    return states

@router.get("/device_steps/", response_model=DeviceControlSchema)
def get_device_step_values(id: str, db: Session = Depends(get_db)):
    """device_control_tableから、指定したidをもつデータを抽出する

    Args:
        id (str): 対象とする制御機器ID
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _DeviceControlSchema_: DeviceControlSchemaの内容をjsonに変換したデータ
    """
    ev = EnvironmentValuesService(db)

    values = ev.get_device_step_values(id)
    # devctrls=[
    # StepValuesSchema(actuator_id='blkcrtn_01', pattern_id=0, priority=1, min_value=28.0, first_stage=28.0, first_value=70.0, secnd_stage=30.0, secnd_value=20.0, third_stage=33.0, third_value=5.0, forth_stage=0.0, forth_value=0.0, fifth_stage=0.0, fifth_value=0.0, daytime_start='', daytime_ending='', daytime_aperture=0.0, night_start='', night_ending='', night_aperture=0.0, classify=0.0), 
    # StepValuesSchema(actuator_id='blkcrtn_01', pattern_id=1, priority=1, min_value=100.0, first_stage=100.0, first_value=20.0, secnd_stage=200.0, secnd_value=10.0, third_stage=250.0, third_value=5.0, forth_stage=0.0, forth_value=0.0, fifth_stage=0.0, fifth_value=0.0, daytime_start='', daytime_ending='', daytime_aperture=0.0, night_start='', night_ending='', night_aperture=0.0, classify=0.0)])

    return values

@router.put("/actuator_mode/", response_model=StateSchema)
def post_change_mode(state: ActuatorModeSchema, db: Session = Depends(get_db)):
    """idをキーとする稼働中の制御機器の動作を変更する
    動作：自動運転中、手動運転中、停止中
    actuator_statesテーブル

    Args:
        id (str): 制御機器ID(actuator_states.actuator_id)
        mode (int): 1:自動運転中, 0:手動運転中, 9:停止中
    Returns:
        StateSchema
            actuator_id
            state
            aperture
            actuator_name
            adjust_value
            group_no
    """
    # print(f'{state.actuator_id=}')
    # print(f'{state.mode=}')

    evs = EnvironmentValuesService(db)
    result = evs.update_actuator_mode(state.actuator_id, state.mode)
    
    return result

@router.put("/update_device_control/")
def post_device_control(data: dict, db: Session = Depends(get_db)) -> bool:
    """段階別データ更新処理
        device_control_tableのデータを更新する
        このコードは、FastAPIを使用してデバイス制御の更新を行うエンドポイントを定義しています。
        @router.put("/update_device_control/", response_model=StateSchema)デコレータは、
        HTTP PUTリクエストを受け取り、StateSchemaというレスポンスモデルを返すことを示しています。

        関数post_device_controlは、更新データを含む辞書型のdataと、
        データベースセッションdbを引数として受け取ります。
        dbはDepends(get_db)を使用して依存関係として注入されます。
        この関数は、デバイス制御テーブルのデータを更新するための処理を行います。        
    Args:
        data (dict): 更新データ
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        StateSchema: 更新後のデータ
    """
    # print(data['id'])
    # print(data['pattern'])
    # print(data['updateData'])

    evs = EnvironmentValuesService(db)
    result = evs.update_device_control(data['id'], data['pattern'], data['updateData'])

    return result

@router.get("/irrigation_schedule/", response_model=IrrigationScheduleSchema)
def get_irrigation_time_schedule(line_no: int, db: Session = Depends(get_db)):
    """自動潅水スケジュールを取得する
    irrigation_timesテーブルから、潅水スケジュールを取得する
    
    Args:
        line_no (int): 潅水ライン番号
        db (Session, optional): _description_. Defaults to Depends(get_db).
    """
    # print(f'{line_no=}')
    # evs = EnvironmentValuesService(db)
    # result = evs.get_irrigation_time_schedule(line_no)
    isa = IrrigationScheduleAdmin(db)
    result = isa.get_irrigation_time_schedule(line_no)
    
    # print(f'{result=}')
    
    return result

@router.put("/update_irrigation_table/")
def update_irrigation_table(data: dict, db: Session = Depends(get_db)) -> bool:
    """自動潅水スケジュールを更新する

    Args:
        data (dict): 更新データ辞書 
            ex.{'id': 'irrgtn_01', 
                'schedules':{'05:00': [0, 0], '06:00': [0, 0], '07:00': [0, 20], ...}}
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        bool: 更新が成功した場合はTrueを返す。更新が失敗した場合はFalseを返す。
    """
    # print(data)
    print(f'id:{data["id"]}')
    print(f'schedules:{data["schedules"]}')
    # evs = EnvironmentValuesService(db)
    isa = IrrigationScheduleAdmin(db)

    result = isa.update_irrigation_table(data)

    return result

@router.get("/irrigation_line_no/")
def get_irrigation_line_no(id: str, db: Session = Depends(get_db)):
    """潅水ライン番号を取得する

    Args:
        id (str): 制御機器ID
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        int: 潅水ライン番号
    """
    isa = IrrigationScheduleAdmin(db)

    result = isa.get_irrigation_line_no(id)
    # print(f'irrigation_line_no:{id=}:{result=}')

    return result

@router.put("/manual_irrigation_time/")
def put_manual_irrigtion_time(data: dict, db: Session = Depends(get_db)) -> bool:
    """手動潅水時刻を設定する

    Args:
        data (dict): {"id": ID, "time": value}
                     ex.{"id": "irrgtn_01", "time": 15}
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        bool: 更新が成功した場合はTrueを返す。更新が失敗した場合はFalseを返す。
    """
    print(f'<<<<<< {data["id"]=}:{data["time"]=}>>>>>>>>')
    isa = IrrigationScheduleAdmin(db)

    result = isa.set_manual_irrigtion_time(data["id"], data["time"])

    return result
