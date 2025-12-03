#!/bin/bash
# prepare_build_push.sh - Complete setup script for EC2

# Assumes you have git (since you cloned this), modified .env file and sudo ./prepare_build_push.sh

set -e  # Exit on any error

echo "---Starting EC2 Docker setup---"

# 1. System updates
echo "Updating system..."
sudo apt update
sudo apt upgrade -y

# 2. Install essential tools
echo "Installing essential tools..."
sudo apt install -y \
    curl \
    wget \
    unzip \
    net-tools \
    htop \
    nano \
    tree \
    ca-certificates \
    gnupg \
    lsb-release

# 3. Install Docker
echo "Installing Docker..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 4. Configure Docker
echo "Configuring Docker..."
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# 5. Verify Docker works
echo "Verifying Docker installation..."
docker --version
docker compose version

cd ..

# Check .env file
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with the following variables:"
    echo ""
    echo "DB_USER=postgres"
    echo "DB_PASSWORD=your_password_here"
    echo "DB_NAME=projeto_gps"
    echo ""
fi

# Validate .env has required variables
echo "Checking .env file contents..."
REQUIRED_VARS=("DB_USER" "DB_PASSWORD" "DB_NAME")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${var}=" .env; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "ERROR: .env file is missing required variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please add these to your .env file and run the script again."
    exit 1
fi

echo ".env file looks good!"
echo ""

# 6. Try to run docker (might need sudo on first run)
if docker run --rm hello-world &>/dev/null; then
    echo "Docker works without sudo!"
else
    echo "Using sudo for first Docker command..."
    sudo docker run --rm hello-world
fi

# 7. Build
if [ -f "docker-compose.yml" ]; then
    echo "Building docker compose file..."
    docker compose build --no-cache
    echo "Built!"
else
    echo "No docker-compose.yml found in current directory."
fi
