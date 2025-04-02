import asyncio
from database.db_access import get_session
from models.actuator_models import ActuatorStates as ast
from sqlalchemy import and_, or_, not_
from actuators.circulation_fans.circulator import CirculatorFan
from actuators.blackout_curtains.curtains import BlackoutCurtain
from actuators.irrigation.base_irrigator import Irrigator
from actuators.irrigation.irrigator_line_1 import IrrigatorLine1
from actuators.irrigation.irrigator_line_2 import IrrigatorLine2
from actuators.side_windows.side_window_1 import SideWindow1

class ActuatorManager:
    """各制御機能を実行する
    ActuatorStates(actuator_states)テーブルに登録されている
    制御機能を実行する
    """
    def __init__(self, loop) -> None:
        self.actuator_dic = {}
        self.loop = loop
    
    def get_actuators_dic(self):
        """ActuatorStates(actuator_states)テーブルの
        class_name列にactuatorクラス名が登録されている
        レコードを抽出する
        その抽出結果を、idをキーとし、クラス名を値とする
        辞書を作成する
            {'blkcrtn_01': 'BlackoutCurtain', 'crcltn_01': 'CirculatorFan'}

        Returns:
            dict: {id: class_name, ...}
        """
        with get_session() as db:
            list = db.query(ast.actuator_id, ast.class_name, ast.aperture, ast.adjust_value) \
                        .filter(
                            and_(
                                ast.class_name != "",
                                ast.class_name is not None
                            )
                        ).all()
            db.commit()
            #filterd:[('blkcrtn_01', 'BlackoutCurtain', 10, 180), ('crcltn_01', 'CirculatorFan', -1, 0)]
            dic = {}
            for element in list:
                actuator_id, class_name, aperture, adjust_value = element
                dic[actuator_id] = (class_name, aperture, adjust_value)

            return dic

    async def execute_task(self):
        """作成した辞書
            {'blkcrtn_01': 'BlackoutCurtain', 'crcltn_01': 'CirculatorFan'}
        をもとに、クラス名からidを仮引数とするインスタンスを作成する
        そのインスタンスを非同期で実行する
        """
        self.actuator_dic = self.get_actuators_dic()
        print(f'actuator_dic:{self.actuator_dic}')

        task_list = []
        for key, value in self.actuator_dic.items():
            print(f'key:{key} value:{value}')
            # key: actuator_id
            # value[0]: Actuator Class Name
            # value[1]: now aperture
            # value[2]: adjust value
            class_name, now_aperture, adjust_value = value
            obj = eval(class_name)(key)
            tk = self.loop.create_task(obj.task(now_aperture, adjust_value))
            # obj = eval(value[0])(key)
            # tk = self.loop.create_task(obj.task(value[1], value[2])) # type: ignore
            task_list.append(tk)

        for tsk in task_list:
            await tsk
