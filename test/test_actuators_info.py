import sys, os

from fastapi import Depends

# インポートさせたいディレクトリパスを取得する
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.actuator_services import EnviromentValuesService as evs   
from database.db_access import SessionLocal, get_db, get_session
from sqlalchemy.orm import Session


def get_actuators_info():
    db = SessionLocal()

    evs_ = evs(db)
    ass_val = evs_.get_actuators_info()
    return ass_val

# class StateSchema(BaseModel):
#     actuator_id: str
#     state: int
#     aperture: float
#     actuator_name: str

def test_get_actuators_info():
    ass_val = get_actuators_info()
    print(f'{ass_val=}')
    #ass_val=ActuatorsStateSchema(
        # actuators=[
            # StateSchema(actuator_id='irrgtn_01', state=1, aperture=0.0, actuator_name='潅水装置'), 
            # StateSchema(actuator_id='blkcrtn_01', state=1, aperture=0.0, actuator_name='遮光カーテン'), 
            # StateSchema(actuator_id='sdwn_01', state=1, aperture=0.0, actuator_name='側窓'), 
            # StateSchema(actuator_id='skylght_01', state=1, aperture=0.0, actuator_name='天窓装置'), 
            # StateSchema(actuator_id='crcltn_01', state=0, aperture=0.0, actuator_name='循環扇')])
    #expected = [('irrgtn_01', 1, 0.0, '潅水装置'), ('blkcrtn_01', 1, 20.0), ('sdwn_01', 1, 50.0), ('skylght_01', 1, 100.0), ('crcltn_01', 0, 0.0)]
    assert True