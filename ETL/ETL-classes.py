#!/usr/bin/env python3

import requests
import json
import psycopg2
from datetime import datetime
import getpass


# ===============================
# CONFIGURACIÓN DE CONEXIÓN
# ===============================
def get_db_config_from_user():
    """Pide credenciales al usuario"""
    dbname = 'user_management',
    user = input("Usuario de PostgreSQL: ")
    password = getpass.getpass("Contraseña: ")
    host = "localhost"
    port = "5432"

    return {
        'dbname': 'user_management',
        'user': user,
        'password': password,
        'host': 'localhost',
        'port': '5432'
    }



# ===============================
# CLASE BASE
# ===============================
class ETLBase:
    def __init__(self, db_config):
        self.db_config = db_config

    def connect_db(self):
        """Crea una conexión a PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = True
            return conn
        except Exception as e:
            print("❌ Error al conectar con la base de datos:", e)
            return None


# ===============================
# CLASE EXTRACTOR
# ===============================
class Extractor(ETLBase):
    def extract(self, num_users=10):
        """Extrae datos de la API Random User"""
        print("📥 Extrayendo datos de la API...")
        url = "https://randomuser.me/api/"
        results = []

        if num_users < 5000:
            response = requests.get(url, params={'results': num_users})
            results.extend(response.json()['results'])
        else:
            batches = num_users // 5000
            remainder = num_users % 5000
            for _ in range(batches):
                response = requests.get(url, params={'results': 5000})
                results.extend(response.json()['results'])
            if remainder > 0:
                response = requests.get(url, params={'results': remainder})
                results.extend(response.json()['results'])

        # necesario para debuggear y ver los datos extraídos
        #  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = f"temporary_raw_data_{timestamp}.json"
        # with open(filename, "w", encoding="utf-8") as f:
        #     json.dump(results, f, indent=2, ensure_ascii=False)
        # print(f"✅ Datos extraídos y guardados en {filename}")

        return results


# ===============================
# CLASE TRANSFORMADOR
# ===============================
class Transformer:
    def get_generation(self, year):
        """Determina la generación según la edad."""
        if year > 2012:
            return "alpha"
        elif year >= 1997 and year <= 2012:
            return "z"
        elif year >= 1981 and year <= 1996:
            return "millennial"
        elif year >= 1965 and year <= 1980:
            return "x"
        elif year >= 1946 and year <= 1964:
            return "baby_boomer"
        else:
            return "silent"

    def transform(self, raw_data):
        """Transforma los datos de la API"""
        print("🔄 Transformando datos...")
        transformed = []
        for u in raw_data:
            age = u['dob']['age']
            dob_year = int(u['dob']['date'][:4])
            generation = self.get_generation(dob_year)

            transformed.append({
                'uuid': u['login']['uuid'],
                'title': u['name']['title'],
                'first_name': u['name']['first'],
                'last_name': u['name']['last'],
                'gender': u['gender'],
                'email': u['email'],
                'dob': u['dob']['date'],
                'generation': generation,
                'nat': u['nat'],
                'phone': u['phone'],
                'cell': u['cell'],
                'state': u['location']['state'],
                'city': u['location']['city'],
                'street_number': u['location']['street']['number'],
                'street_name': u['location']['street']['name'],
                'postcode': u['location']['postcode'],
                'latitude': float(u['location']['coordinates']['latitude']),
                'longitude': float(u['location']['coordinates']['longitude']),
                'timezone_offset': u['location']['timezone']['offset'],
                'timezone_description': u['location']['timezone']['description'],
                'dni_name': u['id']['name'],
                'dni_value': u['id']['value'],
                'country': u['location']['country'],
                'age': age,
            })
        print(f"✅ {len(transformed)} usuarios transformados correctamente.")
        return transformed


# ===============================
# CLASE CARGADOR (LOAD)
# ===============================
class Loader(ETLBase):
    def load(self, data):
        print("💾 Cargando datos en la base de datos...")

        conn = self.connect_db()
        if not conn:
            print("❌ No se pudo establecer conexión.")
            return

        cur = conn.cursor()

        for u in data:
            try:

                # VERIFY IF THERE ARE DUPLICATE USERS
                cur.execute("SELECT value FROM dni WHERE value = %s;", (u['dni_value'],))
                dni_value_result = cur.fetchone()
                if dni_value_result:
                    dni_name_result = cur.execute("SELECT name FROM dni WHERE name = %s;", (u['dni_name'],))
                    if dni_name_result:
                        print("DNI value and name already exist, skipping user.")
                        continue

                cur.execute("SELECT email FROM users WHERE email = %s;", (u['email'],))
                result = cur.fetchone()
                if result:
                    print("Email existe, pasamos al siguiente usuario.")
                    continue
                
                # CREATE USERS
                cur.execute("""
                    INSERT INTO users (id, title, first_name, last_name, gender, email, dob, generation, nat, phone, cell)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (
                    u['uuid'], u['title'], u['first_name'], u['last_name'],
                    u['gender'], u['email'], u['dob'], u['generation'],  # 👈 generación agregada
                    u['nat'], u['phone'], u['cell']
                ))

                user_id = u['uuid']

                # ==========================
                # COUNTRY
                # ==========================
                cur.execute("SELECT id FROM country WHERE name = %s;", (u['country'],))
                result = cur.fetchone()

                if result: #aqui nos damos cuenta que el pais ya existe
                    country_id = result[0]
                else: #si no existe, lo insertamos
                    cur.execute("""
                        INSERT INTO country (id, name)
                        VALUES (uuid_generate_v4(), %s)
                        RETURNING id;
                    """, (u['country'],))
                    country_id = cur.fetchone()[0] #variable que conservamos para colocar en location
                    print(f"✅ País '{u['country']}' insertado con id {country_id}")

                # ==========================
                # LOCATION
                # ==========================
                cur.execute("""
                    INSERT INTO location (
                        id, country_id, user_id, state, city, street_number, street_name, postcode,
                        coord_latitude, coord_longitude, timezone_offset, timezone_description
                    )
                    VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    country_id, user_id, u['state'], u['city'], u['street_number'],
                    u['street_name'], u['postcode'], u['latitude'], u['longitude'],
                    u['timezone_offset'], u['timezone_description']
                ))

                # ==========================
                # DNI
                # ==========================
                cur.execute("""
                    INSERT INTO dni (id, user_id, name, value)
                    VALUES (uuid_generate_v4(), %s, %s, %s);
                """, (user_id, u['dni_name'], u['dni_value']))

                # ==========================
                # REGISTERS
                # ==========================
                cur.execute("""
                    INSERT INTO registers (id, user_id, date, age)
                    VALUES (uuid_generate_v4(), %s, CURRENT_TIMESTAMP, %s);
                """, (user_id, u['age']))

            except Exception as e:
                print(f"⚠️ Error insertando usuario {u['uuid']}: {e}")
                conn.rollback()
            else:
                conn.commit()

        cur.close()
        conn.close()
        print("✅ Datos cargados correctamente en PostgreSQL.")


# ===============================
# CLASE PRINCIPAL (PIPELINE)
# ===============================
class ETLPipeline:
    def __init__(self, db_config):
        self.extractor = Extractor(db_config)
        self.transformer = Transformer()
        self.loader = Loader(db_config)

    def run(self, num_users=10):
        print("🚀 Iniciando proceso ETL...")
        raw = self.extractor.extract(num_users)
        transformed = self.transformer.transform(raw)
        self.loader.load(transformed)
        print("🎯 Proceso ETL completado con éxito.")


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    db_config = get_db_config_from_user()
    num_users = int(input("¿Cuántos usuarios quieres obtener? "))
    pipeline = ETLPipeline(db_config)
    pipeline.run(num_users)
