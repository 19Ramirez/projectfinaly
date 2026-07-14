cat << 'EOF' > /home/1750002782/landinga/README.md
# 🚀 Proyecto Final: Despliegue Automatizado de Aplicación en VPS con Docker Swarm & Traefik

Este proyecto comprende el despliegue automatizado en producción de una aplicación web de microservicios sobre un Servidor VPS de Contabo, utilizando **Docker Swarm** para la orquestación, **Traefik v2** como proxy inverso dinámico con resolución automática de certificados SSL (HTTPS), y un pipeline de **CI/CD con GitHub Actions**.

---

## 👥 Integrantes del Grupo
* **Integrante 1:** Francisco Ramírez
* **Integrante 2:** Domenica Espinosa

---

## 🗺️ Diagrama de Arquitectura de la Solución

El flujo de tráfico e interacción entre componentes sigue el siguiente esquema:

```text
[ Cliente Web / Navegador ] 
        │
        ▼ (Subdominios Públicos de byronrm.com vía Puerto 80 / 443)
┌────────────────────────────────────────────────────────────────────────┐
│ Servidor VPS Contabo (IP: 161.97.139.120 | OS: Debian 12)              │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ Red Overlay Virtual: traefik-public                            │   │
│   │                                                                │   │
│   │  ┌─────────────────┐       HTTPS       ┌────────────────────┐  │   │
│   │  │   TRAEFIK v2.11  │──────────────────►│    PORTAINER CE    │  │   │
│   │  │ (Proxy Inverso) │                   │ (portainerfd.***)  │  │   │
│   │  └────────┬────────┘                   └────────────────────┘  │   │
│   │           │                                                    │   │
│   │           ├────────────────────────────┐                       │   │
│   │           ▼ HTTPS                      ▼ HTTPS                 │   │
│   │  ┌──────────────────┐         ┌────────────────────┐           │   │
│   │  │   FLASK APP      │         │     ADMINER        │           │   │
│   │  │ (fd.byronrm.com) │         │ (pgfd.byronrm.com) │           │   │
│   │  └────────┬─────────┘         └─────────┬──────────┘           │   │
│   │           │                             │                      │   │
│   │           │ Conexión Interna DNS        │ Gestión Gráfica      │   │
│   │           ▼                             ▼                      │   │
│   │  ┌─────────────────────────────────────────────────┐           │   │
│   │  │       BASE DE DATOS POSTGRESQL (Servicio: db)   │           │   │
│   │  │       • Volumen persistente: pgdata             │           │   │
│   │  └─────────────────────────────────────────────────┘           │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘

---

## 🔗 Enlaces de Acceso

| Servicio | URL de Acceso | Descripción |
| :--- | :--- | :--- |
| **🚀 Aplicación Web** | [https://fd.byronrm.com](https://fd.byronrm.com) | Entorno principal de la aplicación Flask / Python. |
| **🗄️ Base de Datos (Adminer)** | [https://pgfd.byronrm.com](https://pgfd.byronrm.com) | Gestor web para administrar la base de datos PostgreSQL. |
| **🐳 Portainer** | [https://portainerfd.byronrm.com](https://portainerfd.byronrm.com) | Panel de administración visual de Docker Swarm. |

---
