#Como Hay

## Development deployment

    docker-compose up  --build

## Production Deployment

For production deployment a new file named `.env.prod` 
should be created containing the production environment 
variables like:

```shell script
DEBUG=0
SECRET_KEY='very_secret_unique_key'
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

DATABASE=postgres
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=comohay_prod
SQL_USER=comohay
SQL_PASSWORD=comohay
SQL_HOST=db
SQL_PORT=5432

POSTGRES_USER=comohay
POSTGRES_PASSWORD=comohay
POSTGRES_DB=comohay_prod
```

Once the production environment variables are defined, 
the application can be started using:

    docker-compose -f docker-compose.prod.yml up --build
    
## Preparing Solr

Building the configuration schema and reloading the precreated core in docker-compose
    
    docker-compose exec web python manage.py build_solr_schema --configure-directory=solr_data/ads/conf --reload-core ads
    
Building Solr index. This may take a while depending on the amount of data

    docker-compose exec web python manage.py rebuild_index
    
If, for some reason, you need to recreate the index from scratch, it is necessary to clean the docker named volumes

     docker-compose down -v
     
Re-init redis cache at pos 0 and 1

     docker-compose -f docker-compose.prod.yml exec redis redis-cli -n 0 flushdb; docker-compose -f docker-compose.prod.yml exec redis redis-cli -n 1 flushdb

## Development

for development proposes is convenient to create a new 
`comohay/settings_local.py` file. In this file you can override default settings or define new ones. 

### Scheduled tasks

By default, ComoHay defines scheduled tasks for crawling and indexing. In the development environment
you may want to avoid the tasks execution. For this you can override the 
`CELERY_BEAT_SCHEDULE` variable including it in `comohay/settings_local.py`:

      CELERY_BEAT_SCHEDULE = {}

### Caching

ComoHay uses caching by default. For development proposes you may want to disable the caching using the
Django `DummyCache`. For this, you can override the `CACHES` setting in `comohay/settings_local.py`:

    CACHES = {
        "default": {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
        "search": {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

### Api credentials for the telegram bot
- https://github.com/telegramdesktop/tdesktop/blob/dev/docs/api_credentials.md