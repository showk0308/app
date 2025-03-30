from contextlib import contextmanager
from requests import Session
from base_actuators import Actuator

class MotorActuator(Actuator):
    def __init__(self, id: str, ot: float) -> None:
        """モーターを制御する機器共通クラス

        Args:
            id (str): 器機ID
            ot (float): 全開時間（単位：秒）
        """
        super().__init__(id)
        self.full_opening_times = ot