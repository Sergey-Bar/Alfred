#!/bin/bash

# Script to add in-app onboarding and tooltips for new users

# Define onboarding configuration file
ONBOARDING_CONFIG="frontend/src/onboardingConfig.js"

# Create onboarding configuration file
echo "Creating in-app onboarding configuration..."
cat <<EOL > $ONBOARDING_CONFIG
export const onboardingSteps = [
  {
    id: 1,
    title: "Welcome to Alfred!",
    content: "This is your dashboard where you can manage your projects.",
    target: "#dashboard",
  },
  {
    id: 2,
    title: "Settings",
    content: "Here you can update your profile and configure your preferences.",
    target: "#settings",
  },
  {
    id: 3,
    title: "Help",
    content: "Need assistance? Visit our help center or contact support.",
    target: "#help",
  },
];
EOL

# Add tooltips to the frontend application
TOOLTIPS_FILE="frontend/src/tooltips.js"

if [ ! -f $TOOLTIPS_FILE ]; then
    echo "Creating tooltips configuration..."
    cat <<EOL > $TOOLTIPS_FILE
export const tooltips = {
  dashboard: "This is your main dashboard.",
  settings: "Update your profile and preferences here.",
  help: "Access help and support options.",
};
EOL
else
    echo "Tooltips configuration already exists."
fi

echo "In-app onboarding and tooltips setup complete."