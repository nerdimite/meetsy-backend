# Pull Hub API base image
FROM 495274804427.dkr.ecr.us-east-1.amazonaws.com/hub-api-base:latest

# Create and set function dir
ARG FUNCTION_DIR="/function/"
RUN mkdir -p ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}

# Install requirements
COPY src/requirements.txt ${FUNCTION_DIR}
RUN pip install -r requirements.txt --target ${FUNCTION_DIR}

# Copy source code
COPY src/* ${FUNCTION_DIR}

# ==================== DO NOT EDIT =========================
ENTRYPOINT [ "/entry_script.sh" ]
CMD [ "main.inference_handler" ]
# ==========================================================