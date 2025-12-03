#!/bin/bash
# prepare_build_push.sh - Complete setup script for EC2

# Assumes you have git (since you cloned this), chmod u+x prepare_build_push.sh and sudo ./prepare_build_push.sh

set -e  # Exit on any error

echo "=== Starting EC2 Docker setup ==="

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

# 6. Try to run docker (might need sudo on first run)
if docker run --rm hello-world &>/dev/null; then
    echo "Docker works without sudo!"
else
    echo "Using sudo for first Docker command..."
    sudo docker run --rm hello-world
fi

# 7. Build and run (if in correct directory)
if [ -f "docker-compose.yml" ]; then
    echo "Building and starting services..."
    docker compose build --no-cache
    docker compose up -d
    echo "Services started!"
    docker compose ps
else
    echo "No docker-compose.yml found in current directory."
    echo "Navigate to your project directory and run:"
    echo "  docker compose up -d --build"
fi
