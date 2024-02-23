from typing import Dict, List, Optional, TypeVar
from aiohttp import ClientSession
from logng.shared import info, error, warn
from .header import HEADERS, cookie_fmt
from lxml.html import fromstring
from pydantic import BaseModel
from traceback import format_exc

__F = TypeVar("__F")


def AsyncRetry(func: __F) -> __F:
    async def _(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error(e)
            error(format_exc())
            await _(*args, **kwargs)

    return _


def SyncRetry(func: __F) -> __F:
    def _(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error(e)
            _(*args, **kwargs)

    return _


class ClassInfo(BaseModel):
    target_dy: str = ""
    target_td: str = ""
    target: str = ""
    name: str = ""


class TableInfo(BaseModel):
    name: str = ""
    table_id: str = ""
    target: str = ""


class APIClient:
    account: str
    pwd: str
    url: str
    cookie: Optional[str] = None

    def __init__(self, url: str, account: str, pwd: str) -> None:
        self.url = url
        self.account = account
        self.pwd = pwd

    @AsyncRetry
    async def __asp_info(self, url: str, use_cookie=False) -> Dict[str, str]:
        async with ClientSession(
            headers=cookie_fmt(self.cookie) if use_cookie else HEADERS
        ) as Session:
            async with Session.get(url) as Resp:
                if Resp.status != 200:
                    return await self.__asp_info(url, use_cookie)
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

    async def _make_chose_info(self, url: str, target: str, arg: str) -> str:
        info = await self.__asp_info(url, use_cookie=True)
        return {
            "__EVENTTARGET": target,
            "__EVENTARGUMENT": arg,
            "__VIEWSTATE": info["__VIEWSTATE"][0],
            "__VIEWSTATEGENERATOR": info["__VIEWSTATEGENERATOR"][0],
            "__ASYNCPOST": True,
            "__VIEWSTATEENCRYPTED": "",
        }

    @AsyncRetry
    async def unchose_cls(self, where: str, ci: ClassInfo) -> None:
        async with ClientSession(headers=cookie_fmt(self.cookie)) as Session:
            async with Session.post(
                self.url + where,
                data=await self._make_chose_cls_info(
                    self.url + where, ci.target, ci.target_td
                ),
            ) as Resp:
                info(Resp.status, await Resp.text())

    @AsyncRetry
    async def list_cls(self, where: str) -> List[ClassInfo]:
        res = list()
        async with ClientSession(headers=cookie_fmt(self.cookie)) as Session:
            async with Session.get(self.url + where) as Resp:
                if Resp.status != 200:
                    error("状态码错误，重试")
                    return await self.list_cls(where)
                elements = fromstring(await Resp.text()).xpath('//*[@class="dg1-item"]')

                def __doPostBack(target, t_id):
                    return target, t_id

                for e in elements:
                    t, dy = eval(
                        e.xpath('//input[@value="选课" or @value="选 课"]/@onclick')[
                            0
                        ].split("javascript:")[-1],
                        {"__doPostBack": __doPostBack},
                    )
                    try:
                        _, td = eval(
                            e.xpath(
                                '//input[@value="退选" or @value="退 选"]/@onclick'
                            )[0].split("javascript:")[-1],
                            {"__doPostBack": __doPostBack},
                        )
                    except Exception as e:
                        td = None

                    res.append(
                        ClassInfo(
                            name=e.xpath("td[2]/text()")[0],
                            target=t,
                            target_dy=dy,
                            target_td=td,
                        )
                    )
        return res

    @AsyncRetry
    async def chose_cls(self, where: str, ci: ClassInfo) -> str:
        async with ClientSession(headers=cookie_fmt(self.cookie)) as Session:
            async with Session.post(
                self.url + where,
                data=await self._make_chose_info(
                    self.url + where, ci.target, ci.target_dy
                ),
            ) as Resp:
                if Resp.status != 200:
                    error("错误的状态码", Resp.status)
                    return await self.chose_cls(where, ci.target, ci.target_dy)
                else:
                    info(Resp.status)
                    raw = await Resp.text()
                    try:
                        return raw.split("alert('")[-1].split("')//]]>")[0]
                    except Exception as e:
                        error(e)
                        warn(raw)
                        return "No callback alert!"

    def has_cookie(self) -> bool:
        return self.cookie is not None

    @AsyncRetry
    async def login(self) -> str:
        info("使用账户", self.account)
        async with ClientSession(headers=HEADERS) as Session:
            async with Session.post(
                self.url + "loginN.aspx",
                data=await self._make_login_info(),
                allow_redirects=False,
            ) as Resp:
                if Resp.status != 302:
                    error("错误的状态码", Resp.status)
                    error(Resp.headers)
                    warn("即将重试")
                    self.cookie = await self.login()
                else:
                    info("状态码", 302)
                    info(Resp.headers)
                    self.cookie = Resp.headers["Set-Cookie"]

    @AsyncRetry
    async def list_tables(self) -> List[TableInfo]:
        res = []
        async with ClientSession(headers=cookie_fmt(self.cookie)) as Session:
            async with Session.get(
                self.url + "web_xsxk/gx_ty_xkfs_xh_sql.aspx"
            ) as Resp:
                if Resp.status != 200:
                    error("错误的状态码", Resp.status)
                    await self.list_tables()
                raw = await Resp.text()
                element = fromstring(raw)
                info(
                    "当前用户 ->", element.xpath('//span[@class="LableCss"]/text()')[0]
                )
                items = element.xpath('//tr[@class="dg1-item"]')

                def __doPostBack(target, t_id):
                    return target, t_id

                for i in items:
                    t, tid = eval(
                        i.xpath('//input[@value="选 择"]/@onclick')[0].split(
                            "javascript:"
                        )[-1],
                        {"__doPostBack": __doPostBack},
                    )
                    res.append(
                        TableInfo(
                            name=i.xpath(
                                "td[4]/text()",
                            )[0],
                            table_id=tid,
                            target=t,
                        )
                    )
                return res

    @AsyncRetry
    async def visit_table(self, _info: TableInfo) -> str:
        _info = await self._make_chose_info(
            self.url + "web_xsxk/gx_ty_xkfs_xh_sql.aspx", _info.target, _info.table_id
        )
        async with ClientSession(headers=cookie_fmt(self.cookie)) as Session:
            async with Session.post(
                self.url + "web_xsxk/gx_ty_xkfs_xh_sql.aspx",
                data=_info,
                allow_redirects=True,
            ):
                # TODO Can't get anything useful here, fuck the CCZU
                pass
