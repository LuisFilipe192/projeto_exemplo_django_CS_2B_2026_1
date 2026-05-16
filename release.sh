#!/bin/bash
echo "Running migrations..."
python manage.py migrate
echo "Migrations completed."