# 1. Use the official Playwright image (includes Node.js and all browser dependencies)
FROM mcr.microsoft.com/playwright:v1.42.0-jammy

# 2. Install Python 3 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy Node.js dependencies and install them
COPY package.json package-lock.json* ./
RUN npm install

# 5. Copy Python dependencies and install them
# (If you don't have a requirements.txt yet, we can create a simple one!)
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your framework's code
COPY . .

# 7. Set the default command when the container starts
# We will default to keeping the container alive so we can send commands to it
CMD ["tail", "-f", "/dev/null"]