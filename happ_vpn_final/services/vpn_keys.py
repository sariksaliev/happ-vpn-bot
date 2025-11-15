from happ_vpn_final.happ_vpn_final.database.db_postgres import add_vpn_key, count_free_keys, get_free_key

# --- Тестовые ключи для первичного наполнения базы ---
INITIAL_KEYS = {
    "1m": [
        "KYNV6619SECHOC21",
        "FOP995RDVDKN8JZC",
        "IOK1QJE79ZEFPKG8",
        "BADVZF4ATJ4N4Z8V",
    ],
    "3m": [
        "HAPP-3M-KEY-001",
        "HAPP-3M-KEY-002",
    ],
    "6m": [
        "HAPP-6M-KEY-001",
        "HAPP-6M-KEY-002",
    ],
    "12m": [
        "HAPP-12M-KEY-001",
        "HAPP-12M-KEY-002",
    ],
}


def seed_keys_if_empty():
    """
    Добавляет тестовые ключи в таблицу vpn_keys, если для тарифа нет свободных.
    """
    for tariff, keys in INITIAL_KEYS.items():
        if count_free_keys(tariff) == 0:
            for k in keys:
                add_vpn_key(tariff, k)


__all__ = ["seed_keys_if_empty", "get_free_key"]
