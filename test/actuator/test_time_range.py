from datetime import datetime

PATERN_TIME: int = 2    # 時間

def test_time_range():
    states = {
        "0":[ [28.0, 30.0, 33.0, None, None], [70.0, 20.0, 5.0, None, None] ],
	    "1":[ [3000, 4000, 5000, None, None], [60.0, 10.0, 0.0, None, None] ],
        "2":[['11:00', '13:00', 20],['19:00', '4:00', 10]]
    }

    times =[['11:00', '13:00', 20],['19:00', '4:00', 10]]
    
    assert has_key("2", states)
    assert times == get_time_range("2", states)
    # assert ['11:00', '13:00', 20] == get_time_range(str(PATERN_TIME), states)[0]
    # assert ['19:00', '4:00', 10] == get_time_range(str(PATERN_TIME), states)[1]
    assert ['11:00', '13:00', 20] == get_daytime_range(str(PATERN_TIME), states)
    assert ['19:00', '4:00', 10] == get_nighttime_range(str(PATERN_TIME), states)
    #assert is_within_night_range(['11:00', '13:00', 20])
    # assert is_within_range(['11:00', '13:00', 20])
    #assert check_include_time("2", states)

def ptest_nighttime_range():
    now = datetime.now()
    hw = now.strftime("%H:%M")
    assert is_within_night_range(hw, ['19:00', '04:00', 20]) #ok
    assert is_within_night_range("19:00", ['19:00', '04:00', 20]) #ok
    assert is_within_night_range("23:59", ['19:00', '04:00', 20]) #ok
    assert is_within_night_range("00:00", ['19:00', '04:00', 20]) #ok
    assert is_within_night_range("04:00", ['19:00', '04:00', 20]) #ok
    #assert is_within_night_range("18:00", ['19:00', '04:00', 20]) #ok
    assert is_within_night_range("05:00", ['19:00', '04:00', 20]) #ok

def ptest_daytime_range():
    assert is_within_day_range("11:00", ['11:00', '13:00', 20])
    assert is_within_day_range("12:00", ['11:00', '13:00', 20])
    assert is_within_day_range("13:00", ['11:00', '13:00', 20])
    #assert is_within_day_range("10:00", ['11:00', '13:00', 20]) #ok
    # assert is_within_day_range("14:00", ['11:00', '13:00', 20]) #ok
    hw = datetime.now().strftime("%H:%M")
    assert is_within_day_range(hw, ['11:00', '13:00', 20])

def has_key(key: str, states: dict):
    return key in states

def get_time_range(key: str, states: dict) -> list:
    if has_key(key, states):
        return states[key]
    
    return []

def get_daytime_range(key: str, states: dict) -> list:
    return get_time_range(key, states)[0]

def get_nighttime_range(key: str, states: dict) -> list:
    return get_time_range(key, states)[1]

def is_within_night_range(now, span: list):
    start_time = span[0]
    end_time = span[1]

    return start_time <= now <= "23:59" or "00:00" <= now <= end_time

def is_within_day_range(now, span: list):
    # now = datetime.now()
    # hw = now.strftime("%H:%M")
    start_time = span[0]
    end_time = span[1]

    return start_time < end_time and  start_time <= now <= end_time

def check_include_time(key: str, states: dict) -> bool:
    return False