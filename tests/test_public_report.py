import hashlib
import json
import pytest
from cmpe.public_report import build_demo, compile_report, validate_series, publish
from cmpe.worldbank import INDICATORS
from cmpe.archive import archive_bytes

def test_dashboard_is_reproducible(tmp_path):
    report=build_demo()
    a=tmp_path/"a";b=tmp_path/"b"
    digest=publish(report,a)
    assert publish(report,b)==digest
    raw=(a/"data.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==digest
    assert (a/"index.html").exists()
    assert json.loads(raw)["status"].startswith("FICTIONAL")

def test_physical_series_unit_validation():
    s=[{"location":"USA","indicator":"EG.ELC.PROD.KH","unit":"kWh","period":"2014","value":10.0}]
    assert validate_series(s,"USA","EG.ELC.PROD.KH")
    with pytest.raises(ValueError):
        validate_series(s+s,"USA","EG.ELC.PROD.KH")
    s[0]["unit"]="USD"
    with pytest.raises(ValueError):
        validate_series(s,"USA","EG.ELC.PROD.KH")

def test_archive_is_content_addressed_and_idempotent(tmp_path,monkeypatch):
    monkeypatch.delenv("CMPE_ARCHIVE_BUCKET",raising=False)
    monkeypatch.setenv("CMPE_ARCHIVE_DIR",str(tmp_path))
    first=archive_bytes(b'{"version":1}',namespace="public")
    assert first["sha256"]==hashlib.sha256(b'{"version":1}').hexdigest()
    assert archive_bytes(b'{"version":1}',namespace="public")==first

def test_missing_physical_measurements_fail_closed():
    s=[{"location":"USA","indicator":"EG.ELC.ACCS.ZS","unit":"percent of population","period":"2020","value":90.0}]
    with pytest.raises(ValueError):
        compile_report([("USA","EG.ELC.ACCS.ZS",s,"a"*64)])
