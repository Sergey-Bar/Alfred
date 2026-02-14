#!/bin/bash

# Script to expand Storybook coverage and add interactive component documentation

# Check if Storybook is installed
if ! command -v npx &> /dev/null
then
    echo "npx not found. Please install Node.js and npm to proceed."
    exit 1
fi

# Initialize Storybook if not already set up
if [ ! -d "./.storybook" ]; then
    echo "Initializing Storybook..."
    npx sb init
else
    echo "Storybook is already initialized."
fi

# Add interactive documentation for components
COMPONENTS_DIR="./src/components"
STORIES_DIR="./src/stories"

if [ ! -d "$STORIES_DIR" ]; then
    mkdir -p $STORIES_DIR
fi

echo "Adding Storybook stories for components..."
for COMPONENT in $COMPONENTS_DIR/*.jsx; do
    COMPONENT_NAME=$(basename $COMPONENT .jsx)
    STORY_FILE="$STORIES_DIR/${COMPONENT_NAME}.stories.jsx"
    if [ ! -f "$STORY_FILE" ]; then
        cat <<EOL > $STORY_FILE
import React from 'react';
import { $COMPONENT_NAME } from '../components/$COMPONENT_NAME';

export default {
  title: 'Components/$COMPONENT_NAME',
  component: $COMPONENT_NAME,
};

export const Default = () => <$COMPONENT_NAME />;
EOL
        echo "Story added for $COMPONENT_NAME."
    else
        echo "Story already exists for $COMPONENT_NAME."
    fi
done

echo "Storybook coverage expanded."