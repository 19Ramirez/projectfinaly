# 🚀 Taller Stack — Sistema de Despliegue Continuo (Docker Swarm + Traefik)

Este repositorio contiene la configuración del stack de producción para el proyecto de taller. Utiliza **Docker Swarm** para la orquestación de contenedores y **Traefik v2.11** como Proxy Inverso para manejar de forma automática los certificados SSL con Let's Encrypt.

---

## 🔗 Enlaces de Acceso

| Servicio | URL de Acceso | Descripción |
| :--- | :--- | :--- |
| **🚀 Aplicación Web** | [https://fd.byronrm.com](https://fd.byronrm.com) | Entorno principal de la aplicación Flask / Python. |
| **🗄️ Base de Datos (Adminer)** | [https://pgfd.byronrm.com](https://pgfd.byronrm.com) | Gestor web para administrar la base de datos PostgreSQL. |
| **🐳 Portainer** | [https://portainerfd.byronrm.com](https://portainerfd.byronrm.com) | Panel de administración visual de Docker Swarm. |

---

## 🏗️ Requisitos Previos en el Servidor (VPS)

Antes de realizar el despliegue en un VPS nuevo (como Contabo), asegúrate de inicializar el Swarm y crear la red pública que utiliza Traefik:

```bash
# 1. Iniciar Docker Swarm (si no está activo)
docker swarm init

# 2. Crear la red overlay externa para Traefik
docker network create --driver=overlay traefik-public

# 3. Dar permisos correctos al socket de Docker (Evita errores de permisos)
sudo chmod 666 /var/run/docker.sock
