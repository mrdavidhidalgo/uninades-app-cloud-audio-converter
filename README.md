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

```` 
gcloud app deploy
```` 

luego de esto se debe ingresar el siguiente código para buscar la url del servicio desplegado

```` 
gcloud app browse
```` 

### Despliegue del consumer API
El consumer API se desplego usando la plataforma de Cloud run(Se escogio esta herramienta bajo la autorización del profesor Jesse Padilla).
Antes de correr el comando para desplegar el consumer API se debe crear la imagen de docker y subirla al registro de Container Register.

#### Habilitar la API de Google container register
https://console.cloud.google.com/gcr/images

#### Construcción/publicación de la imagen
Ejecutar los siguentes comandos

````  
cd converter-api
docker build .
docker tag {tag_sha256}  gcr.io/{project-id}/consumer-api:1.0.0
docker push gcr.io/{project-id}/consumer-api:1.0.0

````  

#### Desplegar en Cloud run
Ir al servicio de Cloud run de GCP en https://console.cloud.google.com/run?project={project-id}
y proceder a crear el servicio por la consola web. (Clic en Crear Servicio) 

![image](https://user-images.githubusercontent.com/3289138/205830226-69e37924-f093-43d1-bf7b-ab35fa6d1d42.png)

Luego de esto se debe selecionar la imagen de docker subida al repositorio en el paso anterior 

![image](https://user-images.githubusercontent.com/3289138/205831760-322fa554-440b-4f2c-a223-22c8574b9554.png)

Y configurar las variables de entorno necesarias del proyecto que se listan(algunas datos se ofuscan por seguridad) a continuación:

![image](https://user-images.githubusercontent.com/3289138/205832421-aa17e593-9d73-47f7-8b57-2a6c47549bcf.png)



## ¿Como enviar una petición?

### Pasos
1. Crear el usuario

```` 
curl --location --request POST '{url-app-engine}/api/auth/signup' 
--header 'Content-Type: application/json' 
--data-raw '{
    "username": "david",
    "mail": "david@gmail.com",
    "password1": "123456",
    "password2": "123456"
}'
```` 

Para mas información sobre los demas recursos rest se incluye un coleccion de postman. [Postman](https://github.com/mrdavidhidalgo/uninades-app-cloud-audio-converter/blob/master/Converter_API.postman_collection.json)
