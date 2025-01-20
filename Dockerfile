FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the source code into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH to include the /app directory
ENV PYTHONPATH=/app

# Expose the application port
EXPOSE 8080

# Run the application
CMD ["python", "src/main.py"]
