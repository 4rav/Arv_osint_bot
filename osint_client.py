import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = os.getenv("OSINT_BASE_URL", "https://osint.stormx.pw/index.cpp")
API_KEY = os.getenv("OSINT_API_KEY", "dark")

def make_session():
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=1,
                    status_forcelist=[429,500,502,503,504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

def lookup_number(number: str, timeout: int = 15):
    s = make_session()
    params = {"key": API_KEY, "number": number}
    try:
        resp = s.get(BASE, params=params, timeout=timeout)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}
    except requests.HTTPError as e:
        r = getattr(e, "response", None)
        return {"error":"http", "status": getattr(r, "status_code", None), "text": getattr(r, "text", str(e))}
    except Exception as e:
        return {"error":"exception", "message": str(e)}
