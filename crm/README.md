# CRM Celery/Beat Setup

## Install Redis and dependencies

- Install Redis:
  ```bash
  sudo apt install redis-server
  sudo systemctl start redis-server
  sudo systemctl enable redis-server
  ```
- Install Python dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Run migrations

```
python manage.py migrate
```

## Start Celery worker

```
celery -A crm worker -l info
```

## Start Celery Beat

```
celery -A crm beat -l info
```

## Verify logs

Check `/tmp/crm_report_log.txt` for weekly CRM report logs.
