#!/bin/bash

# Script to add onboarding scripts and a "first PR" guide for new contributors

# Define onboarding script path
ONBOARDING_SCRIPT="onboarding.sh"

# Create onboarding script
echo "Creating onboarding script..."
cat <<EOL > $ONBOARDING_SCRIPT
#!/bin/bash

# Onboarding script for new contributors

# Clone the repository
echo "Cloning the repository..."
git clone https://github.com/your-repo/alfred.git

# Set up the development environment
echo "Setting up the development environment..."
cd alfred
./devops/scripts/setup_docker_compose_env.sh

# Install dependencies
echo "Installing dependencies..."
npm install
pip install -r backend/requirements/requirements-dev.txt

# Run tests
echo "Running tests..."
npm test
pytest

echo "Onboarding complete!"
EOL
chmod +x $ONBOARDING_SCRIPT

# Create "first PR" guide
FIRST_PR_GUIDE="FIRST_PR_GUIDE.md"
echo "Creating 'first PR' guide..."
cat <<EOL > $FIRST_PR_GUIDE
# First Pull Request Guide

Welcome to the Alfred project! Follow these steps to make your first contribution:

1. Fork the repository.
2. Clone your fork locally.
3. Create a new branch for your changes:
   ```
   git checkout -b my-new-feature
   ```
4. Make your changes and commit them:
   ```
   git add .
   git commit -m "Add my new feature"
   ```
5. Push your branch to your fork:
   ```
   git push origin my-new-feature
   ```
6. Open a pull request from your branch to the `main` branch of the original repository.

Thank you for contributing!
EOL

echo "Onboarding scripts and 'first PR' guide created."