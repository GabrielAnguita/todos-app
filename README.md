# 🍌 Bananatasks

Bananatasks es una aplicación para gestionar tareas de forma **colaborativa** y en **tiempo real**.  
Construida con **Django**, utilizando **WebSockets** y **Redis** para la comunicación en vivo, y desplegable fácilmente con **Docker**.

---

## 🚀 Características

- Gestión de tareas: crear, editar, eliminar y marcar como completadas.  
- Colaboración en tiempo real (sin necesidad de refrescar la página).  
- Arquitectura escalable usando **Redis** como channel layer para WebSockets.  
- **Redis** también se utilizó como **cola de tareas** para **Celery**, unificando la infraestructura.  
- Fanout de actualizaciones de tareas en tiempo real gracias a Redis Channels. (No implementé una lógica de reconciliación de versiones)
- Autenticación mediante Google OAuth.

---

## 🛠️ Tecnologías utilizadas

- [Django](https://www.djangoproject.com/) - Backend principal  
- [Django Channels](https://channels.readthedocs.io/) - Comunicación en tiempo real  
- [Redis](https://redis.io/) - Channel layer / Pub-Sub y cola de tareas para Celery  
- [Celery](https://docs.celeryq.dev/) - Ejecución de tareas en segundo plano  
- [Docker](https://www.docker.com/) - Contenerización y despliegue  
- [Alpine.js](https://alpinejs.dev/)
- [TailwindCSS](https://tailwindcss.com/)

---

## 📝 Notas de desarrollo

Este proyecto se desarrolló en aproximadamente **10 horas** con un objetivo claro:  
**probar una idea de experiencia de usuario y una arquitectura backend sólida en poco tiempo.**

- Gran parte del código fue generado con **Claude Code**, lo que permitió acelerar la implementación.

### Backend
- Toda la **arquitectura** fue diseñada por mí.  
- Todas las **decisiones técnicas** fueron tomadas por mí.  
- Usé **Redis** tanto como **cola de tareas para Celery** como **channel layer para WebSockets**, simplificando infraestructura y habilitando el **fanout de actualizaciones en tiempo real**.  
- La arquitectura fue pensada desde el principio para ser escalable: hoy corre en un solo nodo, pero puede distribuirse en múltiples nodos sin cambios de diseño.
- Aunque tiene un diseño robusto, aún está lejos de tener grado productivo, faltan: tests, monitoreo de errores (Sentry?), respaldo de DB, documentación de API, pipeline de CI/CD, y más.

### Frontend
- Permití que Cloud Code explorara libremente la implementación, pinponeando el aspecto del sitio pero con una expectativa clara de su comportamiento.
- El frontend actual es **mínimamente funcional** y sirve solo para ilustrar la experiencia.  
- En un proyecto productivo hubiera optado por **React + TypeScript**, dado que hay bastante lógica en el cliente.  
- La experiencia de usuario sí fue diseñada por mí: cómo debía sentirse y fluir la interacción.
- En resumen el frontend necesitaría una refactorización urgente y dedicarle tiempo real de diseño.

### Tests
⚠️ Este proyecto **no tiene ningún test automatizado**.  
Esto es **inaceptable en un sistema real**, pero fue una decisión consciente:  
para un prototipo rápido de UX/arquitectura no invertí en robustez, sino en mostrar la idea.

### Despliegue
- Decidí desplegar el proyecto en una **máquina virtual con Docker Compose**, manteniendo todas las imágenes dentro de la misma máquina.  
- En un contexto productivo real, cada componente podría desplegarse en **nodos separados**, otorgando mayor **escalabilidad** y resiliencia.  
- Para este despliegue, **Claude Code fue increíblemente útil**: lo usé en conjunto con la **CLI de Google Cloud** y el proceso fue prácticamente automático.  
  - Levantar la máquina virtual,  
  - Obtener un dominio,  
  - Emitir certificados SSL…  
  Todo consistió prácticamente en **apretar ENTER y mirar cómo Claude Code hacía el trabajo**. Fue, honestamente, **muy cómodo**.  

---
