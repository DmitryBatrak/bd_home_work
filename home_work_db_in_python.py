import psycopg2
import os.path

dotenv_config =  "config.env"
if os.path.exists(dotenv_config):
    load_dotenv(dotenv_config)

data_base = os.getenv("data_base")
user = os.getenv("user")
password = os.getenv("password")

def error_handling(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except psycopg2.DatabaseError as err:
            print(f"Error: {err}")
            if self.conn:
                self.conn.rollback()
    return wrapper

class ClientManagement:
    def __init__(self, *, data_base: str, user: str, password: str) -> None:
        self.data_base = data_base
        self.user = user
        self.password = password
        self.conn = psycopg2.connect(database=self.data_base, user=self.user, password=self.password)
        self.cursor = self.conn.cursor()


    @error_handling
    def create_data_base(self):
        with self.conn:
            self.cursor.execute("""
                    DROP TABLE IF EXISTS client_first_name, client_last_name, email_address, telephone_number;

                    CREATE TABLE IF NOT EXISTS client_first_name (
                        id SERIAL PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE
                    );

                    CREATE TABLE IF NOT EXISTS telephone_number (
                        id SERIAL PRIMARY KEY,
                        client_id INTEGER NOT NULL REFERENCES client_first_name(id),
                        telephone BIGINT UNIQUE
                    );
                """)
            self.conn.commit()

    @error_handling
    def add_new_client(self, *, first_name_client: str, last_name_client: str, email: str, telephone=None) -> None:
        with self.conn:
            self.cursor.execute("""
                INSERT INTO client_first_name(first_name, last_name, email)  VALUES (%s, %s, %s) RETURNING id;
            """, (first_name_client, last_name_client, email))
            client_id = self.cursor.fetchone()[0]

            if telephone:
                self.cursor.execute("""
                    INSERT INTO telephone_number(client_id, telephone) VALUES (%s, %s);
                """, (client_id, telephone))

            self.conn.commit()

    @error_handling
    def add_telephone(self, *, client_id: int, telephone: int) -> None:
        with self.conn:
            self.cursor.execute("""
                INSERT INTO telephone_number(client_id, telephone) VALUES (%s, %s);
            """, (client_id, telephone))

            self.conn.commit()


    @error_handling
    def refresh(self, *, client_id: int, first_name_client=None, last_name_client=None, email=None, old_telephone=None,
                new_telephone=None) -> None:
        with self.conn:
            if first_name_client:
                self.cursor.execute("""
                    UPDATE client_first_name SET first_name = %s WHERE id = %s;
                """, (first_name_client, client_id))

            if last_name_client:
                self.cursor.execute("""
                    UPDATE client_first_name SET last_name = %s WHERE id = %s;
                """, (last_name_client, client_id))

            if email:
                self.cursor.execute("""
                    UPDATE client_first_name SET email = %s WHERE id = %s;
                """, (email, client_id))

            if old_telephone and new_telephone:
                self.cursor.execute("""
                    UPDATE telephone_number SET telephone = %s WHERE client_id = %s AND telephone = %s;
                """, (new_telephone, client_id, old_telephone))

            self.conn.commit()


    @error_handling
    def delete_telephone(self, *, telephone_for_delete: int) -> None:
        with self.conn:
            self.cursor.execute("""
                DELETE FROM telephone_number WHERE telephone = %s;
            """, (telephone_for_delete, ))

        self.conn.commit()


    @error_handling
    def delete_client(self, *, client_id: int) -> None:
        with self.conn:
            self.cursor.execute("""
                DELETE FROM client_first_name WHERE id = %s;
            """, (client_id, ))

        self.conn.commit()


    @error_handling
    def find_client(self, *, first_name_client=None, last_name_client=None, email=None, telephone=None) -> list:
        base_query = """
                SELECT first_name, last_name, email, telephone
                  FROM client_first_name
                  JOIN telephone_number ON client_first_name.id = telephone_number.client_id
                  """

        if email:
            base_query += f"WHERE email = %s"
            final_query = (base_query, email)
        elif telephone:
            base_query += f"WHERE telephone = %s"
            final_query = (base_query, telephone)
        elif first_name_client and last_name_client:
            base_query += f"WHERE first_name = %s AND last_name = %s"
            final_query = (base_query, first_name_client, last_name_client)
        elif last_name_client:
            base_query += f"WHERE last_name = %s"
            final_query = (base_query, last_name_client)
        elif first_name_client:
            base_query += f"WHERE first_name = %s"
            final_query = (base_query, first_name_client)

        with self.conn:
            self.cursor.execute(final_query[0], (final_query[1], ))
            search_result = self.cursor.fetchall()
            return search_result


    def close_connection(self) -> None:
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    Manager = ClientManagement(data_base=data_base, user=user, password=password)
    Manager.create_data_base()
    Manager.add_new_client(first_name_client="Дмитрий", last_name_client="Батрак", email="dmitry@gmail.com")
    Manager.add_new_client(first_name_client="Юлия", last_name_client="Ковалевская", email="julia@gmail.com")
    Manager.add_new_client(first_name_client="Кот", last_name_client="Барсик", email="cat@gmail.com", telephone=765432107)
    Manager.add_telephone(client_id=2, telephone=766655544)
    Manager.add_telephone(client_id=2, telephone=733322211)
    Manager.add_telephone(client_id=2, telephone=799988877)
    Manager.refresh(client_id=2, last_name_client="Батрак", old_telephone=766655544, new_telephone=711122233)
    Manager.delete_telephone(telephone_for_delete=733322211)
    Manager.delete_client(client_id=1)
    print(Manager.find_client(last_name_client="Батрак"))
    Manager.close_connection()