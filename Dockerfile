# Use the official Python image as a base
FROM python:3.10.19-slim

# Set the working directory in the container
WORKDIR /app

# Copy the main application file into the container
COPY main.py .
COPY src/ /app/src/
COPY .env /app/

# Install any dependencies specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Command to run the application
CMD ["python", "main.py"]
