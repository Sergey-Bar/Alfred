#!/bin/bash

# Script to implement accessibility (a11y) testing and improvements

# Check if axe-core CLI is installed
if ! command -v axe &> /dev/null
then
    echo "axe-core CLI not found. Installing..."
    npm install -g axe-core
else
    echo "axe-core CLI is already installed."
fi

# Define the directory for accessibility reports
REPORTS_DIR="a11y-reports"
mkdir -p $REPORTS_DIR

# Run accessibility tests on key pages
echo "Running accessibility tests..."
axe frontend/public/index.html --save $REPORTS_DIR/index.html.json
axe frontend/public/dashboard.html --save $REPORTS_DIR/dashboard.html.json

# Provide recommendations for improvements
echo "Accessibility testing complete. Review the reports in the $REPORTS_DIR directory."
echo "Recommendations:"
echo "1. Fix color contrast issues."
echo "2. Add ARIA labels to interactive elements."
echo "3. Ensure all images have alt text."
echo "4. Verify keyboard navigation works on all pages."