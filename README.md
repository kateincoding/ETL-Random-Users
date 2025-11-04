# ETL-Random-Users

ETL básico en Python que extrae datos de la API Random User, los transforma y los guarda en archivos CSV/JSON.

## Requisitos
- Python 3.x
- requests

## Instalación
```bash
pip install -r requirements.txt
```
```bash
./installVM.sh
```

## Base de datos
```bash
sudo -i -u postgres
psql
\i ./database/create-tables.sql

## ETL
```bash
python ETL-script.py
```

El script te pedirá la cantidad de usuarios que quieres obtener y generará:
- `raw_data_YYYYMMDD_HHMMSS.json` - Datos originales de la API en el proceso de Extract
- `users_YYYYMMDD_HHMMSS.csv` - Datos transformados y cargados en un csv