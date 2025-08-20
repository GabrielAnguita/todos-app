# 🍌 Bananatasks

Bananatasks es una aplicación para gestionar tareas de forma **colaborativa** y en **tiempo real**.  
Construida con **Django**, utilizando **WebSockets** y **Redis** para la comunicación en vivo, y desplegable fácilmente con **Docker**.

---

## 🚀 Características

- Gestión de tareas: crear, editar, eliminar y marcar como completadas.  
- Colaboración en tiempo real (sin necesidad de refrescar la página).  
- Arquitectura escalable usando **Redis** como channel layer para WebSockets.  
- **Redis** también se utilizó como **cola de tareas** para **Celery**, unificando la infraestructura.  
- Fanout de actualizaciones de tareas en tiempo real gracias a Redis Channels.
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

- Tiempo de desarrollo: aproximadamente **10 horas**.  
- Gran parte del código fue generado con ayuda de **Claude Code**. (Iniciado con el archivo prompt.txt)

### Backend
- Toda la **arquitectura** fue diseñada por mí.  
- Todas las **decisiones técnicas** fueron tomadas por mí.  
- Decidí usar **Redis** como **cola de tareas para Celery** y también como **channel layer para WebSockets**, lo que permitió simplificar la infraestructura y habilitar el **fanout de actualizaciones de tareas en tiempo real**.
- Cada línea fue leída por mi, teniendo que instruir varias veces a Claude para que cambiara de enfoque, o a veces simplemente tomé yo el mando para mostrarle el camino.

### Frontend y Experiencia de Usuario
- Definí la forma en que las interacciones debían sentirse y fluir.  
- Permití que Claude Code explorara libremente la implementación, dados mis requerimientos.
- La implementación actual es **mínimamente funcional**: cumple para mostrar la experiencia, pero es **un caos técnico**.  
- De haber sido un proyecto con un fin productivo y más tiempo de desarrollo, hubiera optado por:  
  - **React** para estructurar mejor la interfaz,  
  - **TypeScript** para manejar de forma sólida la lógica del frontend, ya que este proyecto tiene **mucha lógica del lado del cliente**.  
- En este estado, el frontend simplemente muestra el **punto de la experiencia de usuario** que quería ilustrar.
- No leí el código, me preocupé de que funcionara.

### Tests
- Este proyecto **no tiene ningún test automatizado**.  
- Para mí, esto hace que el código sea **inaceptable** en un contexto serio o productivo.  
- Sin embargo, el objetivo de este trabajo no fue producir un sistema robusto, sino **demostrar una idea de experiencia de usuario**.  

### Despliegue
- Decidí desplegar el proyecto en una **máquina virtual con Docker Compose**, manteniendo todas las imágenes dentro de la misma máquina.  
- En un contexto productivo real, cada componente podría desplegarse en **nodos separados**, otorgando mayor **escalabilidad** y resiliencia.  
- Para este despliegue, **Claude Code fue increíblemente útil**: lo usé en conjunto con la **CLI de Google Cloud** y el proceso fue prácticamente automático.  
  - Levantar la máquina virtual,  
  - Obtener un dominio,  
  - Emitir certificados SSL…  
  Todo consistió prácticamente en **apretar ENTER y mirar cómo Claude Code hacía el trabajo**. Fue, honestamente, **muy cómodo**.  

---
