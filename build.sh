<<<<<<< HEAD
=======
#!/bin/bash

#Build the project
echo "Building the project..."
python3.9 -m pip install -r requirements.txt

echo "Migrations..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput
>>>>>>> c85b2298e5d0f5005fa87b3ee7b2b72d93b910d1
