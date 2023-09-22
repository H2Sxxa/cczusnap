from typing import Dict


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36"
}


def cookie_fmt(cookie: str) -> Dict[str, str]:
    t = HEADERS.copy()
    t["Cookie"] = cookie
    return t


