FROM python:3.10

# Set up workdir
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --upgrade pip && pip3 install -r requirements.txt

COPY src/ src/
