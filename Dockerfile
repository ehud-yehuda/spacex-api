FROM python:3.10

# Set up workdir
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip && pip3 install -r requirements.txt
