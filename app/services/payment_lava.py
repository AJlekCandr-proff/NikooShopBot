# Импорт необходимых модулей.
from aiohttp import ClientTimeout, ClientSession

from json import dumps

from hmac import new

from hashlib import sha256

from time import time

from random import randint

from secrets import token_hex

from app.bot_settings import settings


# Класс для работы с API платежной системы Lava.
class Lava:
    """"""
    def __init__(self, shop_id: str, secret_token: str) -> None:
        self.shop_id: str = shop_id
        self.secret: str = secret_token
        self.base_url: str = "https://api.lava.ru/"
        self.timeout: ClientTimeout = ClientTimeout(total=360)

    @classmethod
    def signature_headers(cls, data: dict[str, str | int], secret: str) -> dict[str, str]:
        json_str: bytes = dumps(data).encode()
        sign: str = new(bytes(secret, 'UTF-8'), json_str, sha256).hexdigest()
        headers: dict[str, str] = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Signature': sign
        }
        return headers

    async def create_invoice(self, amount: float, success_url: str) -> dict[str, dict[str, str]]:
        url: str = f"{self.base_url}/business/invoice/create"
        params: dict[str, str | int] = {
            "sum": amount,
            "shopId": self.shop_id,
            "successUrl": success_url,
            "orderId": f'{time()}_{token_hex(randint(5, 10))}',
            "comment": 'Пополнение баланса в профиле на нашем проекте!'
        }
        headers: dict[str, str | int] = self.signature_headers(data=params, secret=self.secret)

        async with ClientSession(headers=headers, timeout=self.timeout) as session:
            request = await session.post(url=url, headers=headers, json=params)
            response: dict[str, dict[str, str]] = await request.json()

            await session.close()

            return response

    async def status_invoice(self, invoice_id: str) -> bool:
        url: str = f"{self.base_url}/business/invoice/status"
        params: dict = {
            "shopId": self.shop_id,
            "invoiceId": invoice_id
        }
        headers: dict[str, str | int] = self.signature_headers(data=params, secret=self.secret)

        async with ClientSession(headers=headers, timeout=self.timeout) as session:
            request = await session.post(url=url, headers=headers, json=params)
            response: dict[str, dict] = await request.json()

            await session.close()

            return response['data']['status'] == "success"


API_Lava = Lava(secret_token=settings.TOKEN_LAVA.get_secret_value(), shop_id=settings.SHOP_ID.get_secret_value())
