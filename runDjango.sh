#this script should be able to run django on a server that has gone through the setup script
cd ~

export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

workon djangoApps2

cd ServiceLearningNew

echo "pip install began"

pip install -r requirements.txt

echo "pip install complete"

python manage.py makemigrations
python manage.py migrate

echo "migration complete"

sudo nohup python manage.py runserver &

echo "application is running on port 8000"

