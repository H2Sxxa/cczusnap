from asyncio import run as run_async
from logng.logger import get_or_create_logger, LogConfig
from logng.outputs import VirtualAttyStdout, FileOutput

LOGGER = get_or_create_logger(
    config=LogConfig(
        stdouts=(
            VirtualAttyStdout,
            FileOutput("latest.log", encoding="utf-8"),
        ),
        shared=True,
    )
)

from api.client import APIClient
from app.config import init_config, load_targets


async def main() -> None:
    CONFIG = init_config()
    client = APIClient(CONFIG.url, CONFIG.account, CONFIG.pwd)
    await client.login()
    targets = load_targets(CONFIG.targets)
    LOGGER.info("获取Cookie", "->", client.cookie)
    for t in targets:
        LOGGER.info("访问", t.web)
        clses = await client.list_cls(t.web)
        for i in t.ids:
            for c in clses:
                if i == c.target_dy:
                    LOGGER.info("捕获", c)
                    LOGGER.info(await client.chose_cls(t.web, c))
        for n in t.names:
            for c in clses:
                if n in c.name:
                    LOGGER.info("捕获", c)
                    LOGGER.info(await client.chose_cls(t.web, c))


if __name__ == "__main__":
    run_async(main())
