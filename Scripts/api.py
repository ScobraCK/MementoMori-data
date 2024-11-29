from datetime import datetime
import json
import uuid
import re
import logging

import httpx
import msgpack

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

def get_version():
    vars_js_url = 'https://mememori-game.com/apps/vars.js'
    backup_html_url = 'https://mememori-game.com/apk/'
    base_url = 'https://mememori-game.com'
    
    try:
        # Try to get APK URL and version from vars.js
        logger.info(f"Trying vars.js")
        response = httpx.get(vars_js_url)
        response.encoding = 'utf-16'
        if response.status_code == 200:
            version_match = re.search(r"var apkVersion = '(.+?)';", response.text)
            if version_match:
                version = version_match.group(1)
                return version
    except Exception as e:
        logger.info(f"Failed to get version from vars.js: {e}")

    try:
        logger.info(f"Trying HTML")
        # Backup method: get APK name and version from HTML
        response = httpx.get(backup_html_url)
        response.encoding = 'utf-16'
        if response.status_code == 200:
            match = re.search(r'<a id="downloadApk" href="(.+?)"></a>', response.text)
            if match:
                apk_name = match.group(1)
                # Extract version from the APK path
                version_match = re.search(r'/apps/mementomori_(.+?).apk', apk_name)
                if version_match:
                    version = version_match.group(1)
                    return version
    except Exception as e:
        logger.info(f"Failed to get version from HTML: {e}")

    logger.info(f"Failed to get version.")
    return None

def generate_uuid():
    return str(uuid.uuid4()).replace("-", "")

ASSET_HEADERS = {
    "accept-encoding": "gzip, identity",
    "user-agent": "BestHTTP/2 v2.3.0",
    "content-length": "0",
    "pragma": "no-cache",
    "cache-control": "no-cache",
}

class API:
    auth_api: str
    ortegauuid: str
    headers: dict

    def __init__(self, version, auth_api="https://prd1-auth.mememori-boi.com", ortegauuid: str = None) -> None:
        self.version = version
        self.session = httpx.Client()
        self.auth_api = auth_api
        if ortegauuid is None:
            ortegauuid = generate_uuid()

        self.session.headers.update(
            {
                "content-type": "application/json; charset=UTF-8",
                "ortegaaccesstoken": "",
                "ortegaappversion": self.version,
                "ortegadevicetype": "7",
                "ortegauuid": ortegauuid,
                "accept-encoding": "gzip, identity",
                "user-agent": "BestHTTP/2 v2.3.0",
                "pragma": "no-cache",
                "cache-control": "no-cache",
            }
        )

    def request(self, uri: str, data: dict = None, method: str = "POST") -> dict:
        if data is None:
            data = {}
        res = self.session.request(
            method,
            uri,
            content=msgpack.packb(data),
        )
        res.raise_for_status()
        if self.auth_api in uri:
            self.server = res.headers["server"]
            self.ortegastatuscode = int(res.headers["ortegastatuscode"])
            self.orteganextaccesstoken = res.headers["orteganextaccesstoken"]
            self.ortegaassetversion = res.headers["ortegaassetversion"]
            self.ortegamasterversion = res.headers["ortegamasterversion"]
            self.ortegautcnowtimestamp = datetime.fromtimestamp(
                float(res.headers["ortegautcnowtimestamp"]) / 1000
            )

        return msgpack.unpackb(res.content, timestamp=3), res.headers

    def getDataUri(self):
        try:
            data, headers = self.request(f"{self.auth_api}/api/auth/getDataUri")
            # self.asset_catalog_uri_format = data["AssetCatalogUriFormat"]
            self.master_uri_format = data["MasterUriFormat"]
            self.notice_banner_image_uri_format = data.get("NoticeBannerImageUriFormat")
            self.asset_catalog_fixed_uri_format = data['AssetCatalogFixedUriFormat']
        except Exception as e:
            logger.info(e)
            logger.info("--------------------------")
            logger.info(data)
            logger.info("--------------------------")
        return data

    async def get_master(self, name: str, client: httpx.AsyncClient):
        uri = self.master_uri_format.format(self.ortegamasterversion, name)
        res = await client.get(uri, headers=ASSET_HEADERS)
        res.raise_for_status()
        return msgpack.unpackb(res.content, timestamp=3)

    async def get_master_catalog(self, client: httpx.AsyncClient):
        return await self.get_master("master-catalog", client)
    
    def get_notice(self, output, category=1, country='US', lang=2, access=0):
        uri = "https://prd1-auth.mememori-boi.com/api/notice/getNoticeInfoList"
        res = self.session.post(
            uri,
            headers=self.session.headers,
            content=msgpack.packb({
                "AccessType": access,  # 0 = None
                                       # 1 = Title
                                       # 2 = MyPage

                "CategoryType": category,  # 0 = EventTab
                                           # 1 = NoticeTab

                "CountryCode": country,  # (JP) Japan
                                         # (US) America
                                         # (KR) Korea
                                         # (TW) Taiwan

                "LanguageType": lang,  # 0 = None
                                       # 1 = jaJP
                                       # 2 = enUS
                                       # 3 = koKR
                                       # 4 = zhTW

                "UserId": 0,
            }),
        )
        res.raise_for_status()

        unpacked_data = msgpack.unpackb(res.content, timestamp=3)
    
        with open(output, 'w', encoding='utf-8') as f:
            f.write(json.dumps(unpacked_data, indent=4, ensure_ascii=False))
