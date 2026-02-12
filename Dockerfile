# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

LABEL maintainer="Gemini Code Assist"
LABEL description="Dockerfile for Yumeko and Yumeko_Music Telegram Bot"

# Set non-interactive frontend for package installers
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# - git: for installing python packages from git
# - ffmpeg: for music functionality
# - Other libs: for playwright and other dependencies mentioned in README
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -U pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Install Playwright browser dependencies
RUN python3 -m playwright install chromium

# Copy the rest of the application code
COPY . .

# Make the entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Set the entrypoint for the container
ENTRYPOINT ["/app/docker-entrypoint.sh"]
