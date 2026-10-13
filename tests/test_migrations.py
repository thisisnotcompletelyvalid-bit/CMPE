import os
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine,inspect,text

def test_migration_on_empty_and_preexisting_database(tmp_path, monkeypatch):
    from cmpe.db import Base
    for existing in (False,True):
        path=tmp_path/("old.sqlite" if existing else "new.sqlite")
        url="sqlite:///"+str(path)
        eng=create_engine(url)
        if existing:Base.metadata.create_all(eng)
        eng.dispose()
        monkeypatch.setenv("CMPE_DATABASE_URL",url)
        cfg=Config("alembic.ini")
        command.upgrade(cfg,"head")
        command.upgrade(cfg,"head")
        eng=create_engine(url)
        assert "alembic_version" in inspect(eng).get_table_names()
        with eng.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar()=="0001_initial"
        eng.dispose()
