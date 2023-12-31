from typing import List
from Remilia.sdb import DataBase, YamlStruct
from logng.shared import info
from pydantic import BaseModel


class AppConfig(BaseModel):
    url: str = None
    account: str = None
    pwd: str = None
    targets: List[str] = []


class TargetInfo(BaseModel):
    web: str = ""
    webname: str = ""
    names: List[str] = []
    ids: List[str] = []


# [load("web_xsxk/xfz_xsxk_gnxz.aspx?dm=0003-004",name_inclued=["太极"],id_included=["Select$1"])]


def load_targets(targets: List[str]) -> List[TargetInfo]:
    def _load(web: str = None, name_included=[], id_included=[]):
        return TargetInfo(web=web, names=name_included, ids=id_included)

    return [eval(t, {"load": _load}) for t in targets]


def init_config() -> AppConfig:
    _db = DataBase("", struct=YamlStruct).getCate("")
    if not _db.hasTable("config.yml"):
        _db.createTable("config.yml").writeKVS(
            {
                "url": "202.195.102.53",
                "account": "",
                "password": "",
                "targets": [
                    'load(web="web_xsxk/xfz_xsxk_gnxz.aspx?dm=0003-004",name_included=["太极"],id_included=["Select$1"])'
                ],
            }
        )
        info("已生成配置文件config.yml，请填写后重启")
        exit(0)
    tb = _db.getTable("config.yml")
    url = tb.readValueElse("url", "")
    account = tb.readValueElse("account", "")
    pwd = tb.readValueElse("password", "")
    targets = tb.readValueElse("targets", [])

    if url == "" or account == "" or pwd == "":
        raise Exception("error config!")
    return AppConfig(
        url="http://" + url + "/", account=account, pwd=pwd, targets=targets
    )
