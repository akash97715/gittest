[6:50 PM] Deep, Akash (External)
[build-image 5/6] RUN  pip3 install --target /function -r requirements.txt:
1750.626 Collecting vsl_utils@ git+https://github.com/pfizer/vessel-services.git@dev#subdirectory=utils/vsl_utils (from -r requirements.txt (line 16))
1760.628   Cloning https://github.com/pfizer/vessel-services.git (to revision dev) to /tmp/pip-install-ebqcaa20/vsl-utils_2cd92362e3df4960b9db7187b1439681
1770.633   ERROR: Error [Errno 2] No such file or directory: 'git' while executing command git version
1780.634 ERROR: Cannot find command 'git' - do you have 'git' installed and in your PATH?
1790.848
180Notice: 0.848 [notice] A new release of pip is available: 23.3 -> 24.1.2
181Notice: 0.848 [notice] To update, run: pip install --upgrade pip
182------
183Dockerfile:16
184--------------------
185  14 |     
186  15 |     # Install the function's dependencies
187  16 | >>> RUN  pip3 install --target ${FUNCTION_DIR} -r requirements.txt
188  17 |     RUN pip3 install --target ${FUNCTION_DIR} awslambdaric
 
[6:50 PM] Deep, Akash (External)
# Define custom function directory
ARG FUNCTION_DIR="/function"
 
FROM 420737321821.dkr.ecr.us-east-1.amazonaws.com/core-vsl-python3.11-slim as build-image
 
# Include global arg in this stage of the build
ARG FUNCTION_DIR
 
# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
 
# Install the function's dependencies
RUN  pip3 install --target ${FUNCTION_DIR} -r requirements.txt
RUN pip3 install --target ${FUNCTION_DIR} awslambdaric
 
FROM 420737321821.dkr.ecr.us-east-1.amazonaws.com/core-vsl-python3.11-slim
 
# Update package lists and install required packages
RUN apt-get update \
&& apt-get install -y \
        rpm \
        curl \
        libgl1 \
        poppler-utils \  
        libmagic-dev \
        libreoffice \
        git \
&& rm -rf /var/lib/apt/lists/*  
 
 
# Include global arg in this stage of the build
ARG FUNCTION_DIR
 
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
 
ARG GITHUB_TOKEN
 
# Set the environment variable GITHUB_TOKEN to the value of the build argument
ENV GITHUB_TOKEN ${GITHUB_TOKEN}
 
# Configure git with the GITHUB_TOKEN for the specific GitHub repository:
# This command will only replace "https://github.com/pfizer/vessel-services" with "https://${GITHUB_TOKEN}:x-oauth-basic@github.com/pfizer/vessel-services"
# so that Git operations on the specific pfizer repository will use the provided token for authentication.
RUN git config --global url."https://${GITHUB_TOKEN}:x-oauth-basic@github.com/pfizer/vessel-services".insteadOf "https://github.com/pfizer/vessel-services"
 
# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
 
# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "app.lambda_handler" ]
 
