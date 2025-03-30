import sys, os

import pytest
# インポートさせたいディレクトリパスを取得する
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime

def test_is_ittigation_time():
    current_time = datetime.now().strftime('%H:%M:00')
    print(f'{current_time=}')

    assert '22:05:00' == current_time
