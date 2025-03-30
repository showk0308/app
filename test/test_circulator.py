import sys, os

import pytest
# インポートさせたいディレクトリパスを取得する
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from actuators.circulation_fans.circulator import CirculatorFan
from base_actuators.calc_aperture import \
    get_aperture, \
    get_degrees_apertures, \
    condition_judgement

async def moving_fun() -> bool:
    cltr = CirculatorFan('crcltn_01')
    await cltr.turn_on(20)
    return True

@pytest.mark.asyncio
async def ptest_moving():
    assert await moving_fun()

def ptest_get__enviroment_values():
    cltr = CirculatorFan('crcltn_01')
    assert 30.7 == cltr.get_enviroment_values()

def ptest_get_aperture():
    aprt = get_aperture('crcltn_01', 5, 10)
    assert 100 == aprt

def ptest_get_toggle_mode():
    states = {}
    stg = []
    aptr = []
    for _, stages, apertures in get_degrees_apertures('crcltn_01'):
        # print(f'pattern:{pattern}')
        print(f'{stages=}')
        # print(f'apertures:{apertures}')
        stg = [x for x in stages if (x is not None) and (x != '')]
        aptr = [x for x in apertures if (x is not None) and (x != '')]
        print(f'{stg=}')
        print(f'{aptr=}')

    #     states[str(pattern)]=[stg, aptr]

    # print(f'result:{states}')
    # stages:[28.0, 30.0, '', None, None]
    # apertures:[0.0, 1.0, None, None, None]
    # stg:[28.0, 30.0]
    # aptr:[0.0, 1.0]
    # result:{'1': [[28.0, 30.0], [0.0, 1.0]]}
    # 現在の温度：29　現在のオンオフ：0
    assert 1 == condition_judgement(24, stg, 0, [1.0, 1.0], 0, 1)
    assert 0 == condition_judgement(20, stg, 0, [1.0, 1.0], 0, 1)
    assert 1 == condition_judgement(28, stg, 0, [1.0, 1.0], 0, 1)
    assert 1 == condition_judgement(30, stg, 0, [1.0, 1.0], 0, 1)
    assert 1 == condition_judgement(31, stg, 0, [1.0, 1.0], 0, 1)

@pytest.mark.asyncio
async def ptest_task():
    cltr = CirculatorFan('crcltn_01')
    await cltr.task(0, 0)
      
    assert True

def test_get_toggle_mode():
    cltr = CirculatorFan('crcltn_01')
    print(f'\n{cltr.get_toggle_mode(11)}')
    print(f'{cltr.get_toggle_mode(12)}')
    print(f'{cltr.get_toggle_mode(13)}')
    print(f'{cltr.get_toggle_mode(14)}')
    print(f'{cltr.get_toggle_mode(20)}')
