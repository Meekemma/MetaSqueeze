FROM python:3.11.4

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install pandoc, LibreOffice, and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pandoc \
    libreoffice \
    libreoffice-java-common && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pandoc --version && \
    libreoffice --version

# Set working directory
WORKDIR /usr/src/app

# Install Python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --timeout=120 -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000