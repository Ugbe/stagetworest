<<<<<<< HEAD
=======
#!/bin/bash

#Build the project
echo "Building the project..."
python3.12 -m pip install -r requirements.txt

echo "Migrations..."
python3.12 manage.py makemigrations 
python3.12 manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python3.12 manage.py collectstatic --noinput
>>>>>>> c85b2298e5d0f5005fa87b3ee7b2b72d93b910d1
