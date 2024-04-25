# don't know right image in the private registry. replace this with right image
ARG BASE_IMAGE=420737321821.dkr.ecr.us-east-1.amazonaws.com/core-vsl-python3.11-slim
FROM $BASE_IMAGE
#ARG BASE_IMAGE=python:3.10-slim
 
# FROM python:3.9.17
 
 
# Create a new user and group
# RUN addgroup --system testgroup && adduser --system --group testuser
 
# Set the working directory
WORKDIR /backend
 
 
 
# Copy only the requirements file to avoid rebuilding dependencies
COPY ./requirements.txt /backend/
 
# Install any needed packages specified in requirements.txt using apk and pip
RUN pip install --no-cache-dir --upgrade pip
# keeping it separate as the req file might need update and also to cache the previous step
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
 
## Copy the application code into the container
COPY . /backend/
RUN pip install -e .
 
# Switch to non-root user
# USER testuser
#ARG URL_PATTERN=vox
#ENV URL_PATTERN=$URL_PATTERN
 
# Expose port 80 to the Docker host, so we can access the application outside the container
EXPOSE 8000
 
#ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*", "--access-log", "--log-level", "info"]
# RUN set PYTHONPATH=$PWD
CMD ["python", "/backend/main.py"]
