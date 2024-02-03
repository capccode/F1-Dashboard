### To prepare for AWS:

# aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 573116658321.dkr.ecr.us-east-1.amazonaws.com

# Docker Build
docker build --file Dockerfile  --tag "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app:test" .

# Docker Tag
docker tag "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app:test" "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app:latest"

# Docker run locally
# docker run --name colton-dash-app -p 8050:8050 --hostname=0.0.0.0 --publish-all=true --privileged=true -t -i -d -e "APP_PORT=8050" -e "APP_HOME=/usr/src/app/" -e "FLASK_APP=app" -e "FLASK_ENV=dev" "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app"


# Docker push
docker push "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app:latest"


### For local:


# # Docker Build
# docker build --file Dockerfile  --tag "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app:local" .

# # Docker Tag
# docker tag "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app:local" "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app:local"

# # Docker run locally
# # docker run --name my-container --hostname=0.0.0.0 --publish-all=true --privileged=true -t -i -d -e "APP_PORT=5000" -e "APP_HOME=/usr/src/app/" -e "APP_SECRET_KEY=nC5CfQ@d2jNvqrba" -e "FLASK_APP=app" -e "FLASK_ENV=dev" -e "POSTGRES_DATABASE=postgresdb" -e "POSTGRES_ENDPOINT=xxxx:5432" -e "POSTGRES_PASSWORD=xxx" -e "POSTGRES_USER=postgres" "****/terraform-flask-postgres-docker-example:latest"
# docker run --name colton-dash-app -p 8050:8050 --hostname=0.0.0.0 --publish-all=true --privileged=true -t -i -d -e "APP_PORT=8050" -e "APP_HOME=/usr/src/app/" -e "FLASK_APP=app" -e "FLASK_ENV=dev" "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app:local"

# # Docker push
# # docker push "573116658321.dkr.ecr.us-east-1.amazonaws.com/colton-dash-app:latest"


