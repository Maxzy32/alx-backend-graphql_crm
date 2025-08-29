INSTALLED_APPS = [
    # other apps...
    "django_crontab",
    # other apps...
    "django_celery_beat",
]



CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
      ('0 */12 * * *', 'crm.cron.update_low_stock'),  # new
]
