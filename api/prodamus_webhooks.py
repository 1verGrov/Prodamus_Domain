import datetime
from fastapi import APIRouter, Request, HTTPException

from services.subscription import activate_subscription, log_subscribtion
from db_queries.queries_read import get_subscription_by_subscription_id, get_user_by_phone_number
from db_queries.queries_write import insert_phone_number_to_user, update_subscribtion_date
from handlers.admin import new_subscriber_message
from handlers.public import send_channel_invite
from dateutil import tz


from config.config import PRODAMUS_SECRET

from collections.abc import MutableMapping
import json

router = APIRouter()

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

@router.post("/webhook/prodamus")
async def prodamus_webhook(request: Request):
    try:
        # Получаем raw тело запроса
        raw_body = await request.body()

        # Парсим JSON данные
        try:
            json_data = json.loads(raw_body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON data")

        print(json_data)

        if json_data.get('payment_type') == 'Автоплатеж':
            subscription = json_data.get('subscription')
            if subscription['action_code'] == 'auto_payment':

                received_signature = request.headers.get("Sign")
                if not received_signature:
                    print("Signature not found")
                    raise HTTPException(400, "No signature provided")

                # Создаем HMAC-SHA256 подпись
                signature = await sign(json_data, PRODAMUS_SECRET)

                # Сравниваем с полученной подписью
                if received_signature != signature:
                    raise Exception('signature incorrect')

                user = get_user_by_phone_number(subscription['customer_phone'])
                 # 1. Парсим строку в datetime (считаем, что исходное время в MSK)
                msk_tz = tz.gettz('Europe/Moscow')  # или просто UTC+3
                date_next_payment_str = subscription['date_next_payment']
                date_next_payment_naive = datetime.datetime.strptime(date_next_payment_str, '%Y-%m-%d %H:%M:%S')
                date_next_payment_msk = date_next_payment_naive.replace(tzinfo=msk_tz)  # Добавляем пояс MSK

                # 2. Конвертируем в UTC
                date_next_payment_utc = date_next_payment_msk.astimezone(tz.UTC)  # или datetime.timezone.utc

                # 3. Добавляем 1 день
                new_date_utc = date_next_payment_utc + datetime.timedelta(days=1)
                telegram_id = user.telegram_id
                await update_subscribtion_date(telegram_id, new_date_utc)

                await new_subscriber_message(telegram_id=telegram_id, sub_type='автоплатеж')

                await log_subscribtion(
                    json_data=json_data,
                    telegram_id=telegram_id,
                    sub_id=None
                )

                return {"status": "ok"}

        else:
            # Проверка обязательных параметров
            if json_data.get("payment_status") != "success":
                print("Payment not completed")
                raise HTTPException(400, "Payment not completed")

            telegram_id = json_data.get("order_num", "").split("_")[0][1:]
            if not telegram_id:
                print("Telegram id not found")
                raise HTTPException(400, "No telegram_id")

            # Проверка и отсеивание новых атемптов
            sub = await get_subscription_by_subscription_id(json_data.get("order_num"))
            if sub:
                return {"status": "already exists"}

            received_signature = request.headers.get("Sign")
            if not received_signature:
                print("Signature not found")
                raise HTTPException(400, "No signature provided")

            # Создаем HMAC-SHA256 подпись
            signature = await sign(json_data, PRODAMUS_SECRET)

            # Сравниваем с полученной подписью
            if received_signature != signature:
                raise Exception('signature incorrect')

            if json_data.get("subscription") == '2430077':
                delta = 30
                sub_type = 'на 1 месяц'
            elif json_data.get("subscription") == '2430080':
                delta = 90
                sub_type = 'на 3 месяц'
            else:
                delta = 1
                sub_type = 'на 1 месяц'

            print(json_data.get("customer_phone"))

            # Активируем подписку
            await insert_phone_number_to_user(telegram_id=telegram_id, phone_number=json_data.get("customer_phone"))
            paid_until = datetime.datetime.utcnow() + datetime.timedelta(days=delta)
            print(json_data.get("subscription"))
            await activate_subscription(telegram_id=int(telegram_id), paid_until=paid_until,
                                        subscription_id=json_data.get("subscription")['id'], order_id= json_data.get("order_num"))

            await new_subscriber_message(telegram_id=telegram_id, sub_type=sub_type)

            await log_subscribtion(
                json_data=json_data,
                telegram_id=telegram_id,
                sub_id=json_data.get("subscription")
            )

            # Отправляем приглашение в канал
            await send_channel_invite(int(telegram_id))

            return {"status": "ok"}

    except HTTPException:
            raise
    except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(500, "Internal server error")