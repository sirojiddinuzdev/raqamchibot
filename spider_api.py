"""
Spider-service.com API bilan ishlash moduli
Asosiy: https://api.spider-service.com?apiKay=...
"""
import aiohttp
import logging

logger = logging.getLogger(__name__)

SPIDER_BASE_URL = "https://api.spider-service.com"


class SpiderAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_params = {"apiKay": api_key}

    async def _get(self, params: dict) -> dict:
        """Umumiy GET so'rov"""
        all_params = {**self.base_params, **params}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    SPIDER_BASE_URL,
                    params=all_params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    data = await response.json(content_type=None)
                    return data
        except Exception as e:
            logger.error(f"Spider API xatolik: {e}")
            return {"error": "CONNECTION_ERROR"}

    async def get_balance(self) -> float:
        """API hisobdagi balansni qaytaradi"""
        data = await self._get({"action": "getBalance"})
        if data.get("error") == "INFORMATION_SUCCESS":
            return float(data.get("result", {}).get("wallet", 0))
        return 0.0

    async def get_countries(self) -> dict:
        """Mavjud davlatlar va narxlarini qaytaradi"""
        data = await self._get({"action": "getCountrys"})
        if data.get("error") == "INFORMATION_SUCCESS":
            result = data.get("result", {})
            countries = result.get("countries", {})
            # countries[1] - Telegram uchun
            return countries.get(1, countries.get("1", {}))
        return {}

    async def get_number(self, country_code: str) -> dict | None:
        """Raqam sotib olish"""
        data = await self._get({"action": "getNumber", "country": country_code})
        if data.get("error") == "INFORMATION_SUCCESS":
            result = data.get("result", {})
            return {
                "number": result.get("phone"),
                "hash_code": result.get("hash_code"),
            }
        logger.warning(f"getNumber xatolik: {data}")
        return None

    async def get_code(self, hash_code: str) -> dict | None:
        """SMS kodni olish"""
        data = await self._get({"action": "getCode", "hash_code": hash_code})
        if data.get("error") == "INFORMATION_SUCCESS":
            result = data.get("result", {})
            return {
                "code": result.get("code"),
                "password": result.get("password", ""),
            }
        logger.warning(f"getCode xatolik: {data}")
        return None
