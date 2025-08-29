# CRM Celery + Celery Beat Setup

## Requirements
- Redis
- Celery
- django-celery-beat

## Setup Steps

1. Install Redis and start it:
   ```bash
   sudo apt install redis-server
   redis-server


# CRM Application

This is the **CRM (Customer Relationship Management)** application built with **Django**, **GraphQL**, and **Celery**.  
It allows you to manage products, handle low-stock alerts, run scheduled reports, and interact with the system via a GraphQL API.

---

## Features

- Django-based backend with ORM models (e.g., Product).
- GraphQL API (`graphene-django`) for queries and mutations.
- Celery workers for background tasks (e.g., generating CRM reports).
- Scheduled tasks using Celery Beat or cron jobs.
- Logging of reports to `/tmp/crmreportlog.txt`.
- Extensible structure for additional features.

---

## Prerequisites

Make sure you have the following installed:

- Python 3.10+
- pip (latest)
- Virtualenv
- Redis (for Celery broker)
- Docker (optional, for containerized setup)

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <your-repo-name>
