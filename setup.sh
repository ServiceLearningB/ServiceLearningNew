# This script installs all the correct basic software onto the ec2 server
# Should only ever have to be run once

cd ~

sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install python-pip -y
sudo apt-get install python-dev -y
sudo apt-get install build-essential -y
sudo pip install virtualenvwrapper

echo "finished setup"

export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

mkvirtualenv djangoApps2

echo "created virtual env"

workon djangoApps2

sudo pip install django
sudo apt-get install git-all -y
sudo git clone https://github.com/ServiceLearningB/ServiceLearningNew.git

echo "finished clone"

cd ServiceLearningNew

echo "pip install began"

pip install -r requirements.txt

echo "pip install complete"


down vote
Here there is a simple version of the script to create a superuser:

echo "from django.contrib.auth.models import User; User.objects.create_superuser('ubuntu', 'admin@example.com', 'SeaSalt52')" | python manage.py shell

echo "created super user USERNAME:ubuntu, PASSWORD:SeaSalt52"