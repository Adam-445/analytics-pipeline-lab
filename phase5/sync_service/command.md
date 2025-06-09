docker-compose exec -e PGPASSWORD=${POSTGRES_PASSWORD} -it postgres psql -U admin -d analytics
