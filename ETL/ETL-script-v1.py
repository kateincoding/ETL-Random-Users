import requests
import psycopg2
from psycopg2 import extras



def proceso_extraccion_data(num_user:int) -> list:
# 0. Definimos variables
    lista_usuarios = []


# 1. Construir la URL completa
    URL_BASE = "https://randomuser.me/api/"
    # La API maneja un máximo de 5000 resultados por petición
    if num_user > 5000:
        print("⚠️ Advertencia: El máximo de resultados por petición es 5000.")
        num_user = 5000

    # Usamos f-string para insertar el parámetro
    url_api = f"{URL_BASE}?results={num_user}"
    print(f"✅ URL construida: {url_api}")

# 2. Hacer la Petición HTTP (con urllib.request)
    data = requests.get(url=f'{url_api}')
    # Verificar el código de estado HTTP
    if  data.status_code == 200:
        lista_usuarios.extend(data.json()['results'])
    else:
        print("❌ Error comunicación de API.")        

    return lista_usuarios    

def proceso_transformar_data(user_list: list)-> list:
    lista_out = []
    for user in user_list:
        try:
            lista_out.append({
                    'uuid': user['login']['uuid'],
                    'title': user['name']['title'],
                    'first_name': user['name']['first'],
                    'last_name': user['name']['last'],
                    'gender': user['gender'],
                    'email': user['email'],
                    'dob': user['dob']['date'],
                    'nat': user['nat'],
                    'phone': user['phone'],
                    'cell': user['cell'],
                    'state': user['location']['state'],
                    'city': user['location']['city'],
                    'street_number': user['location']['street']['number'],
                    'street_name': user['location']['street']['name'],
                    'postcode': user['location']['postcode'],
                    'latitude': float(user['location']['coordinates']['latitude']),
                    'longitude': float(user['location']['coordinates']['longitude']),
                    'timezone_offset': user['location']['timezone']['offset'],
                    'timezone_description': user['location']['timezone']['description'],
                    'dni_name': user['id']['name'],
                    'dni_value': user['id']['value'],
                    'country': user['location']['country'],
                    'age': user['dob']['age'],
                    })    
        except Exception as e:
            print(f"⚠️ Error al procesar un registro: {e}. Saltando este usuario.")
            continue    
    return lista_out

def proceso_carga_data(user_list:list) -> bool:

    confirmar :bool

    if not user_list:
        print("No hay registros para insertar. Terminando.")
        return
    # --- Configuración de la Base de Datos (AJUSTA ESTOS VALORES) ---

    DB_CONFIG = {
    "host": "192.168.1.49",
    "database": "bdprueba",  # Reemplaza con el nombre de tu DB
    "user": "riccgogo",              # Reemplaza con el usuario que tiene permisos
    "password": "123456789", # Reemplaza con la contraseña
    }

    print(f"3. Conectando a PostgreSQL e insertando {len(user_list)} registros...")
    conn = None

    try:
            # Conexión a la BD
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            for u in user_list:
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
                                            coord_latitude, coord_longitude, timezone_offset, timezone_description,
                                                country)
                        VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        u['uuid'], u['state'], u['city'], u['street_number'],
                        u['street_name'], u['postcode'], u['latitude'], u['longitude'],
                        u['timezone_offset'], u['timezone_description'], u['country']
                    ))
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
                    confirmar = False
                    conn.rollback()
                else:
                    conn.commit()
                    confirmar = True
                    print(f"✅ Registro {u['uuid']} cargados correctamente en PostgreSQL.")           
    except (Exception, psycopg2.Error) as error:
            print(f"❌ Error al conectar o insertar en PostgreSQL: {error}")
            if conn:
                confirmar = False
                conn.rollback() # Revertir si hay error
                
    finally:
        if conn:
            cur.close()
            conn.close()
            print("   -> Conexión a PostgreSQL cerrada.")

    return confirmar


def proceso_principal( numero_user:int):

    lista_usuario=[]
    
    print("\n--- INICIO del proceso ETL ---")
    # 1. EXTRACT
    print("Extrayendo datos...")
    lista_usuario = proceso_extraccion_data( numero_user )
    if len(lista_usuario) > 0:
    # 2. TRANSFORM
        print("Transformando datos...")
        lista = proceso_transformar_data(lista_usuario)
        if len(lista) > 0:
    # 3. LOAD
            print("Cargando datos...")
            success = proceso_carga_data(lista)
            if success:
                print("\n--- FIN del proceso ETL: ÉXITO ---")
            else:
                print("\n--- FIN del proceso ETL: FALLO ---")



cantidad_user : int
cantidad_user = int(input("¿Cuántos usuarios deseas registrar?"))
proceso_principal(cantidad_user)