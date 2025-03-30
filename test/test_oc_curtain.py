import sys, os

import pytest
# インポートさせたいディレクトリパスを取得する
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
print(f'path:{sys.path}')

from actuators.blackout_curtains.curtains import BlackoutCurtain

@pytest.mark.asyncio
async def open():
    bc = BlackoutCurtain('blkcrtn_01')
    await bc.open_curtain(2)
    return True

def close():
    bc = BlackoutCurtain('blkcrtn_01')
    bc.close_curtain(1)
    return True

@pytest.mark.asyncio
async def test_open_curtain():
    assert await open()