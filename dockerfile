# 1. Use the official Python image from DockerHub as the base image
FROM --platform=linux/amd64 python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the current directory (your Flask app) contents into the container's /app directory
COPY . /app

# 4. Install the required Python dependencies listed in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# 5. Expose port 8080 to be used by the container (Google Cloud Run requires Flask to run on port 8080)
EXPOSE 8080

# 6. Set environment variable to ensure that Python output is sent straight to terminal (unbuffered)
ENV PYTHONUNBUFFERED=1

# 7. Run the Flask app by default when the container starts
CMD ["python", "app.py"]