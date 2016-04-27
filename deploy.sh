#This script is to only be run independantly on a new EC2 instance
#It should never run from the actual ServiceLearningNew Repo

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

python manage.py makemigrations
python manage.py migrate

echo "migration complete"

sudo nohup python manage.py runserver &

echo "application is running on port 8000"