# Use the official Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables to avoid Python buffering and to specify production mode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY . .

# Expose the port your app runs on
EXPOSE 8080

# Command to start the Gunicorn server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "main:app"]
