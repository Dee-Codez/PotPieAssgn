from celery import Celery
from app.utility.locale import Config

redis_url = f'redis://{Config.REDIS_USERNAME}:{Config.REDIS_PASSWORD}@{Config.REDIS_HOST}:{Config.REDIS_PORT}/0'

celery_app = Celery(
    'tasks',
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    result_expires=3600,
)

import app.utility.analysis