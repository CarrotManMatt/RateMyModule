# Deployment Guide Using Docker

## Quick Links

- [Containerization and Background](#containerization-and-background)
- [Setting Up Docker for Our Application](#setting-up-docker-for-our-application)
- [Integrating Docker into the GitLab Development Pipeline](#integrating-docker-into-the-gitlab-development-pipeline)
- [Versioning and Scalability](#versioning-and-scalability)
- [More Resources](#more-resources)

## Containerization and Background

Docker uses containers, which are bundles of software that package code and its
dependencies together. These containers mean that application code can be run
consistently across different development environments, avoiding discrepancies
throughout our development process and eventually in deployment.

Using Docker in our application means that we can create a Docker container
image from our application code, this can then be deployed on any system using
Docker Engine where it becomes a live container. Having our application
packaged in this compact and portable way, not only reduces setup and
configuration times for ourselves, but isolates the application which enhances
security and aids in version control.

Containers work by virtualizing the operating system layer, where multiple
containers share the OS kernel but operate in isolation. When a container is
launched from a container image, the container runtime (i.e. Docker Engine) on
the host system sets up this isolated environment which includes resources the
application needs to run. The container runtime is also responsible for the
lifecycle of the container, including container creation, execution,
termination, and deletion.

## Setting Up Docker for Our Application

To set up Docker for our application, we have created a `Dockerfile` in the
root of our project. This file outlines the environment and dependencies
required to run our application within a Docker container.

Below we will explain the contents of our `Dockerfile` and what each line does:

```Dockerfile
FROM python:3.12 as builder
```

This line specifies the base image for our container. In this case, we are
using `python:3.12` as our base image. The `as builder` tag is used to create a
temporary container for building the application.

```Dockerfile
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_HOME=/opt/poetry
```

This line sets environment variables for the container. These variables are
used to configure the Python and Poetry environments.

```Dockerfile
RUN apt-get update && apt-get install --no-install-recommends -y curl build-essential
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==1.8.1
```

This section installs the required system dependencies for the container,
including `curl` and `build-essential`. They also install `poetry` and create a
virtual environment for the application.

```Dockerfile
WORKDIR /app

COPY poetry.lock pyproject.toml README.md ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    $POETRY_HOME/bin/poetry install --without dev \
    --no-root --no-interaction --with deploy
```

This section sets the working directory for the container to `/app` and copies
the `poetry.lock`, `pyproject.toml`, and `README.md` files into the container.
It then installs the application dependencies using `poetry`. The `--mount`
flag is used to cache the `poetry` dependencies to improve build times, meaning
that the dependencies are only reinstalled if the `poetry.lock` file changes.

```Dockerfile
FROM python:3.12-slim as runtime

ENV LANG=C.UTF-8 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
```

This section specifies the base image for the **runtime container**
using `python:3.12-slim` which is a stripped down version of the one used to
build. It also sets the runtime environment variables for the container, such
as specifying the virtual environment path as `/app/.venv`.

```Dockerfile
WORKDIR /app
RUN printf '#!/bin/sh\n\n'\
'./manage.py migrate --no-input\n'\
'./manage.py collectstatic --no-input\n'\
'gunicorn core.wsgi:APPLICATION --bind=0.0.0.0:8000\n' > /app/entrypoint.sh
WORKDIR /
```

This section sets the working directory for the container to `/app` again and
creates a new shell script named `entrypoint.sh`. The script does the
following:

- `./manage.py migrate --no-input` - this runs Django's `manage.py migrate`
  command which carries out database migrations (the `--no-input` flag is used
  to avoid prompting the user for input).
- `./manage.py collectstatic --no-input` - this runs
  Django's `manage.py collectstatic` command which collects static files from
  the application (CSS, JavaScript, images, etc.) into a single directory for
  deployment.
- `gunicorn core.wsgi:APPLICATION --bind=0.0.0.0:8000` - this runs the Gunicorn
  web server with `core.wsgi:APPLICATION` as the application entry point (this
  is defined in [`/core/wsgi.py`](/core/wsgi.py)) and binds it to port `8000`.
  Gunicorn is a Python WSGI HTTP Server, and is used to host our application in
  production.

The working directory is then set back to the root of the container.

```Dockerfile
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
WORKDIR /app
COPY LICENSE .en[v] core.d[b] core.sqlit[e] sqlite3.d[b] manage.py ./
RUN chmod +x manage.py
```

This section copies the virtual environment from the builder container to the
runtime container and copies the application files into the container.

```Dockerfile
COPY core/ ./core
COPY api_htmx/ ./api_htmx
COPY api_rest/ ./api_rest
COPY ratemymodule/ ./ratemymodule/
COPY web/ ./web/
```

This section copies the application code into the container.

```Dockerfile
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
```

This line specifies the entrypoint for the container, which is the entrypoint
script created earlier.

## Integrating Docker into the GitLab Development Pipeline

The CI/CD pipeline allows for Docker images to be automatically built upon
merging with the main branch. This means the latest version of our application
is always available to be tested and deployed.

The steps below show the flow from a commit to deployment:

1. Commit: A team member merges their branch into the main repository.
2. Build: The CI/CD pipeline is triggered, and the application is tested and
   built in a Docker container using the [`Dockerfile`](/Dockerfile)
   and [`.gitlab-ci.yml`](/.gitlab-ci.yml) files.
3. Image: A Docker image is created and pushed to the GitLab Container
   Registry.
4. Deploy: The Docker image is deployed to the production environment.

Our `.gitlab-ci.yml` file contains the following notable configurations:

```yaml
stages:
  - check
  - test
  - build
```

This section defines the stages of the pipeline. The `check` stage is used to
check the code for any issues, the `test` stage is used to run the application
tests, and the `build` stage is used to build the Docker image.

A series of jobs are then defined for each stage. We won't go into the check
and test stages here, but they include:

- `check-updated-tag` - checking that the version specified in
  the `pyproject.toml` file matches the tag that triggered the pipeline.
- `mypy-test` - performing static type checking on the application code
  using `mypy`.
- `ruff-test` - performing linting on the application code using `ruff`.
- `pre-commit-test` - performing pre-commit checks on the application code
  using `pre-commit`.

Our `build` stage contains the following jobs:

```yaml
build-latest-docker-image:
  stage: build
  tags:
    - docker
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  before_script:
    - echo "logging in to registry:$CI_REGISTRY as $CI_REGISTRY_USER"
    - >
      docker login $CI_REGISTRY -u $CI_REGISTRY_USER
      -p $CI_REGISTRY_PASSWORD
    - echo "pulling most recent latest image for caching"
    - docker pull $CI_REGISTRY_IMAGE:latest || true
  script:
    - echo "building docker image latest version:$CI_COMMIT_SHA"
    - >
      docker build --cache-from $CI_REGISTRY_IMAGE:latest
      --tag $CI_REGISTRY_IMAGE:latest
      --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - echo "pushing built images to GitLab repository"
    - docker push $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

```

This job builds the Docker image for the latest version of the application and
pushes it to the GitLab Container Registry. It uses the `latest` tag for the
latest version and the commit SHA for the specific version.

```yaml
build-stable-docker-image:
  stage: build
  tags:
    - docker
  rules:
    - if: $CI_COMMIT_TAG
  when: manual
  before_script:
    - echo "logging in to registry:$CI_REGISTRY as $CI_REGISTRY_USER"
    - >
      docker login $CI_REGISTRY -u $CI_REGISTRY_USER
      -p $CI_REGISTRY_PASSWORD
    - echo "pulling most recent stable image for caching"
    - docker pull $CI_REGISTRY_IMAGE:stable || true
  script:
    - echo "building docker image stable version:$CI_COMMIT_TAG"
    - >
      docker build --cache-from $CI_REGISTRY_IMAGE:stable
      --tag $CI_REGISTRY_IMAGE:stable
      --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
      --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG .
    - echo "pushing built images to GitLab repository"
    - docker push $CI_REGISTRY_IMAGE:stable
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG

```

This job builds the Docker image for the stable version of the application and
pushes it to the GitLab Container Registry. It uses the `stable` tag for the
stable version, the commit SHA for the specific version, and the tag that
triggered the pipeline.

For deployment to the production environment, we have created
a `docker-compose.yml` file which contains the following services, networks and
volumes:

Services:

```yaml
latestratemymoduleproxy:
  container_name: latestratemymoduleproxy
  hostname: latestratemymoduleproxy
  image: nginx:alpine
  volumes:
    - latest_static:/static
    - /ratemymodule/latest-default.conf:/etc/nginx/conf.d/default.conf:ro
  networks:
    - frontend
    - backend
  restart: unless-stopped
  labels: [ "com.centurylinklabs.watchtower.scope=ratemymodule" ]
  depends_on:
    - latestratemymoduleapp
```

This service is used to host the static files for the latest version of the
application using a Nginx web server. It mounts the `latest_static` volume to
store the static files and the `latest-default.conf` file to configure the
Nginx server.

```yaml
 latestratemymoduleapp:
   container_name: latestratemymoduleapp
   hostname: latestratemymoduleapp
   volumes:
     - latest_static:/static
     - /ratemymodule/latest-core.db:/app/core.db
   environment:
     SECRET_KEY: *****
     OAUTH_GOOGLE_CLIENT_ID: *****.apps.googleusercontent.com
     OAUTH_MICROSOFT_CLIENT_ID: *****-****-****-****-*****
     OAUTH_GOOGLE_SECRET: *****
     OAUTH_MICROSOFT_SECRET: *****
     PRODUCTION: false
     DEBUG: true
     LOG_LEVEL: INFO
     EMAIL_TO_CONSOLE: false
     EMAIL_HOST: smtp.emailserver.example.com
     EMAIL_PASSWORD: *****
     EMAIL_PORT: 465
     EMAIL_HOST_USER: email@example.com
     EMAIL_USE_SSL: true
   image: git.cs.bham.ac.uk:5050/team-projects-2023-24/team55:latest
   networks:
     - backend
   restart: unless-stopped
   labels: [ "com.centurylinklabs.watchtower.scope=ratemymodule" ]
```

This service is used to host the latest version of the application using a
Gunicorn web server. It mounts the `latest_static` volume to store the static
files and the `latest-core.db` file to store the application database. It also
sets environment variables for the application, for example the `SECRET_KEY`
and `OAUTH_GOOGLE_CLIENT_ID`. It uses the `latest` tag to pull the latest
version of the application from the GitLab Container Registry, and deploys it
to the production environment.

```yaml
stableratemymoduleproxy:
  container_name: stableratemymoduleproxy
  hostname: stableratemymoduleproxy
  image: nginx:alpine
  volumes:
    - stable_static:/static
    - /ratemymodule/stable-default.conf:/etc/nginx/conf.d/default.conf:ro
  networks:
    - frontend
    - backend
  restart: unless-stopped
  labels: [ "com.centurylinklabs.watchtower.scope=ratemymodule" ]
  depends_on:
    - stableratemymoduleapp

  stableratemymoduleapp:
    container_name: stableratemymoduleapp
    hostname: stableratemymoduleapp
    volumes:
      - stable_static:/static
      - /ratemymodule/stable-core.db:/app/core.db
    environment:
      SECRET_KEY: *****
      OAUTH_GOOGLE_CLIENT_ID: *****.apps.googleusercontent.com
      OAUTH_MICROSOFT_CLIENT_ID: *****-****-****-****-*****
      OAUTH_GOOGLE_SECRET: *****
      OAUTH_MICROSOFT_SECRET: *****
      PRODUCTION: true
      EMAIL_HOST: smtp.emailserver.example.com
      EMAIL_PASSWORD: ******
      EMAIL_PORT: 465
      EMAIL_HOST_USER: email@example.com
      EMAIL_USE_SSL: true
    image: git.cs.bham.ac.uk:5050/team-projects-2023-24/team55:stable
    networks:
      - backend
    restart: unless-stopped
    labels: [ "com.centurylinklabs.watchtower.scope=ratemymodule" ]
```

Similarly, these services are used to host the stable version of the
application using Nginx and Gunicorn web servers. They mount
the `stable_static` volume to store the static files and the `stable-core.db`
file to store the application database. They also set environment variables for
the application, for example the `SECRET_KEY` and `OAUTH_GOOGLE_CLIENT_ID`.
They use the `stable` tag to pull the stable version of the application from
the GitLab Container Registry, and deploy it to the production environment.

```yaml
ratemymodulewatchtower:
  container_name: ratemymodulewatchtower
  hostname: ratemymodulewatchtower
  image: containrrr/watchtower
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - /.docker/config.json:/config.json:ro
  command: --interval 30 --scope ratemymodule
  labels: [ "com.centurylinklabs.watchtower.scope=ratemymodule" ]
  networks:
    - frontend
```

This service is used to automatically update the application containers when a
new version of the application is available. It uses
the `containrrr/watchtower` image to monitor the GitLab Container Registry for
new versions of the application, and updates the application containers when a
new version is available.

Networks:

```yaml
networks:
  frontend:
    name: proxy-apps
    external: true
  backend:
```

These networks are used to connect the application containers to the Nginx
proxy containers.

Volumes:

```yaml
volumes:
  latest_static:
  stable_static:
```

These volumes are used to store the static files for the application.

This `docker-compose.yml` file is then used to deploy the application to the
production environment using the following command:

```bash
docker-compose -f docker-compose.yml up -d
```

This command uses the `docker-compose.yml` file to create and start the
application containers in the background, and the `-d` flag is used to run the
containers in detached mode.

## Versioning and Scalability

Docker containers are designed with version control and scalability in mind.

Everytime we make changes to our main branch, a new Docker image is built and
pushed to the GitLab Container Registry. This allows us to keep track of
different versions of our application and easily roll back to a previous
version if needed. This also allows us to have a `stable` version of our
application that is always available for deployment as well as a `latest`
version that is continuously updated with the latest changes.

With future scalability in mind, Docker containers can be easily scaled up to
meet the demands of our application. This could be done by running multiple
instances of the same container across different machines or servers, allowing
us to handle increased traffic and load on our application without any
downtime. Tools like Docker Swarm and Kubernetes can be used to manage and
orchestrate these containers, ensuring that they are distributed and scaled
effectively. Whilst this is not currently implemented, it is a feature that we
can easily integrate into our application in the future.

## More Resources

For more information on Docker and containerization, please refer to the
following resources:

- [Docker Documentation](https://docs.docker.com/)
- [Docker Engine](https://www.docker.com/products/container-runtime/)
- [Docker Scalability](https://docs.docker.com/engine/swarm/)
- [Docker Best Practices](https://www.docker.com/resources/best-practices)
- [Docker Security](https://www.docker.com/resources/security)
