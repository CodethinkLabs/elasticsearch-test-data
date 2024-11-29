### --------------------------------------------------------------------
### Docker Build Arguments
### Available only during Docker build - `docker build --build-arg ...`
### --------------------------------------------------------------------
ARG DEBIAN_VERSION="buster"
ARG ALPINE_VERSION="3.12"
ARG PYTHON_VERSION="3.9.1"
ARG APP_PYTHON_USERBASE="/app"
ARG APP_USER_NAME="appuser"
ARG APP_USER_ID="1000"
ARG APP_GROUP_NAME="appgroup"
ARG APP_GROUP_ID="1000"
# Reminder- the ENTRYPOINT is hardcoded so make sure you change it (remove this comment afterwards)
### --------------------------------------------------------------------


### --------------------------------------------------------------------
### Build Stage
### --------------------------------------------------------------------
FROM python:"$PYTHON_VERSION"-slim-"${DEBIAN_VERSION}" as build

ARG APP_PYTHON_USERBASE

# Define env vars
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUSERBASE="$APP_PYTHON_USERBASE" \
    PATH="${APP_PYTHON_USERBASE}/bin:${PATH}"

# Upgrade pip and then install build tools
RUN pip install --upgrade pip && \
    pip install --upgrade wheel setuptools wheel

# Define workdir
WORKDIR "$APP_PYTHON_USERBASE"

# Install the app
COPY requirements.txt .
RUN pip install --ignore-installed --no-warn-script-location --prefix="/dist" -r requirements.txt

WORKDIR /dist/

COPY modules ./modules/
COPY search_test.py .

# For debugging the Build Stage
CMD ["bash"]
### --------------------------------------------------------------------


### --------------------------------------------------------------------
### App Stage
### --------------------------------------------------------------------
FROM python:"$PYTHON_VERSION"-alpine"${ALPINE_VERSION}" as app

# Fetch values from ARGs that were declared at the top of this file
ARG APP_NAME
ARG APP_PYTHON_USERBASE
ARG APP_USER_ID
ARG APP_USER_NAME
ARG APP_GROUP_ID
ARG APP_GROUP_NAME

# Define env vars
ENV HOME="$APP_PYTHON_USERBASE" \
    PYTHONUSERBASE="$APP_PYTHON_USERBASE" \
    PYTHONUNBUFFERED=0
ENV PATH="${PYTHONUSERBASE}/bin:${PATH}"

# Define workdir
WORKDIR "$PYTHONUSERBASE"

# Run as a non-root user
RUN \
    addgroup -g "${APP_GROUP_ID}" "${APP_GROUP_NAME}" && \
    adduser -H -D -u "$APP_USER_ID" -G "$APP_GROUP_NAME" "$APP_USER_NAME" && \
    chown -R "$APP_USER_ID":"$APP_GROUP_ID" "$PYTHONUSERBASE"
USER "$APP_USER_NAME"

# Copy artifacts from Build Stage
COPY --from=build --chown="$APP_USER_NAME":"$APP_GROUP_ID" /dist/ "$PYTHONUSERBASE"/

# Use ENTRYPOINT instead CMD to force the container to start the application
ENTRYPOINT ["python", "search_test.py"]
