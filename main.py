# Use the specified base image from the private registry
ARG BASE_IMAGE=420737321821.dkr.ecr.us-east-1.amazonaws.com/core-vsl-python3.11-slim
FROM $BASE_IMAGE

# Set the working directory inside the container
WORKDIR /backend

# Install system dependencies
# Assuming Debian-based image as we are using apt-get
RUN apt-get update && apt-get install -y \
    poppler-utils \    # Install poppler-utils for PDF processing
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Copy the requirements file first to leverage Docker cache
COPY ./requirements.txt /backend/

# Install Python dependencies from requirements file
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

# Copy the rest of the application code into the container
COPY . /backend/

# Install the application (editable mode assumes setup.py is present)
RUN pip install -e .

# Optional: Uncomment and modify if you need to use a non-root user
# RUN addgroup --system testgroup && adduser --system --group testuser
# USER testuser

# Expose port 8000 for the application
EXPOSE 8000

# Set the command to run the application
# Update this command according to how you actually run your application, e.g., using a WSGI server like Gunicorn
CMD ["python", "/backend/main.py"]
