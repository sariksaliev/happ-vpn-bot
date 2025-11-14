import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

# --- Настройки подключения к БД ---
DB_CONFIG = {
    "dbname": "happ_vpn",
    "user": "postgres",
    "password": "1002",      # при необходимости поменяй
    "host": "localhost",
    "port": 5432,
}

print("✅ db_postgres.py загружен из:", __file__)


def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=DictCursor)


# ==========================
# 🔹 Пользователи
# ==========================

def add_user(user_id, username, first_name, last_name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING;
                """,
                (user_id, username, first_name, last_name),
            )


def get_user_by_id(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
            return cur.fetchone()


# ==========================
# 🔹 VPN-ключи (таблица vpn_keys)
# ==========================

def add_vpn_key(tariff: str, key: str) -> int:
    """Добавить один ключ в таблицу vpn_keys."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO vpn_keys (tariff, key)
                VALUES (%s, %s)
                RETURNING id;
                """,
                (tariff, key),
            )
            return cur.fetchone()[0]


def mark_key_as_used(key: str, user_id: int):
    """Пометить ключ как использованный определённым пользователем."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE vpn_keys
                SET is_used = TRUE,
                    used_by_user_id = %s,
                    used_at = NOW()
                WHERE key = %s;
                """,
                (user_id, key),
            )


def count_free_keys(tariff_code: str) -> int:
    """Сколько свободных ключей осталось по тарифу."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM vpn_keys
                WHERE tariff = %s AND is_used = FALSE;
                """,
                (tariff_code,),
            )
            return cur.fetchone()[0]


def get_free_key(tariff_code: str, user_id: int) -> str | None:
    """
    Взять любой свободный ключ по тарифу и пометить его как использованный.
    Возвращает строку-ключ или None, если ключей нет.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, key
                FROM vpn_keys
                WHERE tariff = %s AND is_used = FALSE
                LIMIT 1;
                """,
                (tariff_code,),
            )
            row = cur.fetchone()
            if not row:
                return None

            key_id, key_value = row

            cur.execute(
                """
                UPDATE vpn_keys
                SET is_used = TRUE,
                    used_by_user_id = %s,
                    used_at = NOW()
                WHERE id = %s;
                """,
                (user_id, key_id),
            )
            conn.commit()
            return key_value


def get_user_keys(user_id: int):
    """Все ключи пользователя (из таблицы subscriptions)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.key, s.tariff_code, s.date_end
                FROM subscriptions s
                WHERE s.user_id = %s
                ORDER BY s.date_end DESC;
                """,
                (user_id,),
            )
            return cur.fetchall()


# ==========================
# 🔹 Подписки (таблица subscriptions)
# ==========================

def add_subscription(user_id, tariff_code, key, date_start, date_end):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO subscriptions (user_id, tariff_code, key, date_start, date_end)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (user_id, tariff_code, key, date_start, date_end),
            )


def get_user_subscriptions(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM subscriptions WHERE user_id = %s;",
                (user_id,),
            )
            return cur.fetchall()


# ==========================
# 🔹 Сервисная проверка
# ==========================

def init_db():
    """Проверка подключения при старте бота."""
    try:
        conn = get_connection()
        conn.close()
        print("✅ PostgreSQL подключение успешно установлено.")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")


# ==========================
# 🔹 Массовое добавление/удаление ключей (для админ-панели)
# ==========================

def add_many_keys(keys: list[str], tariff_code: str):
    """
    Массово добавить ключи в vpn_keys к конкретному тарифу.
    `keys` — список строк (каждый ключ отдельной строкой).
    """
    if not keys:
        return

    clean_keys = [k.strip() for k in keys if k.strip()]
    if not clean_keys:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO vpn_keys (tariff, key, is_used)
                VALUES (%s, %s, FALSE);
                """,
                [(tariff_code, k) for k in clean_keys],
            )
        conn.commit()


def delete_all_keys():
    """Удалить ВСЕ ключи из vpn_keys."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM vpn_keys;")
        conn.commit()


# ==========================
# 🔹 Статистика для админа
# ==========================

def count_users() -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users;")
            return cur.fetchone()[0]


def count_subscriptions() -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM subscriptions;")
            return cur.fetchone()[0]


def sum_payments() -> int:
    """
    Общая сумма всех оплат, считая по tariff_code.
    Цены «зашиты» в CASE, т.к. в таблице нет колонки amount.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(
                    SUM(
                        CASE tariff_code
                            WHEN '1m'  THEN 189
                            WHEN '3m'  THEN 449
                            WHEN '6m'  THEN 699
                            WHEN '12m' THEN 1499
                            ELSE 0
                        END
                    ), 0
                )
                FROM subscriptions;
                """
            )
            return cur.fetchone()[0]


def stats_last_24h() -> tuple[int, int, int]:
    """
    Статистика за последние 24 часа:
    - новых пользователей,
    - количество подписок,
    - сумма оплат.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(DISTINCT user_id) AS users,
                    COUNT(*) AS subs,
                    COALESCE(
                        SUM(
                            CASE tariff_code
                                WHEN '1m'  THEN 189
                                WHEN '3m'  THEN 449
                                WHEN '6m'  THEN 699
                                WHEN '12m' THEN 1499
                                ELSE 0
                            END
                        ), 0
                    ) AS income
                FROM subscriptions
                WHERE date_start >= NOW() - INTERVAL '24 hours';
                """
            )
            users, subs, income = cur.fetchone()
            return users, subs, income


def delete_keys_by_tariff(tariff_code: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM vpn_keys WHERE tariff = %s", (tariff_code,))
        conn.commit()


def count_keys_by_tariff(tariff_code: str) -> int:
    """
    Возвращает количество свободных ключей по конкретному тарифу.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM vpn_keys WHERE tariff = %s AND is_used = FALSE",
                (tariff_code,)
            )
            return cur.fetchone()[0]


def delete_keys_by_tariff(tariff_code):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM vpn_keys WHERE tariff = %s", (tariff_code,))
        conn.commit()
