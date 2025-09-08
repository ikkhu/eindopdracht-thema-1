# Gebruik Python 3.9 slim image
FROM python:3.9-slim

# Stel werkdirectory in
WORKDIR /app

# Installeer systeem dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopieer requirements bestand
COPY requirements.txt .

# Installeer Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer applicatie bestanden
COPY app.py .
COPY index.html .
COPY admin.html .

# Maak een gebruiker aan voor security
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose poort
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start applicatie
CMD ["python", "app.py"]