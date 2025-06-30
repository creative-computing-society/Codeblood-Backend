# Use official Python 3.13 image (adjust if 3.13 isn't fully released yet)
FROM python:3.13-slim

# Set workdir inside container
WORKDIR /app

# Copy requirements first for caching layer
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code
COPY . .

# Expose port FastAPI will run on
EXPOSE 8000

# Run the app
CMD ["python", "main.py"]
