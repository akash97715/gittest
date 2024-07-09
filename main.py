# Define custom function directory
ARG FUNCTION_DIR="/function"

# Base image for building dependencies
FROM 420737321821.dkr.ecr.us-east-1.amazonaws.com/core-vsl-python3.11-slim as build-image

# Include global args in this stage of the build
ARG FUNCTION_DIR
ARG GITHUB_TOKEN

# Install git and any other necessary build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the environment variable GITHUB_TOKEN to the value of the build argument
ENV GITHUB_TOKEN ${GITHUB_TOKEN}

# Configure git with the GITHUB_TOKEN for the specific GitHub repository:
RUN git config --global url."https://${GITHUB_TOKEN}:x-oauth-basic@github.com/pfizer/vessel-services".insteadOf "https://github.com/pfizer/vessel-services"

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Install the function's dependencies
RUN pip3 install --target ${FUNCTION_DIR} -r requirements.txt
RUN pip3 install --target ${FUNCTION_DIR} awslambdaric

# Production image
FROM 420737321821.dkr.ecr.us-east-1.amazonaws.com/core-vsl-python3.11-slim

# Install necessary runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    rpm \
    curl \
    libgl1 \
    poppler-utils \  
    libmagic-dev \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

ARG GITHUB_TOKEN

# Set the environment variable GITHUB_TOKEN to the value of the build argument
ENV GITHUB_TOKEN ${GITHUB_TOKEN}

# Configure git with the GITHUB_TOKEN for the specific GitHub repository:
RUN git config --global url."https://${GITHUB_TOKEN}:x-oauth-basic@github.com/pfizer/vessel-services".insteadOf "https://github.com/pfizer/vessel-services"

# Copy in the built dependencies from the build image
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# Pass the name of the function handler as an argument to the runtime
CMD [ "app.lambda_handler" ]
