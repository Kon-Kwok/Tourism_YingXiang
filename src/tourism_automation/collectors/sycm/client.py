"""HTTP client helpers for SYCM homepage collection."""

from __future__ import annotations

from urllib.parse import urlencode

from tourism_automation.shared.chrome import ChromeHttpClient


class SycmHomeClient:
    def __init__(self, http: ChromeHttpClient | None = None):
        self.http = http or ChromeHttpClient.from_local_chrome()

    def fetch_home_payloads(self, biz_date: str):
        return (
            self.http.fetch_json(
                _build_path(
                    "/portal/coreIndex/new/overview/v3.json",
                    {
                        "needCycleCrc": "true",
                        "dateType": "day",
                        "dateRange": f"{biz_date}|{biz_date}",
                    },
                ),
                referer="https://sycm.taobao.com/portal/home.htm",
            ),
            self.http.fetch_json(
                _build_path(
                    "/portal/coreIndex/new/trend/v3.json",
                    {
                        "dateType": "day",
                        "dateRange": f"{biz_date}|{biz_date}",
                    },
                ),
                referer="https://sycm.taobao.com/portal/home.htm",
            ),
            self.http.fetch_json(
                _build_path(
                    "/portal/coreIndex/new/getTableData/v3.json",
                    {
                        "dateType": "day",
                        "dateRange": f"{biz_date}|{biz_date}",
                    },
                ),
                referer="https://sycm.taobao.com/portal/home.htm",
            ),
        )


def _build_path(path: str, params: dict[str, str]) -> str:
    return f"{path}?{urlencode(params)}"
