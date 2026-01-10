FROM python:3.11-slim

LABEL maintainer="Splice3D Contributors"
LABEL description="Splice3D G-code post-processor"
LABEL version="0.1.0"

# Set working directory
WORKDIR /app

# Copy post-processor files
COPY postprocessor/ ./postprocessor/
COPY cli/ ./cli/
COPY samples/ ./samples/

# Install dependencies
RUN pip install --no-cache-dir -r postprocessor/requirements.txt

# Set up PATH
ENV PATH="/app/postprocessor:${PATH}"
ENV PYTHONPATH="/app"

# Default command shows help
CMD ["python", "postprocessor/splice3d_postprocessor.py", "--help"]

# Usage examples:
# 
# Build:
#   docker build -t splice3d .
#
# Run post-processor:
#   docker run -v $(pwd):/data splice3d \
#     python postprocessor/splice3d_postprocessor.py /data/model.gcode
#
# Interactive shell:
#   docker run -it -v $(pwd):/data splice3d /bin/bash
#
# Run simulator:
#   docker run -v $(pwd):/data splice3d \
#     python cli/simulator.py /data/recipe.json
