FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

# Set working directory
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv
RUN uv sync --locked

# Copy application code
COPY ./frontend .

# Expose Streamlit port
EXPOSE 8501

# Command to run Streamlit application
# streamlit run app.py --server.port 8501 --server.address 0.0.0.0
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 