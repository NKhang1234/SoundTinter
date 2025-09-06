#!/bin/bash

echo "Creating RabbitMQ users from .env..."

# Load env variables
set -a
. /etc/rabbitmq/.env
set +a

# Add users
rabbitmqctl add_user "$UPLOAD_USER" "$UPLOAD_PASS"
rabbitmqctl add_user "$ANALYST_USER" "$ANALYST_PASS"

# Set permissions (must match those defined in definitions.json)
rabbitmqctl set_permissions -p / "$UPLOAD_USER" "^upload_q$" "^upload_q$" ""
rabbitmqctl set_permissions -p / "$ANALYST_USER" "" "" "^upload_q$"
