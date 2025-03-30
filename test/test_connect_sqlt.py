# import sys, os

# import pytest
# # インポートさせたいディレクトリパスを取得する
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from contextlib import contextmanager
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
#from config import settings
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

#DB_URL: str = 'sqlite:///../database/actuators_manage_db.sqlite'
#DB_URL: str = 'sqlite:////192.168.10.4/home/pi/Develop/flaskr/enviroments_db.sqlite'
DB_URL: str = 'sqlite:////192.168.10.4/home/pi/Develop/flaskr/enviroments_db.sqlite'

engine = create_engine(DB_URL, connect_args={'check_same_thread': False})
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine, checkfirst=False)

# CREATE TABLE "env_table" (
# 	"id"	INTEGER,
# 	"temperature"	REAL,
# 	"humidity"	REAL,
# 	"lux"	REAL,
# 	"moisture"	REAL,
# 	"builder_cd"	TEXT,
# 	"created"	TIMESTAMP DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
# 	"updator_cd"	TEXT,
# 	"modified"	TIMESTAMP DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
# 	PRIMARY KEY("id" AUTOINCREMENT)
# );

class EnvTbl(Base):
    __tablename__ = 'env_table'
    
    id = Column(Integer, primary_key=True)
    temperature = Column(Float)
    humidity = Column(Float)
    lux = Column(Float)
    moistur = Column(Float)
    builder_cd = Column(String)
    created = Column(DateTime(timezone=True))   # 作成年月日時刻
    updator_cd	= Column(String)            # 更新者コード
    modified = Column(DateTime(timezone=True))   # 更新年月日時刻

@contextmanager
def get_session():
    """DBセッションコンテキストマネージャ
    with ブロックを組み合わせて使うことによって、
    データーベースセッションのリソースの解放を行なうコードを実装する

    Yields:
        SessionLocal: sqlite3 DBセッション
    """
    db = session()
    try:
        yield db
    except:
        db.rollback()
        raise 
    finally:
        db.close()

def connect_db():
    with get_session() as db:
        enviroments = db.query(EnvTbl).first()
    
    for env in enviroments:
        print(env.id, env.teperature)
    
def test_connect_db():
    connect_db()
    assert True