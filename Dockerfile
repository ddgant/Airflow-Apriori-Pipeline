# Usamos la imagen oficial de Airflow
FROM apache/airflow:2.9.0

# Copiamos el archivo de requerimientos
COPY requirements.txt .

# Instalamos las dependencias (como pandas)
RUN pip install --no-cache-dir -r requirements.txt