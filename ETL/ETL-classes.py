import requests
import json
import psycopg2
from datetime import datetime

# ===============================
# CONFIGURACIÓN DE CONEXIÓN
# ===============================
DB_CONFIG = {
    'dbname': 'user_management',
    'user': 'postgres',
    'password': 'tu_password',
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

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temporary_raw_data_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ Datos extraídos y guardados en {filename}")

        return results


# ===============================
# CLASE TRANSFORMADOR
# ===============================
class Transformer:
    def transform(self, raw_data):
        """Transforma los datos de la API"""
        print("🔄 Transformando datos...")
        transformed = []
        for u in raw_data:
            transformed.append({
                'uuid': u['login']['uuid'],
                'title': u['name']['title'],
                'first_name': u['name']['first'],
                'last_name': u['name']['last'],
                'gender': u['gender'],
                'email': u['email'],
                'dob': u['dob']['date'],
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
                'age': u['dob']['age'],
            })
        print(f"✅ {len(transformed)} usuarios transformados correctamente.")
        return transformed


# ===============================
# CLASE CARGADOR (LOAD)
# ===============================
class Loader(ETLBase):
    def load(self, data):
        """Inserta los datos transformados en PostgreSQL"""
        print("💾 Cargando datos en la base de datos...")

        conn = self.connect_db()
        if not conn:
            print("❌ No se pudo establecer conexión.")
            return

        cur = conn.cursor()
        for u in data:
            try:
                # Insertar en users
                cur.execute("""
                    INSERT INTO users (id, title, first_name, last_name, gender, email, dob, nat, phone, cell)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (
                    u['uuid'], u['title'], u['first_name'], u['last_name'],
                    u['gender'], u['email'], u['dob'], u['nat'], u['phone'], u['cell']
                ))

                # Insertar en location
                cur.execute("""
                    INSERT INTO location (id, user_id, state, city, sreet_number, street_name, postcode,
                                          coord_latitude, coord_longitude, timezone_offset, timezone_description)
                    VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    u['uuid'], u['state'], u['city'], u['street_number'],
                    u['street_name'], u['postcode'], u['latitude'], u['longitude'],
                    u['timezone_offset'], u['timezone_description']
                ))

                # Insertar en country (verificar si existe primero)
                cur.execute("SELECT id FROM country WHERE name = %s;", (u['country'],))
                country_result = cur.fetchone()
                
                if not country_result:
                    cur.execute("""
                        INSERT INTO country (id, location_id, name)
                        VALUES (uuid_generate_v4(), %s, %s) RETURNING id;
                    """, (u['uuid'], u['country']))
                    country_id = cur.fetchone()[0]
                    print(f"✅ País '{u['country']}' insertado")
                else:
                    country_id = country_result[0]
                    print(f"ℹ️ País '{u['country']}' ya existe")

                # Insertar en DNI
                cur.execute("""
                    INSERT INTO dni (id, user_id, name, value)
                    VALUES (uuid_generate_v4(), %s, %s, %s);
                """, (u['uuid'], u['dni_name'], u['dni_value']))

                # Insertar en registers
                cur.execute("""
                    INSERT INTO registers (id, user_id, date, age)
                    VALUES (uuid_generate_v4(), %s, CURRENT_TIMESTAMP, %s);
                """, (u['uuid'], str(u['age'])))

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
    num_users = int(input("¿Cuántos usuarios quieres obtener? "))
    pipeline = ETLPipeline(DB_CONFIG)
    pipeline.run(num_users)
    