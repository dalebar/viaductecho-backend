#!/bin/bash

# Zsh Setup Script for EC2
# Sets up Zsh with Oh My Zsh, syntax highlighting, and autosuggestions
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/dalebar/viaductecho-backend/main/scripts/setup_zsh.sh | bash
#   or
#   ./scripts/setup_zsh.sh

set -e

echo "=================================="
echo "Zsh Setup Script"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Install Zsh
echo "Installing Zsh..."
sudo apt update && sudo apt install zsh curl git -y
echo -e "${GREEN}✓ Zsh installed${NC}"

# Install Oh My Zsh (non-interactive)
echo ""
echo "Installing Oh My Zsh..."
if [ -d "$HOME/.oh-my-zsh" ]; then
    echo -e "${YELLOW}Oh My Zsh already installed, skipping...${NC}"
else
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    echo -e "${GREEN}✓ Oh My Zsh installed${NC}"
fi

# Install syntax highlighting plugin
echo ""
echo "Installing zsh-syntax-highlighting..."
ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
if [ -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
    echo -e "${YELLOW}Already installed, skipping...${NC}"
else
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
    echo -e "${GREEN}✓ zsh-syntax-highlighting installed${NC}"
fi

# Install autosuggestions plugin
echo ""
echo "Installing zsh-autosuggestions..."
if [ -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    echo -e "${YELLOW}Already installed, skipping...${NC}"
else
    git clone https://github.com/zsh-users/zsh-autosuggestions.git "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
    echo -e "${GREEN}✓ zsh-autosuggestions installed${NC}"
fi

# Configure .zshrc
echo ""
echo "Configuring .zshrc..."

# Set theme to bira
sed -i 's/^ZSH_THEME=.*/ZSH_THEME="bira"/' "$HOME/.zshrc"

# Enable plugins
sed -i 's/^plugins=.*/plugins=(git zsh-syntax-highlighting zsh-autosuggestions)/' "$HOME/.zshrc"

echo -e "${GREEN}✓ Configuration complete${NC}"

# Set Zsh as default shell
echo ""
echo "Setting Zsh as default shell..."
if [ "$SHELL" != "$(which zsh)" ]; then
    chsh -s $(which zsh)
    echo -e "${GREEN}✓ Zsh set as default shell${NC}"
else
    echo -e "${YELLOW}Zsh is already the default shell${NC}"
fi

echo ""
echo "=================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================="
echo ""
echo "To start using Zsh now, run:"
echo "  exec zsh"
echo ""
echo "Or log out and log back in."
echo ""
