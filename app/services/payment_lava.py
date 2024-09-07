from aiohttp import ClientTimeout, ClientSession

from json import dumps

from hmac import new

from hashlib import sha256

from time import time

from random import randint

from secrets import token_hex

from app.bot_settings import settings


class LavaAPI:
    def __init__(self, shop_id: str, api_token: str) -> None:
        """
        Класс работы с Lava API.
        Все методы преимущественно асинхронные.

        :param shop_id: ID проекта.
        :param api_token: API токен для работы с платежной системой.
        """

        self.shop_id: str = shop_id
        self.api_token: str = api_token
        self.base_url: str = "https://api.lava.ru/"
        self.timeout: ClientTimeout = ClientTimeout(total=360)

    @classmethod
    def signature_headers(cls, data: dict[str, str | int], api_token: str) -> dict[str, str]:
        """
        Метод формирования сигнатуры.

        :param data: Словарь хранящий данные запроса.
        :param api_token: API токен для работы с платежной системой.
        :return: Словарь-заголовок для дальнейшего создания запроса.
        """

        json_str: bytes = dumps(data).encode()
        sign: str = new(bytes(api_token, 'UTF-8'), json_str, sha256).hexdigest()
        headers: dict[str, str] = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Signature': sign
        }
        return headers

    async def create_invoice(self, amount: float) -> tuple[str, str]:
        """
        Асинхронный метод создания платежной ссылки для пользователя.

        :param amount: Сумма пополнения.
        :return: Кортеж из непосредственно платежной ссылки и ID платежна.
        """

        url: str = f"{self.base_url}/business/invoice/create"
        params: dict[str, str | int] = {
            "sum": amount,
            "shopId": self.shop_id,
            "successUrl": self.base_url,
            "orderId": f'{time()}_{token_hex(randint(5, 10))}',
            "comment": 'Пополнение баланса в профиле на нашем проекте!'
        }
        headers: dict[str, str | int] = self.signature_headers(data=params, api_token=self.api_token)

        async with ClientSession(headers=headers, timeout=self.timeout) as session:
            request = await session.post(url=url, headers=headers, json=params)
            response: dict[str, dict[str, str]] = await request.json()

            await session.close()

            return response['data']['url'], response['data']['id']

    async def status_invoice(self, invoice_id: str) -> bool:
        """
        Асинхронный метод проверки платежа.

        :param invoice_id: ID платежа.
        :return: Константа True/False.
        """

        url = f"{self.base_url}/business/invoice/status"
        params: dict = {"shopId": self.shop_id, "invoiceId": invoice_id}
        headers: dict[str, str | int] = self.signature_headers(data=params, api_token=self.api_token)

        async with ClientSession(headers=headers, timeout=self.timeout) as session:
            request = await session.post(url=url, headers=headers, json=params)
            response: dict[str, dict] = await request.json()

            await session.close()

            return response['data']['status'] == "success"


API_Lava = LavaAPI(api_token=settings.LAVA_API_TOKEN.get_secret_value(), shop_id=settings.SHOP_ID.get_secret_value())
