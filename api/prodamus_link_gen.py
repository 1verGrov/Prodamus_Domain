import aiohttp
from datetime import datetime, timedelta
from db_queries.queries_read import get_subscription_by_telegram_id, get_user_by_telegram_id

from config.config import BASE_LINK, PUBLIC_BOT_LINK, NOTIFICATION_LINK, PRODAMUS_SECRET #Базовый домен для оплаты зарегистрированный в продамусе

def prepare_prodamus_params(params: dict) -> dict:
    """
    Автоматически преобразует словарь параметров в формат, совместимый с Prodamus API.
    Особенно обрабатывает список `products` в products[0][name], products[0][price] и т. д.
    """
    prepared_params = {}

    for key, value in params.items():
        if key == "products" and isinstance(value, list):
            # Обработка списка товаров
            for i, product in enumerate(value):
                if not isinstance(product, dict):
                    continue
                for field, field_value in product.items():
                    prepared_params[f"products[{i}][{field}]"] = field_value
        else:
            prepared_params[key] = value

    return prepared_params

"""     В этом модуле собраны все взаимодействия с Prodamus-ом

            далее буду закоментированные все параметры
                необязательные для данной реализации
"""

"""     ГЕНЕРАЦИЯ ССЫЛКИ ДЛЯ ОПЛАТЫ       """
async def generate_payment_link(telegram_id: int, product_name: str, product_price: float,
                          product_quantity: int,
                          #,product_sku:str
                          # По необходимости можно передавать больше параметров, например,
                          customer_extra: str) -> str:

    if "1" in product_name:
        sub_id = 2430077
    elif "3" in product_name:
        sub_id = 2430080

    #sub_id = 2430073

    # Параметры массива products, Лучше формировать его не в этой части кода, Так сделано для наглядности
    """ Логику формирование массива можно менять,
            но НЕЛЬЗЯ менять структуру      """
    products = [
        {
            # Обязательные параметры
            "name":product_name, # наименование товара
            "price":product_price, # цена товара
            "quantity":product_quantity, # количество товара
            # Необязательные параметры
            #"sku":product_sku
        }
    ]

    params = {
        # Обязательные параметры при формировании ссылки
        "do": "link", # параметры:link передаёт ссылку для оплаты, pay:является ссылкой для оплаты
        "sys": "anishamilk_blog", # код системы интернет-магазина (необходимо согласовать с поддержкой Продамуса)
        "products": products, # Товары
        # Необязательные параметры
        #order_sum:... # Полная сумма заказа
        #discount_value:... # Размер скидки в рублях

            # Обязательный параметр для рекуррентных платежей
        "subscription": sub_id, # Только int, id подписки
            # Необязательный параметр для рекуррентных платежей
        "subscription_date_start":datetime.now().strftime("%Y-%m-%d %H:%M"), # дата начала подписки в формате "гггг-мм-дд чч:мм"
        # "subscription_demo_period": int()  # количество дней демо-периода подписки
        # "subscription_limit_autopayments": int() # максимальное количество авто-платежей по подписке

            # Параметры для пользователей Вк, являются НЕобязательными
        #"vk_user_id":... # id пользователя в системе Вк
        #"vk_user_name":... # ФИО пользователя в системе Вк

            # Параметры передающие данные о юр. статусе плательщика
            # !!! НАДО ЕСЛИ ПОКУПАТЕЛИ НЕ ФИЗ. ЛИЦА
            # ЧТО УЗНАТЬ ПАРАМЕТРЫ ЛУЧШЕ, ОБРАТИТЕСЬ К ДОКУМЕНТАЦИИ
        #"npd_income_type":... # тип плательщика
        #"npd_income_inn":... # инн плательщика
        #"npd_income_company":... # название компании плательщика

            # Общие Необязательные параметры

        "order_id": f"t{telegram_id}_{datetime.now().strftime('%Y%m%d%H%M')}", # номер заказа в Вашей системе, Способ формирование может быть любым
        #"customer_phone":..., # номер телефона клиента
        #"customer_email":..., # e-mail адрес клиента
        "customer_extra": customer_extra, # описание заказа (Поле дополнительные данные)
        #"ref":..., # идентификатор партнера (ПРОМОКОД)
        #"paid_content":..., # платный контент
        "link_expired": (datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"), # срок действия ссылки в формате "гггг-мм-дд чч:мм"
        #"payment_method":..., # метод оплаты
        #"available_payment_methods":..., # Список доступных методов оплаты
        "urlReturn":PUBLIC_BOT_LINK+'/payment_canceled', # URL-адрес для возврата пользователя без оплаты
        "urlSuccess":PUBLIC_BOT_LINK+'/payment_success', # URL-адрес для возврата пользователя при успешной оплате
        "urlNotification":NOTIFICATION_LINK, # служебный URL-адрес для уведомления интернет-магазина о поступлении оплаты по заказу
        #"_param_хххх":..., # произвольный сквозной параметр, где хххх - имя вашего произвольного параметра
        #"utm_хххх":..., # сквозной параметр в виде utm-метки, где хххх - имя вашей метки
        #"installments_disabled":..., # отключение рассрочки
        #"demoFlow":..., # Параметр для проверки негативного сценария с отказом по рассрочке
        #"demo_mode": 1, # Если передано значение 1, то платеж пройдет в демо-режиме
        #"type":..., # Если передано значение json, то ответ от Продамуса придет в формате json
        "callbackType":"json", # Если передано значение json, то веб-хуки от Продамуса будут приходить в формате json
        #"currency":..., # Валюта платежа.
        "payments_limit":1, # Лимит оплат по сформированной ссылке
        #"acquiring":..., # Эквайринг.
    }

    prepared_params = prepare_prodamus_params(params)

    # Если в return надо передавать ссылку после параметра do=link
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(BASE_LINK, params=prepared_params) as response:
                response.raise_for_status()  # Проверяем HTTP-ошибки
                return await response.text()
        except aiohttp.ClientError as e:
            print(f"Ошибка при запросе к Prodamus: {e}")
            raise


"""     ГЕНЕРАЦИЯ ССЫЛКИ ДЛЯ ОТМЕНЫ ПОДПИСКИ       """

import aiohttp
from datetime import datetime

from collections.abc import MutableMapping
import json

async def deep_int_to_string(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, MutableMapping):
            await deep_int_to_string(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            for k, v in enumerate(value):
                await deep_int_to_string({str(k): v})
        else: dictionary[key] = str(value)

async def sign(data, secret_key):
    import hashlib
    import hmac
    import json

    # переводим все значения data в string c помощью кастомной функции deep_int_to_string (см ниже)
    await deep_int_to_string(data)

    # переводим data в JSON, с сортировкой ключей в алфавитном порядке, без пробелом и экранируем бэкслеши
    data_json = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).replace("/", "\\/")

    # создаем подпись с помощью библиотеки hmac и возвращаем ее
    return hmac.new(secret_key.encode('utf8'), data_json.encode('utf8'), hashlib.sha256).hexdigest()


async def generate_cancel_link(telegram_id: int) -> dict:
    user = await get_user_by_telegram_id(telegram_id)
    subscription = await get_subscription_by_telegram_id(telegram_id)

    payload = {
        "subscription": subscription.subscription_id,
        "active_manager": 0,
        "active_user": 0,
        "customer_phone": user.phone_number,
    }

    # Генерируем подпись и добавляем в payload
    payload['signature'] = await sign(payload, PRODAMUS_SECRET)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    BASE_LINK + "rest/setActivity/",
                    data=payload,  # Отправляем как form-urlencoded
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'text/html'  # Ожидаем text/html в ответе
                    }
            ) as response:
                response.raise_for_status()

                # Получаем текст ответа и вручную обрабатываем
                response_text = await response.text()
                try:
                    return {"raw_response": response_text}  # или парсим как нужно
                except Exception as e:
                    print(f"Не удалось обработать ответ: {e}")
                    return {"error": "Invalid response format", "raw_response": response_text}

        except aiohttp.ClientError as e:
            print(f"Ошибка при отмене подписки: {e}")
            raise