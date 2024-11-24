import psycopg2
import os.path

dotenv_config =  "config.env"
if os.path.exists(dotenv_config):
    load_dotenv(dotenv_config)

data_base = os.getenv("data_base")
user = os.getenv("user")
password = os.getenv("password")

class ClientManagement:
    def __init__(self, *, data_base: str, user: str, password: str) -> None:
        self.data_base = data_base
        self.user = user
        self.password = password
        self.conn = psycopg2.connect(database=self.data_base, user=self.user, password=self.password)
        self.cursor = self.conn.cursor()


    def create_data_base(self) -> None:
        try:
            with self.conn:
                self.cursor.execute("""
                    DROP TABLE IF EXISTS client_first_name, client_last_name, email_address, telephone_number;

                    CREATE TABLE IF NOT EXISTS client_first_name (
                        id SERIAL PRIMARY KEY,
                        first_name TEXT NOT NULL
                        );

                    CREATE TABLE IF NOT EXISTS client_last_name (
                        id INTEGER PRIMARY KEY REFERENCES client_first_name(id),
                        last_name TEXT NOT NULL
                        );

                    CREATE TABLE IF NOT EXISTS email_address (
                        id INTEGER PRIMARY KEY REFERENCES client_first_name(id),
                        email TEXT NOT NULL UNIQUE
                        );

                    CREATE TABLE IF NOT EXISTS telephone_number (
                        id SERIAL PRIMARY KEY,
                        client_id INTEGER NOT NULL REFERENCES client_first_name(id),
                        telephone INTEGER UNIQUE
                        );
                """)
                self.conn.commit()
        except psycopg2.DatabaseError as err:
            print(f"Error: {err}")
            self.conn.rollback()


    def add_new_client(self, *, first_name_client: str, last_name_client: str, email: str, telephone=None) -> None:
        try:
            with self.conn:
                self.cursor.execute("""
                    INSERT INTO client_first_name(first_name) VALUES (%s) RETURNING id;
                """, (first_name_client,))
                client_id = self.cursor.fetchone()[0]

                self.cursor.execute("""
                    INSERT INTO client_last_name(id, last_name) VALUES (%s, %s);
                """, (client_id, last_name_client))

                self.cursor.execute("""
                    INSERT INTO email_address(id, email) VALUES (%s, %s);
                """, (client_id, email))

                if telephone:
                    self.cursor.execute("""
                        INSERT INTO telephone_number(client_id, telephone) VALUES (%s, %s);
                    """, (client_id, telephone))

                self.conn.commit()
        except psycopg2.DatabaseError as err:
            print(f"Error: {err}")
            self.conn.rollback()


    def add_telephone(self, *, client_id: int, telephone: int) -> None:
        try:
            with self.conn:
                self.cursor.execute("""
                    INSERT INTO telephone_number(client_id, telephone) VALUES (%s, %s);
                """, (client_id, telephone))

                self.conn.commit()
        except psycopg2.DatabaseError as err:
            print(f"Error: {err}")
            self.conn.rollback()


    def refresh(self, *, client_id: int, first_name_client=None, last_name_client=None, email=None, old_telephone=None,
                new_telephone=None) -> None:
        try:
            with self.conn:
                if first_name_client:
                    self.cursor.execute("""
                        UPDATE first_name_client SET first_name = %s WHERE id = %s;
                    """, (first_name_client, client_id))

                if last_name_client:
                    self.cursor.execute("""
                        UPDATE client_last_name SET last_name = %s WHERE id = %s;
                    """, (last_name_client, client_id))

                if email:
                    self.cursor.execute("""
                        UPDATE email_address SET email = %s WHERE id = %s;
                    """, (email, client_id))

                if old_telephone and new_telephone:
                    self.cursor.execute("""
                        UPDATE telephone_number SET telephone = %s WHERE client_id = %s AND telephone = %s;
                    """, (new_telephone, client_id, old_telephone))

                self.conn.commit()
        except psycopg2.DatabaseError as err:
            print(f"Error: {err}")
            self.conn.rollback()


    def delete_telephone(self, *, telephone_for_delete: int) -> None:
        try:
            with self.conn:
                self.cursor.execute("""
                    DELETE FROM telephone_number WHERE telephone = %s;
                """, (telephone_for_delete, ))

            self.conn.commit()
        except psycopg2.DatabaseError as err:
            print(f"Error: {err}")
            self.conn.rollback()


    def delete_client(self, *, client_id: int) -> None:
        try:
            with self.conn:
                self.cursor.execute("""
                    DELETE FROM telephone_number WHERE client_id = %s;
                    DELETE FROM email_address WHERE id = %s;
                    DELETE FROM client_last_name WHERE id = %s;
                    DELETE FROM client_first_name WHERE id = %s;
                """, (client_id, client_id, client_id, client_id))

            self.conn.commit()
        except psycopg2.DatabaseError as err:
            print(f"Error: {err}")
            self.conn.rollback()


    def find_client(self, *, first_name_client=None, last_name_client=None, email=None, telephone=None) -> list:
        try:
            with self.conn:
                self.cursor.execute("""
                    SELECT first_name, last_name, email, telephone
                      FROM client_first_name
                      JOIN client_last_name ON client_first_name.id = client_last_name.id
                      JOIN email_address ON client_first_name.id = email_address.id
                      JOIN telephone_number ON client_first_name.id = telephone_number.client_id
                     WHERE first_name = %s OR last_name = %s OR email = %s OR telephone = %s;
                """, (first_name_client, last_name_client, email, telephone))

                search_result = self.cursor.fetchall()
                return search_result

        except psycopg2.DatabaseError as err:
            print(f"Error: {err}")
            self.conn.rollback()


    def close_connection(self) -> None:
        self.cursor.close()
        self.conn.close()


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