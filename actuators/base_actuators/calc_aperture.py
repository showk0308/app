from datetime import datetime
from models.actuator_models import DeviceControlTable as dc
from database.db_access import get_session

PATTERN_TEMP: int = 0    # 温度
PATTERN_LUX: int = 1    # 日射量
PATTERN_TIME: int = 2    # 時間
PATTERN_DISMISS: int = -1    # データなし

def get_degrees_apertures(id: str):
    """device_control_tableから対象とするactuator_idをもつ
    レコードを抽出する。
    抽出したレコードから*_stageリスト、*_valueリストを作成する。
    作成したペアのリストと、パターンID PATTERN_idを返す。

    Args:
        id (str): 抽出対象制御機器ID

    Returns:
        list, list: なにも抽出されなかった場合は、空のペアリストを返す

    Yields:
        int, list, list: パターンid, stageリスト, apertureリスト
    """
    with get_session() as db:
        controlls = db.query(dc).filter(dc.actuator_id == id).all()

        if controlls is not None:
            for ctrl in controlls:
                if ctrl.pattern_id == PATTERN_TIME: #時間
                    yield ctrl.pattern_id, \
                            [ctrl.daytime_start, ctrl.daytime_ending, ctrl.daytime_aperture],\
                            [ctrl.night_start, ctrl.night_ending, ctrl.night_aperture]
                else:
                    stage_list = [
                        ctrl.first_stage,   # 第1段階
                        ctrl.secnd_stage,   # 第2段階
                        ctrl.third_stage,   # 第3段階
                        ctrl.forth_stage,   # 第4段階
                        ctrl.fifth_stage,   # 第5段階
                    ]

                    aperture_list = [
                        ctrl.first_value,   # 第1段階設定値
                        ctrl.secnd_value,   # 第2段階設定値
                        ctrl.third_value,   # 第3段階設定値
                        ctrl.forth_value,   # 第4段階設定値
                        ctrl.fifth_value,   # 第5段階設定値
                    ]
                
                    yield ctrl.pattern_id, stage_list, aperture_list

        db.commit()

        return PATTERN_DISMISS, [], []

def has_key(key: str, states: dict) -> bool:
    """states辞書に対象のkeyがあるか調べる
        key:
        PATTERN_TEMP: int = 0    # 温度
        PATTERN_LUX: int = 1    # 日射量
        PATTERN_TIME: int = 2    # 時間

        検索対象辞書：
        states = {
            "0":[ [28.0, 30.0, 33.0, None, None], [70.0, 20.0, 5.0, None, None] ],
            "1":[ [3000, 4000, 5000, None, None], [60.0, 10.0, 0.0, None, None] ],
            "2":[['11:00', '13:00', 20],['19:00', '04:00', 10]]
        }

    Args:
        key (str): 検索キー
        states (dict): 検索対象辞書

    Returns:
        bool: 存在する:True
    """
    return key in states

def get_range(key: str, states: dict) -> list:
    """states辞書から対象keyを持つ辞書要素を取得する

    Args:
        key (str): 検索キー
        states (dict): 検索対象辞書

    Returns:
        list: 対象keyを持つ辞書要素、存在しないときは空リスト[]
        [ [3000, 4000, 5000, None, None], [60.0, 10.0, 0.0, None, None] ]
    """
    if has_key(key, states):
        return states[key]
    
    return []

def is_within_night_range(now: str, span: list) -> bool:
    """夜間時間範囲に、対象時間が含まれるか検査する

    Args:
        now (str): 検査対象時間
        span (list): 夜間時間範囲, [start, end]

    Returns:
        bool: True: 範囲内にある
    """
    if len(span) < 1:
        return False

    start_time = span[0]
    end_time = span[1]

    return start_time <= now <= "23:59" or "00:00" <= now <= end_time

def is_within_day_range(now: str, span: list) -> bool:
    """昼間時間範囲に、対象時間が含まれるか検査する

    Args:
        now (str): 検査対象時間
        span (list): 昼間時間範囲, [start, end]

    Returns:
        bool: True: 範囲内にある
    """
    if len(span) < 1:
        return False
    
    start_time = span[0]
    end_time = span[1]

    return start_time < end_time and  start_time <= now <= end_time

def get_daytime_range(key: str, states: dict) -> list:
    """states辞書から対象keyを持つ昼時間範囲（辞書要素）を取得する
    "2":[['11:00', '13:00', 20],['19:00', '04:00', 10]]
    
    Args:
        key (str): 
        states (dict): 検索対象辞書

    Returns:
        list: 昼時間範囲
        ex.['11:00', '13:00', 20]
        keyが存在しない場合-> []リスト
    """
    result = get_range(key, states)

    return result[0] if len(result) > 1 else []

def get_nighttime_range(key: str, states: dict) -> list:
    """states辞書から対象keyを持つ夜間時間範囲（辞書要素）を取得する
    "2":[['11:00', '13:00', 20],['19:00', '04:00', 10]]
    ⇒ ['19:00', '04:00', 10]
    
    Args:
        key (str): 
        states (dict): 検索対象辞書

    Returns:
        list: 夜間時間範囲
    """
    result = get_range(key, states)

    return result[1] if len(result) == 2 else []

def get_day_or_night_aperture(states: dict) -> int:
    """現在時刻から昼間時間または、夜間時間の開度を取得する

    Args:
        states (dict): 検索対象辞書
            states = {"0":[[28.0, 30.0, 33.0],[70.0, 20.0, 5.0]], 
                      "1":[[3000.0, 4000.0, 5000.0],[60.0, 20.0, 5.0]]}

    Returns:
        int: 昼間または、夜間時間開度
            時間範囲外の場合は、PATTERN_DISMISS(-1)
    """
    # 現在時間を取得 hh:mm形式
    now = datetime.now()
    now_hw = now.strftime("%H:%M")
    
    term = get_daytime_range(str(PATTERN_TIME), states)
    if is_within_day_range(now_hw, term) \
        or is_within_night_range(now_hw, term):
        #['11:00', '13:00', 20]
        return term[2]

    return PATTERN_DISMISS

def condition_judgement(
        now_degree: int, 
        degrees: list, 
        now_aperture: int, 
        apertures: list,
        min_aperture=100,
        max_aperture=0) -> int:
    """状態判定関数

    Args:
        now_degree (int): 現在の温度または、照度
        degrees (list): 温度範囲または、照度範囲 -> [30, 33, 35]
        now_aperture (int): 現在の開度
        apertures (list): 現在の温度または、照度から求めた開度範囲 -> [60, 40, 0]
        min_aperture (int): 現在温度または、照度が最低値未満の場合のデフォルト値 100
        max_aperture (int): 現在温度または、照度が最大値より大きい場合のデフォルト値 0

    Returns:
        int: 最新の開度
    """
    aperture = -1
    prev_degree = now_degree
    prev_aperture = now_aperture  # 現在の開度

    min_degree = min(degrees)
    max_degree = max(degrees)
    
    if now_degree < min_degree:
        return min_aperture #100
        # return prev_aperture
    elif now_degree > max_degree:
        return min(apertures)
        # return max_aperture #0

    for degree, aptr in zip(degrees, apertures):
        #print(f'\nnow_degree:{now_degree} degree:{degree} aptr:{aptr} prev_degree:{prev_degree} prev_aperture:{prev_aperture}')
        if now_degree < prev_degree:
            aperture = prev_aperture
            break
        elif now_degree == degree:
            aperture = aptr
            break;
        elif prev_degree <= now_degree < degree:
            aperture = prev_aperture
            break
        elif prev_degree < now_degree <= degree:
            aperture = aptr
            break
        elif now_degree > degree:
            prev_degree = degree
            prev_aperture = aptr
        else:
            break

    if aperture == -1:
        aperture = 0
    
    return aperture

def on_off_condition_judgement(
        now_degree: int, 
        degrees: list, 
        now_aperture: int, 
        apertures: list
    ) -> int:
    """オンオフ系状態判定関数
        returnにnotしているのは、condition_judgementが
        現在の温度が最大設定温度(stage)未満の時は１を返し,
        最大設定温度(stage)以上の場合は０を返すため
        モータを回すためには１を返す必要がるので、notする

    Args:
        now_degree (int): 現在の温度または、照度
        degrees (list): 温度範囲または、照度範囲 -> [30, 33, 35]
        now_aperture (int): 現在の開度
        apertures (list): 現在の温度または、照度から求めた開度範囲 -> [60, 40, 0]

    Returns:
        int: _description_
    """
    return not condition_judgement(
        now_degree, 
        degrees, 
        now_aperture, 
        apertures,
        min_aperture=1,
        max_aperture=0)

def get_aperture(id: str, value: float, now_aperture: float) -> float:
    """device_control_tableから、対象のIDをもつレコードを取得する
    取得したレコードの情報と現在の計測した温度または、照度と比較して、
    比較から得られた開度を求める。
    例.
        取得したレコードの情報
        degrees     =   [30, 33, 35]
        apertures   =   [60, 50, 20]

        計測した温度 32℃ 
        開度:50 (30< 計測した温度 <=33)

    Args:
        id (str): 対象とする制御機器ID
        value(float): 現在の環境測定値（温度、湿度、照度、水分...）
        now_aperture(float):現在の開度
        
    Returns:
        float: 開度（0≦開度≦100）
    """
    states = {}
    for pattern, stages, apertures in get_degrees_apertures(id):
        stg = [x for x in stages if (x != None) and (x != '')]
        aptr = [x for x in apertures if (x != None) and (x != '')]

        states[str(pattern)]=[stg, aptr]
        # states = {"0":[[28.0, 30.0, 33.0],[70.0, 20.0, 5.0]], 
        # "1":[[3000.0, 4000.0, 5000.0],[60.0, 20.0, 5.0]]}

    # PATTERN_TEMP: int = 0    # 温度
    # PATTERN_LUX: int = 1    # 日射量
    # PATTERN_TIME: int = 2    # 時間
    # PATTERN_DISMISS: int = -1    # データなし

    # states辞書のなかから、keyが時間である（key="2"）要素があるか検査する
    # "2":[ [11:00, 13:00, 10], [19:00, 4:00, 20] ]
    # もし存在すれば、これを最優先とし、この開度を返す。
    # 夜間の定義（気象庁）18時頃から翌日の午前６時頃まで。府県天気予報では日界が24時のため、18時頃から24時まで。別図参照。
    aperture = 0
    #print(f'converted states:{states}')
    if str(PATTERN_TIME) in states:
        aperture = get_day_or_night_aperture(states)
    # keyが日射量（key="1"）が含まれているときは、温度より先に、計測した照度を比較検証する。
    elif str(PATTERN_LUX) in states:
        return get_new_aperture(value, PATTERN_LUX, now_aperture, states)
        # list = get_range(str(PATTERN_LUX), states)
        # print(f'PATTERN_LUX:{stages}')
        # if list != []:
        #     aperture = condition_judgement(
        #         value, 
        #         list[0], # 照度リスト ex.[3000, 4000, 5000]
        #         now_aperture, 
        #         list[1])    # 開度リスト ex.[60.0, 20.0, 5.0]

        #     return aperture
    # 比較した結果、states辞書の照度範囲に入っていれば、照度に対応する開度を返す。

    # 現在の照度が範囲以外のときは、温度(PATTERN_TEMP=0)範囲から、対応する開度を返す。
    elif str(PATTERN_TEMP) in states:
        print(f'PATTERN_TEMP:{states}')
        return get_new_aperture(value, PATTERN_TEMP, now_aperture, states)
        # list = get_range(str(PATTERN_TEMP), states)
        # print(f'PATTERN_TEMP:{stages}')
        # if list != []:
        #     aperture = condition_judgement(
        #         value, 
        #         list[0],    # 温度リスト ex.[28.0, 30.0, 33.0]
        #         now_aperture, 
        #         list[1])    # 開度リスト ex.[70.0, 20.0, 5.0]

        #     return aperture
        
    # else:
    #     pass

    return aperture

def get_new_aperture(value: float, pattern_value: int, now_aperture: float, states: dict) -> float:
    """
    指定された値に基づいてアクチュエータの開度を計算します。
    Args:
        value (float): 現在のセンサー値（例: 温度）。
        PATTERN_value (int): パターン値。状態を特定するためのキーとして使用されます。
        now_aperture (float): 現在のアクチュエータの開度。
        states (dict): 状態を定義する辞書。パターン値に対応する温度リストと開度リストを含みます。
    Returns:
        float: 計算されたアクチュエータの開度。
    """
    # この関数の日本語ドキュメントを作成してください

    aperture = 0
    
    list = get_range(str(pattern_value), states)
    
    if list != []:
        aperture = condition_judgement(
            value, 
            list[0],    # 温度リスト ex.[28.0, 30.0, 33.0]
            now_aperture, 
            list[1])    # 開度リスト ex.[70.0, 20.0, 5.0]

    return aperture
