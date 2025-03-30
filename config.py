from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "K'sFarmware"
    ORIGIN_FLSKR_URL: str = ""
    DATABASE_URL: str = 'sqlite:///../database/actuators_manage_db.sqlite'
    # 遮光カーテン自動、手動モード
    # mode (int): 1:自動運転中, 0:手動運転中, 9:停止中
    ACTUATOR_AUTO: int = 1
    ACTUATOR_MANUAL: int = 0
    ACTUATOR_STOPPED: int = 9
    ACTUATOR_FORCED_OPEN: int = 11
    ACTUATOR_FORCED_CLOSE: int = 19
    ACTUATOR_MODE: int = ACTUATOR_MANUAL
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
