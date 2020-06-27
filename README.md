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
