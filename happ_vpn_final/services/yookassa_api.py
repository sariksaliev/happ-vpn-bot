import os
from dotenv import load_dotenv
from yookassa import Configuration, Payment

# Загружаем переменные окружения
load_dotenv()

# Настройки ЮKassa
Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")


def create_payment(amount: int, description: str, return_url: str) -> dict:
    """
    Создаёт платёж через ЮKassa и возвращает ссылку на оплату.
    """
    try:
        payment = Payment.create({
            "amount": {
                "value": f"{amount}.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,

            # Полный чек для 54-ФЗ
            "receipt": {
                "customer": {
                    "email": "client@example.com"
                },
                "items": [
                    {
                        "description": description,
                        "quantity": "1.00",
                        "amount": {
                            "value": f"{amount}.00",
                            "currency": "RUB"
                        },
                        "vat_code": "1",
                        "payment_mode": "full_prepayment",  # способ расчёта — полная предоплата
                        "payment_subject": "service"        # предмет расчёта — услуга (VPN)
                    }
                ]
            }
        })

        return {
            "id": payment.id,
            "url": payment.confirmation.confirmation_url
        }

    except Exception as e:
        print(f"Ошибка ЮKassa: {e}")
        raise


def get_payment_status(payment_id: str) -> str:
    """
    Проверяет статус платежа (waiting_for_capture / succeeded / canceled)
    """
    payment = Payment.find_one(payment_id)
    return payment.status
