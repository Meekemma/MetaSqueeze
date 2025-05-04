FROM python:3.11.4

# Set environment variables to prevent Python from writing .pyc files and buffering output
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy requirements first to leverage Docker caching during builds
COPY ./requirements.txt /usr/src/app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --timeout=120 -r requirements.txt


# Copy the rest of the application code into the container
COPY . .

# Expose the port that Django will run on (8000 by default)
EXPOSE 8000

# CMD is handled by docker-compose.yml


