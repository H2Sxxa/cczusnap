from typing import Dict, Optional
from aiohttp import ClientSession
from logng.logger import get_or_create_logger
from .header import HEADERS, cookie_fmt
from lxml.html import fromstring

LOGGER = get_or_create_logger()


class APIClient:
    account: str
    pwd: str
    url: str
    cookie: Optional[str] = None

    def __init__(self, url: str, account: str, pwd: str) -> None:
        self.url = url
        self.account = account
        self.pwd = pwd

    async def __asp_info(self, url: str, use_cookie=False) -> Dict[str, str]:
        async with ClientSession(
            headers=cookie_fmt(self.cookie) if use_cookie else HEADERS
        ) as Session:
            async with Session.get(url) as Resp:
                if Resp.status != 200:
                    return self.__asp_info(url, use_cookie)
                htmlxp = fromstring(await Resp.text())
                return {
                    "__VIEWSTATE": htmlxp.xpath('//input[@id="__VIEWSTATE"]/@value'),
                    "__VIEWSTATEGENERATOR": htmlxp.xpath(
                        '//input[@id="__VIEWSTATEGENERATOR"]/@value'
                    ),
                }

    async def _make_login_info(self) -> str:
        info = await self.__asp_info(self.url + "loginN.aspx")
        return {
            "username": self.account,
            "userpasd": self.pwd,
            "btLogin": "登录",
            "__VIEWSTATE": info["__VIEWSTATE"][0],
            "__VIEWSTATEGENERATOR": info["__VIEWSTATEGENERATOR"][0],
        }

    async def _make_chose_cls_info(self, url: str, target: str) -> str:
        info = await self.__asp_info(url, use_cookie=True)
        return {
            "__EVENTTARGET": "GVgxkbk",
            "__EVENTARGUMENT": target,
            "__VIEWSTATE": info["__VIEWSTATE"][0],
            "__VIEWSTATEGENERATOR": info["__VIEWSTATEGENERATOR"][0],
            "__ASYNCPOST": True,
            "__VIEWSTATEENCRYPTED": "",
        }

    async def unchose_cls(self, where: str, target: str) -> None:
        async with ClientSession(headers=cookie_fmt(self.cookie)) as Session:
            async with Session.post(
                self.url + where,
                data=await self._make_chose_cls_info(self.url + where, target),
            ) as Resp:
                LOGGER.info(Resp.status, await Resp.text())

    async def chose_cls(self, where: str, target: str) -> None:
        async with ClientSession(headers=cookie_fmt(self.cookie)) as Session:
            async with Session.post(
                self.url + where,
                data=await self._make_chose_cls_info(self.url + where, target),
            ) as Resp:
                if Resp.status != 200:
                    LOGGER.error("错误的状态码", Resp.status)
                    await self.chose_cls(where, target)
                else:
                    LOGGER.info(Resp.status, await Resp.text())

    def has_cookie(self) -> bool:
        return self.cookie is not None

    async def login(self) -> str:
        LOGGER.info("使用账户", self.account)
        async with ClientSession(headers=HEADERS) as Session:
            async with Session.post(
                self.url + "loginN.aspx",
                data=await self._make_login_info(),
                allow_redirects=False,
            ) as Resp:
                if Resp.status != 302:
                    LOGGER.error("错误的状态码", Resp.status)
                    LOGGER.error(Resp.headers)
                    LOGGER.warn("即将重试")
                    self.cookie = await self.login()
                else:
                    LOGGER.info("状态码", 302)
                    LOGGER.info(Resp.headers)
                    self.cookie = Resp.headers["Set-Cookie"]

    async def goto_table(self) -> None:
        if not self.has_cookie():
            return LOGGER.warn("Plz login first!")
        async with ClientSession(headers=cookie_fmt(self.cookie)) as Session:
            async with Session.get(self.url + "View/indexTablejw.aspx") as Resp:
                if Resp.status != 200:
                    LOGGER.error("错误的状态码", Resp.status)
                    await self.goto_table()
                else:
                    element = fromstring(await Resp.text())
                    LOGGER.info(
                        element.xpath(
                            "/html/body/form/div[3]/div[1]/div/div/span/text()"
                        )[0]
                    )
