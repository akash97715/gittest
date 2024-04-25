FROM 420737321821.dkr.ecr.us-east-1.amazonaws.com/core-vsl-python3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=warning

# Update package lists and install required packages
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        libgl1 \
        poppler-utils \  # Ensure poppler-utils is included for PDF processing
        libmagic-dev \
        libreoffice \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

COPY requirements.txt .
COPY libzip.tar .

RUN python -m pip install --no-cache-dir -r requirements.txt
RUN python -m pip list

WORKDIR /app

# Copy the application code into the container
COPY . /app

EXPOSE 8000

RUN chmod 700 prestart.sh
ENTRYPOINT ["/bin/bash"]
CMD ["./prestart.sh"]
