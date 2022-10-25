# Cloud audio converter

## Como correr el proyecto?
Para correr el projecto es necesario tener Docker(docker-client y docker-compose) instalado, se debe ejecutar el siguiente comando:´

### Forma 1 (Recomendado)
Se deben abrir 3 terminales y correr los siguientes comandos

#### Terminal Kafka
`` 
 docker compose up kafka
`` 
 
 Luego esperar a que suba el servidor correctamente
 
 #### Terminal Consumer-api
 `` 
 docker compose up consumer-api
 `` 
 
 Luego esperar a que el consumidor suba
 
 #### Terminal Converter-api
 `` 
 docker compose up converter-api
 `` 
 
 Luego esperar a que suba el API, se puede verificar si esta arriba el servicio con el siguiente comando
 
 `` 
 WGET localhost:5000/health
 `` 
 
 
### Forma 2 (No se recomienda)

 `` 
 docker compose up -d
 `` 
 
 Para verificar si los servicios subieron se puede utilizar el siguiente comando:
  
 `` 
 docker ps
 `` 
 
 Se deberan observar 2 microservicios desplegados y 3 servicios
 1. Kafka
 2. Zookeper
 3. Postgres
 4. Converter-api
 5. Consumer-api
 
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

Para mas información sobre los demas recursos rest se incluye un coleccion de postman. 
