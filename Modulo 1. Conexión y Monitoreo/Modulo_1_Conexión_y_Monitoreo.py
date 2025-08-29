#!/usr/bin/env python3

import logging
import pandas as pd
import requests
from urllib.parse import quote_plus
import hmac
import hashlib
import base64
from datetime import datetime
import os

# Configurar el logger
logging.basicConfig(filename='whalewisdom_api.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Definir las claves de acceso API
shared_key = 'wY0e3zria06ULMWuSmR2'
secret_key = 'MJ4RWDjzZxtA36KBZh5LMlDKMrw9m0cHpfRzrgH0'

# Archivo para almacenar los quarters previamente procesados
quarters_file = '/Users/sevago/Desktop/Green Gable Advisors LLC/Modulo 1. Conexión y Monitoreo/quarters.csv'

# Función para generar la URL de la API
def generate_api_url(command, shared_key, secret_key, filer_id=None):
    if command == "quarters":
        json_args = f'{{"command":"{command}"}}'
    elif command == "holdings" and filer_id:
        json_args = f'{{"command":"holdings","filer_ids":[{filer_id}],"include_13d":1}}'
    else:
        raise ValueError("Comando o argumentos inválidos para generar la URL.")
    
    formatted_args = quote_plus(json_args)
    timenow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    raw_args = f'{json_args}\n{timenow}'
    hmac_hash = hmac.new(secret_key.encode(), raw_args.encode(), hashlib.sha1).digest()
    sig = base64.b64encode(hmac_hash).decode().rstrip()
    return (f'https://whalewisdom.com/shell/command.json?args={formatted_args}'
            f'&api_shared_key={shared_key}&api_sig={sig}&timestamp={timenow}')

# Función para realizar la solicitud a la API
def fetch_data_from_api(api_url):
    try:
        logging.info(f"Realizando solicitud a la API: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al conectar con la API: {e}")
        return None

# Función para procesar los datos de quarters
def process_quarters(data):
    if not data or 'quarters' not in data:
        logging.warning("No se encontraron datos de quarters en la respuesta.")
        return []
    quarters = data['quarters']
    logging.info(f"Se obtuvieron {len(quarters)} quarters.")
    return quarters

# Función para verificar si hay nuevos quarters
def has_new_quarters(current_quarters):
    if os.path.exists(quarters_file):
        # Leer los quarters previamente almacenados
        try:
            previous_quarters = pd.read_csv(quarters_file)['quarters'].apply(eval).tolist()
        except Exception as e:
            logging.error(f"Error al leer el archivo quarters.csv: {e}")
            return True  # Si no se puede leer el archivo, asumir que hay nuevos quarters

        # Comparar los quarters actuales con los previos
        if set(tuple(sorted(q.items())) for q in current_quarters) == set(tuple(sorted(q.items())) for q in previous_quarters):
            logging.info("No hay nuevos quarters disponibles. Finalizando la ejecución.")
            return False
    return True

# Función para guardar los quarters actuales
def save_quarters(current_quarters):
    try:
        pd.DataFrame({'quarters': [str(q) for q in current_quarters]}).to_csv(quarters_file, index=False)
        logging.info("Quarters actuales guardados en el archivo.")
    except Exception as e:
        logging.error(f"Error al guardar los quarters en el archivo: {e}")

# Función para procesar holdings de un filer_id
def fetch_holdings(filer_id):
    api_url = generate_api_url("holdings", shared_key, secret_key, filer_id=filer_id)
    data = fetch_data_from_api(api_url)
    if not data:
        return []
    
    holdings = []
    results = data.get('results', [])
    for result in results:
        filer_name = result['filer_name']
        for record in result['records']:
            for holding in record['holdings']:
                holding['filer_name'] = filer_name
                holdings.append(holding)
    logging.info(f"Datos obtenidos para filer_id: {filer_id}")
    return holdings

# Medir el tiempo de extracción
start_time = datetime.now()

# Obtener y procesar los datos de quarters
quarters_api_url = generate_api_url("quarters", shared_key, secret_key)
data = fetch_data_from_api(quarters_api_url)
quarter_list = process_quarters(data)

# Verificar si hay nuevos quarters
if not quarter_list or not has_new_quarters(quarter_list):
    print("No hay nueva información de quarters. Finalizando la ejecución.")
else:
    # Guardar los quarters actuales
    save_quarters(quarter_list)

    # Leer el DataFrame de filer_ids desde un archivo CSV
    filers = pd.read_csv('filers.csv')

    filers = filers.rename(columns={'id': 'filer_id'})

    # Lista para almacenar los holdings
    holdings_list = []

    # Iterar sobre todos los registros en filers
    for index, row in filers.iterrows():
        filer_id = row['filer_id']
        holdings = fetch_holdings(filer_id)
        holdings_list.extend(holdings)

    # Almacenar la información en un DataFrame
    holdings_df = pd.DataFrame(holdings_list)
    logging.info("Datos almacenados en el DataFrame")
    print(holdings_df)

# Calcular el tiempo de extracción
end_time = datetime.now()
extraction_time = (end_time - start_time).total_seconds()
logging.info(f"Tiempo total de extracción: {extraction_time} segundos")