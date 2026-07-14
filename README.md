```markdown
# 🚀 Proyecto Final: Despliegue Automatizado de Aplicación en VPS con Docker Swarm y Traefik

## 👥 Integrantes del Grupo

* **Francisco Ramírez**
* **Domenica Espinosa**

---

# 📖 Descripción del Proyecto

Este proyecto consiste en el despliegue automatizado de una aplicación web basada en microservicios sobre un VPS de Contabo utilizando:

* Docker Engine
* Docker Swarm
* Traefik v2 como proxy inverso
* PostgreSQL
* Adminer
* Portainer CE
* GitHub Actions para CI/CD
* GitHub Container Registry (GHCR)

La infraestructura permite la publicación segura de servicios mediante HTTPS automático con Let's Encrypt, administración centralizada de contenedores y despliegues continuos desde GitHub.

---

# 🗺️ Arquitectura de la Solución

```text
[ Cliente Web / Navegador ]
        │
        ▼
(Subdominios byronrm.com vía HTTP/HTTPS)
        │
        ▼
┌──────────────────────────────────────────────┐
│         VPS Contabo (Debian 12)              │
│         IP: 161.97.139.120                   │
│                                              │
│   Red Overlay: traefik-public                │
│                                              │
│  ┌──────────────────────────┐                │
│  │       Traefik v2.11      │                │
│  │      Reverse Proxy       │                │
│  └────────────┬─────────────┘                │
│               │                              │
│   ┌───────────┼───────────────┐              │
│   ▼           ▼               ▼              │
│ Flask App   Adminer      Portainer CE        │
│               │                              │
│               ▼                              │
│          PostgreSQL                          │
│       Volumen: pgdata                        │
└──────────────────────────────────────────────┘
```

---

# 🏗️ Componentes de la Infraestructura

| Servicio       | Función                                     |
| -------------- | ------------------------------------------- |
| Traefik v2.11  | Proxy inverso dinámico y administración SSL |
| Flask App      | Aplicación web principal                    |
| PostgreSQL     | Base de datos relacional                    |
| Adminer        | Administración gráfica de PostgreSQL        |
| Portainer CE   | Gestión visual de Docker Swarm              |
| GitHub Actions | Automatización CI/CD                        |

---

# 🔹 Fase 1: Desarrollo de la Aplicación

## Creación de la Aplicación

Se desarrolló una aplicación web utilizando Flask y Python con conexión a una base de datos PostgreSQL.

## Estructura del Proyecto

```text
.
├── app.py
├── requirements.txt
├── Dockerfile
├── templates/
├── static/
├── stack.yml
└── .github/workflows/
```

## Variables de Entorno

La conexión a la base de datos se realiza mediante variables de entorno para evitar exponer credenciales dentro del código fuente.

---

# 🔹 Fase 2: Dockerización

## Dockerfile

Se construyó una imagen Docker optimizada basada en Python para contenerizar la aplicación Flask.

### Proceso

1. Selección de imagen base ligera.
2. Definición del directorio de trabajo.
3. Instalación de dependencias.
4. Copia del código fuente.
5. Exposición del puerto de servicio.
6. Ejecución automática de la aplicación.

## Validación Local

Antes del despliegue, se realizaron pruebas locales para verificar el correcto funcionamiento de la imagen Docker.

---

# 🔹 Fase 3: Configuración del VPS

## Servidor Utilizado

* Proveedor: Contabo
* Sistema Operativo: Debian 12

## Instalación de Docker

Se instaló Docker Engine utilizando los repositorios oficiales.

## Inicialización de Docker Swarm

```bash
docker swarm init
```

## Creación de Red Overlay

```bash
docker network create \
  --driver=overlay \
  traefik-public
```

## Permisos del Socket Docker

```bash
sudo chmod 666 /var/run/docker.sock
```

---

# 🔹 Fase 4: Orquestación con Docker Swarm

Toda la infraestructura fue definida mediante un archivo `stack.yml`.

## Servicios Desplegados

### Traefik

* Proxy inverso
* Certificados SSL automáticos
* Balanceo de carga
* Descubrimiento dinámico de servicios

### Flask App

* Aplicación principal
* Imagen almacenada en GHCR

### PostgreSQL

* Motor de base de datos
* Persistencia mediante volumen Docker

### Adminer

* Interfaz web para administración de PostgreSQL

### Portainer CE

* Administración visual de Docker Swarm

## Volúmenes Persistentes

```yaml
volumes:
  pgdata:
```

## Red Compartida

```yaml
networks:
  traefik-public:
    external: true
```

---

# 🔹 Fase 5: Pipeline CI/CD con GitHub Actions

## Secretos Configurados

| Variable        | Descripción                        |
| --------------- | ---------------------------------- |
| VPS_IP          | Dirección IP del VPS               |
| SSH_PRIVATE_KEY | Llave privada para despliegue      |
| DB_PASSWORD     | Contraseña PostgreSQL              |
| CR_PAT          | Token de GitHub Container Registry |

## Flujo Automatizado

Cada vez que se realiza un:

```bash
git push origin main
```

GitHub Actions ejecuta automáticamente:

### 1. Validación

* Verificación del código
* Instalación de dependencias

### 2. Build

* Construcción de imagen Docker

### 3. Push

* Publicación en GitHub Container Registry

```text
ghcr.io/19ramirez/
```

### 4. Deploy

* Conexión SSH al VPS
* Actualización del repositorio
* Actualización de variables de entorno
* Ejecución automática de:

```bash
docker stack deploy \
  -c stack.yml \
  taller
```

---

# 🔹 Fase 6: Validaciones en Producción

## Certificados SSL

Se verificó la emisión automática de certificados HTTPS mediante Let's Encrypt para todos los servicios publicados.

## Pruebas de Persistencia

Detener el servicio:

```bash
docker service scale taller_db=0
```

Levantar nuevamente:

```bash
docker service scale taller_db=1
```

Resultado:

* Los datos permanecen almacenados.
* El volumen `pgdata` conserva la información.

---

# 🌐 Servicios Publicados

| Servicio            | URL                             |
| ------------------- | ------------------------------- |
| 🚀 Aplicación Flask | https://fd.byronrm.com          |
| 🗄️ Adminer         | https://pgfd.byronrm.com        |
| 🐳 Portainer        | https://portainerfd.byronrm.com |

---

# 📋 Requisitos Previos para un Nuevo VPS

Ejecutar los siguientes comandos antes del despliegue:

```bash
# Inicializar Docker Swarm
docker swarm init

# Crear red overlay para Traefik
docker network create \
  --driver=overlay \
  traefik-public

# Ajustar permisos del socket Docker
sudo chmod 666 /var/run/docker.sock
```

---

# 🚀 Flujo de Despliegue

## Desarrollo

```bash
git add .
git commit -m "Actualización"
git push origin main
```

## CI/CD

GitHub Actions:

1. Compila la aplicación.
2. Genera la imagen Docker.
3. Publica la imagen en GHCR.
4. Se conecta al VPS.
5. Actualiza los servicios de Docker Swarm.

## Producción

Los servicios quedan disponibles automáticamente mediante HTTPS con certificados SSL válidos.

---

# ✅ Tecnologías Utilizadas

* Python
* Flask
* PostgreSQL
* Docker
* Docker Swarm
* Traefik v2.11
* Adminer
* Portainer CE
* GitHub Actions
* GitHub Container Registry (GHCR)
* Debian 12
* Contabo VPS
* Let's Encrypt

---

# 📌 Resultado Final

Se implementó una plataforma completamente automatizada para despliegue continuo de aplicaciones en producción, utilizando Docker Swarm como orquestador, Traefik como proxy inverso con certificados SSL automáticos y GitHub Actions para CI/CD, garantizando escalabilidad, seguridad y persistencia de datos.
```
