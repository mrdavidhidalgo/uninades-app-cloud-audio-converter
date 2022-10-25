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
curl --location --request POST 'http://localhost:5000/api/auth/signup' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "david",
    "mail": "david@gmail.com",
    "password1": "123456",
    "password2": "123456"
}'
`` 


