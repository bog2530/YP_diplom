from celery import Celery
from configs.celery import CELERY
from configs.redis import REDIS

from tasks import update_genres_index, update_movies_index, update_persons_index

app = Celery(
    broker=REDIS.URI,
    backend=REDIS.URI,
)

app.config_from_object(CELERY.model_dump())
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        15.0,
        update_movies_index.s(),
        name="Check for updates in movies index.",
    )
    sender.add_periodic_task(
        15.0,
        update_genres_index.s(),
        name="Check for updates in genres index.",
    )
    sender.add_periodic_task(
        15.0,
        update_persons_index.s(),
        name="Check for updates in persons index.",
    )
