from Remilia.sdb import DataBase, YamlStruct
from pydantic import BaseModel


class AppConfig(BaseModel):
    url: str = None
    account: str = None
    pwd: str = None


def init_config() -> AppConfig:
    _db = DataBase("", struct=YamlStruct).getCate("")
    if not _db.hasTable("config.yml"):
        _db.createTable("config.yml").writeKVS(
            {"url": "202.195.102.53", "account": "", "password": ""}
        )
    tb = _db.getTable("config.yml")
    url = "http://" + tb.readValueElse("url", None) + "/"
    account = tb.readValueElse("account", None)
    pwd = tb.readValueElse("password", None)
    if url is None or account is None or pwd is None:
        raise Exception("error config!")
    return AppConfig(url=url, account=account, pwd=pwd)
