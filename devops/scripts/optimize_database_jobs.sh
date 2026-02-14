#!/bin/bash

# Script to profile and optimize database queries and background jobs

# Check if pg_stat_statements extension is enabled for PostgreSQL
DB_NAME="my_database"
DB_USER="my_user"
DB_HOST="localhost"
DB_PORT="5432"

# Enable pg_stat_statements if not already enabled
echo "Checking if pg_stat_statements is enabled..."
psql -U $DB_USER -d $DB_NAME -h $DB_HOST -p $DB_PORT -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

# Profile slow queries
echo "Profiling slow queries..."
psql -U $DB_USER -d $DB_NAME -h $DB_HOST -p $DB_PORT -c "SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"

# Optimize background jobs (example for Celery)
CELERY_LOG="/var/log/celery/worker.log"
echo "Analyzing Celery logs for slow tasks..."
grep -i "task" $CELERY_LOG | sort | uniq -c | sort -nr | head -n 10

# Recommendations for optimization
echo "Recommendations:"
echo "1. Add indexes to frequently queried columns."
echo "2. Optimize slow SQL queries using EXPLAIN ANALYZE."
echo "3. Use task prioritization in Celery to improve job execution."

echo "Database and background job optimization complete."