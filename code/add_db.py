import psycopg2

# Параметры подключения к базе данных
conn_params = {
    'host': 'localhost',
    'database': 'Practice',
    'user': 'postgres',
    'password': '123123',
    'port': '5432'
}

def create_tables():
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        # Создание таблицы roles, если не существует
        cur.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                role_name TEXT UNIQUE NOT NULL
            );
        """)

        # Создание таблицы users, если не существует
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role_id INTEGER REFERENCES roles(id),
                is_blocked BOOLEAN DEFAULT FALSE,
                fail_count INTEGER DEFAULT 0
            );
        """)

        # Вставка ролей, если они отсутствуют
        cur.execute("INSERT INTO roles (role_name) VALUES ('admin') ON CONFLICT (role_name) DO NOTHING;")
        cur.execute("INSERT INTO roles (role_name) VALUES ('user') ON CONFLICT (role_name) DO NOTHING;")

        # Вставка админа, если отсутствует
        cur.execute("""
            INSERT INTO users (login, password, role_id)
            SELECT 'admin', 'admin123', r.id
            FROM roles r
            WHERE r.role_name = 'admin'
            AND NOT EXISTS (SELECT 1 FROM users WHERE login = 'admin');
        """)

        conn.commit()
        print("База данных инициализирована успешно.")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_tables()