from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

engine = create_engine(settings.DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine, checkfirst=False)

# 手動潅水専用設定時刻　潅水装置IDひとつにつき、１つの設定時刻を持つ
MANUAL_IRRIGATION_TIME: str = '99:99'

# Dependency
# yield を使ってデータベースセッションを返すことで、ジェネレーターとして機能します。
# ジェネレーターは内部状態を保持します。yield の前のコードが実行され、その状態が保持されます。
# 例えば、トランザクションの途中でエラーが発生した場合、finally ブロックでセッションを閉じることができます。
# 総じて、yield を使うことで、データベースセッションを効率的に管理でき、リソースの最適な利用が可能になります。 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_session():
    """DBセッションコンテキストマネージャ
    with ブロックを組み合わせて使うことによって、
    データーベースセッションのリソースの解放を行なうコードを実装する

    Yields:
        SessionLocal: sqlite3 DBセッション
    """
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise 
    finally:
        db.close()
