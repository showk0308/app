import sys, os

from fastapi import Depends

# インポートさせたいディレクトリパスを取得する
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.actuator_services import EnviromentValuesService as evs   
from database.db_access import SessionLocal, get_db, get_session
from sqlalchemy.orm import Session


def get_device_step_values(id:str):
    db = SessionLocal()

    evs_ = evs(db)
    val = evs_.get_device_step_values(id)
    return val

def test_get_actuators_info():
    vals = get_device_step_values('blkcrtn_01')
    print(f'{vals=}')
    assert True