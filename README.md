# Cloud audio converter

## Como correr el proyecto?
El proyecto esta comprendido por 2 servicios el coverter-api encargado de la interacción web del aplicativo y el consumer-api que actua como worker y es el componente que efectivamente realiza la conversión entre los formatos de audio

### Despliegue del converter API
El converter API se desplego usando la plataforma de App Engine.
Antes de correr el comando para desplegar el converter API se debe crear el archivo env_variables.yaml en el directorio converter-api
este archivo contendra las variables y configuraciones de la aplicación, por seguridad no se colocan en el repo publico

#### Estructura del archivo env_variables.yaml
```` 
env_variables:
  POSTGRES_HOST: "{{POSTGRES_HOST}}"
  POSTGRES_PASSWORD: "{{POSTGRES_PASSWORD}}"
  EMAIL_ENABLE: "False"
  DATA_PATH: "/tmp/data"
  BUCKET_NAME: "converter_bucket"
  BUCKET_PATH: "converter_bucket"
  SENDGRID_API_KEY: "{{SENDGRID_API_KEY}}"
  EMAIL_SENDER: "formatconverter15@gmail.com"
  FILE_MANAGER: "GCP_STORAGE"
  GCP_PROJECT_ID: "{{GCP_PROJECT_ID}}"
```` 

una vez creado este archivo, nos ubicamos en el directorio converter-api y se procede a desplegar la aplicación con el siguiente comando:
`` 
gcloud app deploy
`` 


### Despliegue del consumer API
El consumer API se desplego usando la plataforma de Cloud run(Se escogio esta herramienta bajo la autorización del profesor Jesse Padilla).
Antes de correr el comando para desplegar el consumer API se debe crear la imagen de docker y subirla al registro de Container Register.

#### Construcción/publicación de la imagen
Ejecutar los siguentes comandos
````  
cd converter-api
docker build .
docker tag {tag_sha256}  gcr.io/{project-id}/consumer-api:1.0.0
docker push gcr.io/proyecto-desarrollo-nube/consumer-api:1.0.2

````  









Para correr el projecto es necesario tener Docker(docker-client y docker-compose) instalado, se debe ejecutar el siguiente comando:´

#### Terminal Kafka
`` 
 docker compose up kafka
`` 

## ¿Como enviar una petición?

Para enviar una petición, antes se debe agregar el archivo a convertir al directorio ./data del repositorio.
Con lo que el archivo de ejemplo musica.mp3 debe quedar en ./data/musica.mp3

### Pasos
1. Crear el usuario

`` 
curl --location --request POST 'http://localhost:5000/api/auth/signup' 
--header 'Content-Type: application/json' 
--data-raw '{
    "username": "david",
    "mail": "david@gmail.com",
    "password1": "123456",
    "password2": "123456"
}'
`` 

2. Extraer el token de la solicitud anterior 
3. Llamar el servicio tasks 

`` 
curl --location --request POST 'http://localhost:5000/api/tasks' 
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2NjU3MzMwMywianRpIjoiOTRjNWY0MTAtNjYyOC00M2QwLWJlOTgtMTRiY2I0MmE0ZDg0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNjY2NTczMzAzLCJleHAiOjE2NjY1NzQyMDN9.RghW5D1yuj6fHNdO469nnwlqrHkGjXzM48q-WTeyjsE' 
--header 'Content-Type: application/json' 
--data-raw '{
    "fileName": "musica.mp3",
    "newFormat": "WAV"   
}'
``

**Nota:**
Se debe incluir solo el nombre del archivo en la petición, para la petición el archivo estara en ./data/musica.mp3
Luego el servicio retornara un identificador de la tarea creada.

Para mas información sobre los demas recursos rest se incluye un coleccion de postman. [Postman](https://github.com/mrdavidhidalgo/uninades-app-cloud-audio-converter/blob/master/Converter_API.postman_collection.json)
