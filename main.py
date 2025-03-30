import uvicorn
import asyncio
import threading
from actuator_manager import ActuatorManager
from config import settings
from fastapi import FastAPI
from api.endpoints.actuator_endpoints import router as api_router
from database.db_access import engine, Base
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

def run_web_server():
    """Fastapi実行

    Returns:
        json: RESTでの処理結果
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("startup event")
        engine.connect()
        yield
        print("shutdown event")
        engine.dispose()
    
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    
    origins = [
        settings.ORIGIN_FLSKR_URL,
        # "http://192.168.10.4:5000",
    ]
        # allow_origins=["*"],
        # allow_origins=origins,

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    
    # sqliteアクセスにあたり、テーブルを作成する
    Base.metadata.create_all(bind=engine)

    #print('api_router')
    app.include_router(api_router)

    # print('start fastapi..')
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")

async def main(loop):
    """各制御装置オブジェクトを起動する
    ここには、Fastapiは含まれていない。
    Fastapiは別スレッドで起動する。

    Args:
        loop (EventLoop): 非同期処理実行オブジェクト
    """
    am = ActuatorManager(loop)
    await am.execute_task()

if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main(loop))
        loop.run_forever()
    except KeyboardInterrupt:
        print('exit')
    finally:
        loop.close()
