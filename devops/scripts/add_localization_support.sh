#!/bin/bash

# Script to add localization/i18n support for global teams

# Define localization directory
LOCALE_DIR="frontend/src/locales"

# Create localization directory and files
echo "Setting up localization support..."
mkdir -p $LOCALE_DIR

# Add English translations
cat <<EOL > $LOCALE_DIR/en.json
{
  "welcome": "Welcome",
  "dashboard": "Dashboard",
  "settings": "Settings",
  "help": "Help"
}
EOL

# Add Spanish translations
cat <<EOL > $LOCALE_DIR/es.json
{
  "welcome": "Bienvenido",
  "dashboard": "Tablero",
  "settings": "Configuraciones",
  "help": "Ayuda"
}
EOL

# Integrate i18n library into the frontend
I18N_FILE="frontend/src/i18n.js"

if [ ! -f $I18N_FILE ]; then
    echo "Creating i18n integration file..."
    cat <<EOL > $I18N_FILE
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import es from './locales/es.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      es: { translation: es },
    },
    lng: 'en',
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  });

export default i18n;
EOL
else
    echo "i18n integration file already exists."
fi

echo "Localization/i18n support setup complete."