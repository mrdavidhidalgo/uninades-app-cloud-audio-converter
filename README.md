# Cloud audio converter

## Como correr el proyecto?
Para correr el projecto es necesario tener Docker(docker-client y docker-compose) instalado, se debe ejecutar el siguiente comando:´

### Forma 1 (Recomendado)
Se deben abrir 3 terminales y correr los siguientes comandos

#### Terminal Kafka
 `` 
 docker compose up kafka
 `` 
 luego esperar a que suba el servidor correctamente
 
 #### Terminal Consumer-api
 `` 
 docker compose up consumer-api
 `` 
 luego esperar a que el consumidor suba
 
 #### Terminal Converter-api
 `` 
 docker compose up converter-api
 `` 
 luego esperar a que suba el API
 
 
 
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
 
## Como enviar una petición?
 
