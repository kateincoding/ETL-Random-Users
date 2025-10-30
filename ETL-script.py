import requests
import json
import csv
from datetime import datetime

def extract_data(num_users=10):
    """Extrae datos de la API Random User"""
    url = f"https://randomuser.me/api/"
    all_results = []
    if num_users < 5000:
        response = requests.get(url,  params={'results' : num_users})
        all_results.extend(response.json()['results'])
    else:
        batches = num_users // 5000
        remainder = num_users % 5000
        for _ in range(batches):
            response = requests.get(url, params={'results': 5000})
            all_results.extend(response.json()['results'])
        if remainder > 0:
            response = requests.get(url, params={'results': remainder})
            all_results.extend(response.json()['results'])
    
    # Guardar response en JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"temporary_raw_data_{timestamp}.json", 'w', encoding='utf-8') as file:
        json.dump(all_results, file, indent=2, ensure_ascii=False)
    print(f"Response guardado en: raw_data_{timestamp}.json")
    
    return all_results

def transform_data(raw_data):
    """Transforma los datos extraídos"""
    transformed = []
    for user in raw_data:
        transformed.append({
            'first_name': user['name']['first'],
            'last_name': user['name']['last'],
            'gender': user['gender'],
            'title': user['name']['title'],
            'street_number': user['location']['street']['number'],
            'street_name': user['location']['street']['name'],
            'city': user['location']['city'],
            'state': user['location']['state'],
            'country': user['location']['country'],
            'postcode': user['location']['postcode'],
            'latitude': user['location']['coordinates']['latitude'],
            'longitude': user['location']['coordinates']['longitude'],
            'timezone_offset': user['location']['timezone']['offset'],
            'timezone_description': user['location']['timezone']['description'],
            'email': user['email'],
            'uuid': user['login']['uuid'],
            'username': user['login']['username'],
            'password': user['login']['password'],
            'salt': user['login']['salt'],
            'md5': user['login']['md5'],
            'sha1': user['login']['sha1'],
            'sha256': user['login']['sha256'],
            'dob_date': user['dob']['date'],
            'age': user['dob']['age'],
            'registered_date': user['registered']['date'],
            'registered_age': user['registered']['age'],
            'phone': user['phone'],
            'cell': user['cell'],
            'id_name': user['id']['name'],
            'id_value': user['id']['value'],
            'picture_large': user['picture']['large'],
            'picture_medium': user['picture']['medium'],
            'picture_thumbnail': user['picture']['thumbnail'],
            'nationality': user['nat']
        })
    return transformed

def load_data(data, format='csv'):
    """Carga los datos transformados"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'csv':
        filename = f"users_{timestamp}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    else:
        filename = f"users_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    
    print(f"Datos guardados en: {filename}")

def run_etl(num_users=10, output_format='csv'):
    """Ejecuta el proceso ETL completo"""
    print("Iniciando ETL...")
    
    # Extract
    print("Extrayendo datos...")
    raw_data = extract_data(num_users)
    print(f"Datos extraídos: {len(raw_data)} usuarios")
    # print(raw_data[:2])  # Muestra una muestra de los datos extraídos
    
    # Transform
    print("Transformando datos...")
    clean_data = transform_data(raw_data)
    
    # Load
    print("Cargando datos...")
    load_data(clean_data, output_format)
    
    print("ETL completado!")

if __name__ == "__main__":
    num_users = int(input("¿Cuántos usuarios quieres obtener? "))
    run_etl(num_users=num_users, output_format='csv')