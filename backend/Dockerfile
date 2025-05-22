# Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (if your app uses a different port, change it here)
EXPOSE 8000

# Command to run the application (replace with your actual command)
# 예시: FastAPI를 uvicorn으로 실행하는 경우
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# 예시: Langserve를 직접 실행하는 경우 (langserve.cli 사용)
# CMD ["python", "-m", "langserve", "start", "--host", "0.0.0.0", "--port", "8000", "your_langgraph_module:chain"]
CMD ["echo", "Replace with your backend start command"] 