import requests
import json
import csv
from datetime import datetime

def extract_data(num_users=10):
    """Extrae datos de la API Random User"""
    url = f"https://randomuser.me/api/"
    if num_users < 5000:
        response = requests.get(url,  params={'results' : num_users})
    else:
        batches = num_users // 5000
        remainder = num_users % 5000
        all_results = []
        for _ in range(batches):
            response = requests.get(url, params={'results': 5000})
            all_results.extend(response.json()['results'])
        if remainder > 0:
            response = requests.get(url, params={'results': remainder})
            all_results.extend(response.json()['results'])
        return all_results
    return response.json()['results']

def transform_data(raw_data):
    """Transforma los datos extraídos"""
    transformed = []
    for user in raw_data:
        transformed.append({
            'full_name': f"{user['name']['first']} {user['name']['last']}",
            'email': user['email'],
            'gender': user['gender'],
            'country': user['location']['country'],
            'age': user['dob']['age'],
            'phone': user['phone']
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