from asyncio import run as run_async
from logng.logger import get_or_create_logger, LogConfig
from logng.outputs import VirtualAttyStdout, FileOutput

LOGGER = get_or_create_logger(
    config=LogConfig(
        stdouts=(
            VirtualAttyStdout,
            FileOutput("latest.log"),
        ),
        shared=True,
    )
)

from api.client import APIClient
from app.config import init_config


async def main() -> None:
    CONFIG = init_config()
    client = APIClient(CONFIG.url, CONFIG.account, CONFIG.pwd)
    await client.login()
    LOGGER.info("获取Cookie", "->", client.cookie)
    LOGGER.info(await client.chose_cls("web_xsxk/xfz_xsxk_fs1_zcxk.aspx", "Btxk$12"))


if __name__ == "__main__":
    run_async(main())
