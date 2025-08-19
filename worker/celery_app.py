import os
from celery import Celery
from kombu import Queue


def create_celery_app() -> Celery:
	broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
	backend_url = os.getenv("CELERY_RESULT_BACKEND", "rpc://")
	app = Celery("oms", broker=broker_url, backend=backend_url, include=["worker.tasks"])  # ensure tasks loaded
	# Single durable queue named 'oms'
	app.conf.task_default_queue = "oms"
	app.conf.task_queues = [Queue("oms", durable=True)]
	app.conf.update(
		task_track_started=True,
		task_acks_late=True,
		task_time_limit=300,
		task_soft_time_limit=240,
		enable_utc=False,
		timezone=os.getenv("TIMEZONE", "Asia/Kolkata"),
	)
	return app


celery_app = create_celery_app()

# Fallback explicit import to register tasks when running in some environments
try:
	import worker.tasks  # noqa: F401
except Exception:
	pass
