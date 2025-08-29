Document Setup

Create crm/README.md:
# CRM Celery Setup

## Prerequisites
- Redis installed and running on `localhost:6379`
- Python dependencies installed:
  ```bash
  pip install -r requirements.txt

Setup Steps
python manage.py migrate


Start Redis (if not already running): redis-server

Start Celery worker: celery -A crm worker -l info

Start Celery Beat scheduler: celery -A crm beat -l info

Verify logs: cat /tmp/crm_report_log.txt
