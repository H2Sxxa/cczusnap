from asyncio import run as run_async
from logng.logger import get_or_create_logger

from api.client import APIClient
from app.config import init_config

LOGGER = get_or_create_logger()


async def main() -> None:
    CONFIG = init_config()
    client = APIClient(CONFIG.url, CONFIG.account, CONFIG.pwd)
    await client.login()
    LOGGER.info("获取Cookie", "->", client.cookie)
    await client.chose_cls("web_xsxk/xfz_xsxk_fs1_zcxk.aspx","Btxk$12")#Bttk
#http://202.195.102.53/web_xsxk/ty_xsxk_xh_sql_new.aspx?dm=0003-008

if __name__ == "__main__":
    run_async(main())
