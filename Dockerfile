# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /code

# Copia el archivo de dependencias
COPY ./requirements.txt /code/requirements.txt

# Instala las dependencias
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copia el código de la aplicación
COPY ./app /code/app

# Expone el puerto en el que correrá la app
EXPOSE 8000

# Comando para correr la aplicación usando uvicorn
# --host 0.0.0.0 es crucial para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]