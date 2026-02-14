#!/bin/bash

# Script to set up automated security scanning tools

# Install Snyk for dependency vulnerability scanning
if ! command -v snyk &> /dev/null
then
    echo "Installing Snyk..."
    npm install -g snyk
else
    echo "Snyk is already installed."
fi

# Install Bandit for Python static code analysis
if ! command -v bandit &> /dev/null
then
    echo "Installing Bandit..."
    pip install bandit
else
    echo "Bandit is already installed."
fi

# Run initial scans
echo "Running initial Snyk scan..."
snyk test

echo "Running initial Bandit scan..."
bandit -r ../dev/app

# Schedule scans (example using cron)
crontab -l > mycron
# Add new cron jobs
{
    echo "0 0 * * 0 snyk test > snyk_report.log"
    echo "0 1 * * 0 bandit -r ../dev/app > bandit_report.log"
} >> mycron
crontab mycron
rm mycron

echo "Security scanning setup complete."