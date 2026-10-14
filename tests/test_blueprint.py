import yaml
from pathlib import Path
def test_public_blueprint_read_only_and_private_data_boundary():
    x=yaml.safe_load(Path("render.yaml").read_text())
    assert x["databases"][0]["plan"]=="free"
    svc=x["services"][0]
    assert svc["plan"]=="free"
    assert svc["healthCheckPath"]=="/health/ready"
    env={v["key"]:v for v in svc["envVars"]}
    assert env["CMPE_PUBLIC_READ_ONLY"]["value"]=="1"
    assert env["CMPE_REQUIRE_MIGRATIONS"]["value"]=="1"
    assert env["CMPE_DATABASE_URL"]["fromDatabase"]["property"]=="connectionString"
    assert not any("TOKEN" in z for z in env)
