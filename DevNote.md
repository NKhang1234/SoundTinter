# Development Dashboard Access

This document lists the URLs to access the dashboards of all internal services in the development environment.  
All dashboards are routed through Traefik using the `dev.localhost` domain.

---

## 1. MinIO Console
- **URL:** [http://minioConsole.dev.localhost](http://minioConsole.dev.localhost)  
- **Purpose:** Access MinIO web console for managing S3 buckets.  
- **Notes:** Only exposed in development. Do not expose in production.

---

## 2. DynamoDB Admin
- **URL:** [http://dynamodbAdmin.dev.localhost](http://dynamodbAdmin.dev.localhost)  
- **Purpose:** GUI for managing local DynamoDB tables.  
- **Notes:** Connects internally to DynamoDB Local container.

---

## 3. RabbitMQ Management UI
- **URL:** [http://rabbitmqUI.dev.localhost](http://rabbitmqUI.dev.localhost)  
- **Purpose:** Monitor queues, exchanges, and messages in RabbitMQ.  
- **Notes:** Exposed via Traefik in development only.

---

## 4. Traefik Dashboard
- **URL:** [http://traefikDashboard.dev.localhost](http://traefikDashboard.dev.localhost)  
- **Purpose:** Monitor Traefik routers, services, and entrypoints.  
- **Authentication:** Basic Auth enabled for development.

---

## 5. Analyst Service API
- **URL:** [http://analyst.dev.localhost/docs](http://analyst.dev.localhost/docs)  
- **Purpose:** Access Analyst Service APIs for debugging.  
- **Notes:** Only exposed in development. Do not expose in production.

---

## 6. Mapping Service API
- **URL:** [http://mapping.dev.localhost/docs](http://mapping.dev.localhost/docs)  
- **Purpose:** Access Mapping Service APIs for debugging.  
- **Notes:** Only exposed in development. Do not expose in production.


## ⚠️ Notes
- All services are routed through Traefik and accessible under the `dev.localhost` domain.  
- Ports are **internal to Docker**, except for Traefik’s HTTP entrypoint.  
- This setup is **dev-only**. In production, dashboards should be secured and not publicly accessible.