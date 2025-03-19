FROM python:3.9-slim

WORKDIR /app

# Copy the application files
COPY main.py /app/
COPY hosts /app/

# Make the script executable
RUN chmod +x /app/main.py

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the hosts manager in daemon mode
CMD ["python3", "/app/main.py"]
