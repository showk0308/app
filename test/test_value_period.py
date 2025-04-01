import sys, os
# インポートさせたいディレクトリパスを取得する
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#print(f'path:{sys.path}')

from datetime import datetime
from base_actuators.calc_aperture import \
    get_daytime_range, \
    get_nighttime_range, \
    get_range, \
    has_key,\
    is_within_day_range, \
    is_within_night_range, \
    condition_judgement, \
    get_day_or_night_aperture, \
    get_aperture

PATERN_TIME: int = 2    # 時間

def ptest_time_range():
    states = {
        "0":[ [28.0, 30.0, 33.0, None, None], [70.0, 20.0, 5.0, None, None] ],
	    "1":[ [3000, 4000, 5000, None, None], [60.0, 10.0, 0.0, None, None] ],
        "2":[['11:00', '13:00', 20],['19:00', '04:00', 10]]
    }

    times =[['11:00', '13:00', 20],['19:00', '04:00', 10]]
    
    now = datetime.now().strftime("%H:%M")

    assert has_key(str(PATERN_TIME), states)
    assert times == get_range(str(PATERN_TIME), states)
    # assert ['11:00', '13:00', 20] == get_range(str(PATERN_TIME), states)[0]
    # assert ['19:00', '4:00', 10] == get_range(str(PATERN_TIME), states)[1]
    assert ['11:00', '13:00', 20] == get_daytime_range(str(PATERN_TIME), states)
    assert ['19:00', '04:00', 10] == get_nighttime_range(str(PATERN_TIME), states)
    assert is_within_night_range(now, ['19:00', '04:00', 20])
    assert is_within_day_range(now, ['11:00', '13:00', 20])
    #assert check_include_time("2", states)

def ptest_nighttime_range():
    now = datetime.now()
    hw = now.strftime("%H:%M")
    print(f'now:{hw}')
    # assert is_within_day_range(hw, ['11:00', '13:00', 0])
    assert is_within_night_range(hw, ['19:00', '04:00', 20])

    # assert is_within_night_range("19:00", ['19:00', '04:00', 20]) #ok
    # assert is_within_night_range("23:59", ['19:00', '04:00', 20]) #ok
    # assert is_within_night_range("00:00", ['19:00', '04:00', 20]) #ok
    # assert is_within_night_range("04:00", ['19:00', '04:00', 20]) #ok
    # assert not is_within_night_range("05:00", ['19:00', '04:00', 20]) #ok

def test_condition_judgement():
    # def condition_judgement(
    #         now_degree: int, 
    #         degrees: list, 
    #         now_aperture: int, 
    #         apertures: list) -> int:

    # 現在の照度：900　現在の開度：0
    # assert 30 == condition_judgement(900, [100.0, 300.0, 600.0, 800.0], 0, [90.0, 80.0, 50.0, 30])

    # 現在の照度：900　現在の開度：0
    # assert 50 == condition_judgement(721, [100.0, 300.0, 600.0, 800.0], 30, [90.0, 80.0, 50.0, 30])
    assert 1 == condition_judgement(22, [12, 14], 0, [0, 1], 0, 1)

    # 現在の照度：99　現在の開度：10
    # assert 10 == condition_judgement(99, [100.0, 200.0, 500.0], 10, [40.0, 15.0, 5.0])

    # 現在の照度：300　現在の開度：25
    # assert 15 == condition_judgement(300, [100.0, 200.0, 500.0], 25, [40.0, 15.0, 5.0])

    # 現在の照度：500　現在の開度：55
    # assert 5 == condition_judgement(500, [100.0, 200.0, 500.0], 55, [40.0, 15.0, 5.0])

    # 現在の照度：600　現在の開度：100
    # assert 0 == condition_judgement(501, [100.0, 200.0, 500.0], 100, [40.0, 15.0, 5.0])
    # assert 60 == condition_judgement(3500, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])
    # assert 88 == condition_judgement(2900, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])
    # assert 60 == condition_judgement(3000, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])
    # assert 20 == condition_judgement(4000, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])
    # assert 5 == condition_judgement(5000, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])
    # assert 0 == condition_judgement(5001, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])
    # assert 20 == condition_judgement(4001, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])
    # assert 60 == condition_judgement(3001, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])
    # assert 60 == condition_judgement(3000.1, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])
    # assert 60 == condition_judgement(3999.99, [3000.0, 4000.0, 5000.0], 88.0, [60.0, 20.0, 5.0])

def ptest_get_aperture():
    # Args:
    # id (str): 対象とする制御機器ID
    # value(float): 現在の環境測定値（温度、湿度、照度、水分...）
    # now_aperture(float):現在の開度

    # PATERN_LUX:[[100.0, 200.0, 250.0], [40.0, 10.0, 5.0]]
    assert 10 == get_aperture("blkcrtn_01", 5, 10)

def ptest_get_day_or_night_aperture():
    # states = {"0":[[28.0, 30.0, 33.0],[70.0, 20.0, 5.0]], "1":[[3000.0, 4000.0, 5000.0],[60.0, 20.0, 5.0]]}
    states = {"0":[[28.0, 30.0, 33.0],[70.0, 20.0, 5.0]], \
            "1":[[3000.0, 4000.0, 5000.0],[60.0, 20.0, 5.0]], \
            "2":[["11:00", "13:00", 0],[0, 0]]}

    assert 20 == get_day_or_night_aperture(states)

def ptest_get_daytime_range():
    #states = {"0":[[28.0, 30.0, 33.0],[70.0, 20.0, 5.0]], "1":[[3000.0, 4000.0, 5000.0],[60.0, 20.0, 5.0]]}
    states = {"0":[[28.0, 30.0, 33.0],[70.0, 20.0, 5.0]], \
            "1":[[3000.0, 4000.0, 5000.0],[60.0, 20.0, 5.0]], \
            "2":[["11:00", "13:00", 1],[0, 0]]}

    assert ["11:00", "13:00", 1] == get_daytime_range('2', states)

# def ptest_daytime_range():
#     assert is_within_day_range("11:00", ['11:00', '13:00', 20])
#     assert is_within_day_range("12:00", ['11:00', '13:00', 20])
#     assert is_within_day_range("13:00", ['11:00', '13:00', 20])
#     #assert is_within_day_range("10:00", ['11:00', '13:00', 20]) #ok
#     # assert is_within_day_range("14:00", ['11:00', '13:00', 20]) #ok
#     hw = datetime.now().strftime("%H:%M")
#     assert is_within_day_range(hw, ['11:0

# def has_key(key: str, states: dict):
#     return key in states

# def get_range(key: str, states: dict) -> list:
#     if has_key(key, states):
#         return states[key]
    
#     return []

# def get_daytime_range(key: str, states: dict) -> list:
#     return get_range(key, states)[0]

# def get_nighttime_range(key: str, states: dict) -> list:
#     return get_range(key, states)[1]

# def is_within_night_range(now, span: list):
#     start_time = span[0]
#     end_time = span[1]

#     return start_time <= now <= "23:59" or "00:00" <= now <= end_time

# def is_within_day_range(now, span: list):
#     # now = datetime.now()
#     # hw = now.strftime("%H:%M")
#     start_time = span[0]
#     end_time = span[1]

#     return start_time < end_time and  start_time <= now <= end_time

# def check_include_time(key: str, states: dict) -> bool:
#     return False