# === [ STAGE 1 ] ===
FROM library/python:3.8.5-alpine as base
FROM base as builder

RUN mkdir /install
WORKDIR /install

# Install requirements and libraries.
#   --no-cache allows users to install packages with an index that is updated and used on-the-fly and not cached locally
RUN apk --no-cache add gcc make g++ bash git openssh \
    postgresql-dev curl build-base libffi-dev python-dev py-pip \
    jpeg-dev zlib-dev libsass-dev

# Install pillow globally.
ENV LIBRARY_PATH=/lib:/usr/lib

# Add requirements.txt before rest of repo for caching.
COPY requirements.txt /requirements.txt

# Install project dependencies before copying the rest of the codebase.
RUN python -m pip install --install-option="--prefix=/install" -r /requirements.txt

# === [ STAGE 2 ] ===
FROM base
COPY --from=builder /install /usr/local

RUN apk --no-cache --quiet add libpq

# Set project path for use throughout the script.
ENV PROJECT_PATH=/usr/src/app

# Echo the directory to install as a sanity check.
RUN echo "Installing into $PROJECT_PATH..."

# Create project directory on the image.
RUN mkdir -p $PROJECT_PATH

# Run all commands in this new directory.
WORKDIR $PROJECT_PATH

# Copy this directory to the image.
COPY . $PROJECT_PATH

# Open port 80 to traffic.
EXPOSE 8080 80 443

# Run a startup script in the specified directory.
CMD sh /usr/src/app/run.sh