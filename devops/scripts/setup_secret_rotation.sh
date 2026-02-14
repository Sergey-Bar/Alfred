#!/bin/bash

# Script to automate secret and credential rotation using HashiCorp Vault

# Check if Vault CLI is installed
if ! command -v vault &> /dev/null
then
    echo "Vault CLI not found. Installing Vault..."
    # Install Vault (example for Linux)
    curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
    sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
    sudo apt-get update && sudo apt-get install vault
else
    echo "Vault CLI is already installed."
fi

# Initialize Vault (if not already initialized)
if [ ! -f /etc/vault.d/vault-init.txt ]; then
    echo "Initializing Vault..."
    vault operator init > /etc/vault.d/vault-init.txt
    echo "Vault initialized. Save the unseal keys and root token securely."
else
    echo "Vault is already initialized."
fi

# Unseal Vault
echo "Unsealing Vault..."
VAULT_KEYS=$(grep 'Unseal Key' /etc/vault.d/vault-init.txt | awk '{print $4}')
for key in $VAULT_KEYS; do
    vault operator unseal $key
done

# Enable secret engines
vault secrets enable -path=secret kv-v2

# Example: Rotate database credentials
echo "Rotating database credentials..."
vault write database/config/my-database \
    plugin_name=mysql-database-plugin \
    connection_url="{{username}}:{{password}}@tcp(127.0.0.1:3306)/" \
    allowed_roles="my-role" \
    username="root" \
    password="rootpassword"

vault write database/roles/my-role \
    db_name=my-database \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT ON *.* TO '{{name}}'@'%';" \
    default_ttl="1h" \
    max_ttl="24h"

# Schedule rotation (example using cron)
crontab -l > mycron
{
    echo "0 * * * * vault lease revoke -prefix database/creds/my-role"
} >> mycron
crontab mycron
rm mycron

echo "Secret rotation setup complete."