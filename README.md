# wherethenews

A Web-App showing places mentioned in the news on a map.

Scraping news sites (currently only derStandard.at) with **python** and **selenium**

Geoparsing with external services using **geopy**

Managing data with an SQLite database using **flask_sqlalchemy**

Displaying results with **Flask / Leaflet.js**

**Try it:** [ryepenchi.gihub.io/wherethenews](https://ryepenchi.github.io/wherethenews) (Hopefully a live version)

### Ubuntu 20.04 Server Setup
```
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv unzip
```
### Chromium + Webdriver
```
sudo apt install chromium-browser chromium-chromedriver
```
### Project Files
```
wget https://github.com/ryepenchi/wherethenews/archive/master.zip
unzip master.zip && rm master.zip && mv wherethenews-master wherethenews && cd wherethenews
```
or if git is available
```
git clone https://github.com/ryepenchi/wherethenews.git && cd wherethenews

```
### Virtual environment and Python packages
```
python3.8 -m venv wherethenews
source wherethenews/bin/activate
pip install wheel
pip install -r requirements.txt
```
### Download a pre-trained model for the spacy NER
```
python -m spacy download de_core_news_md
```
### Initialize the Database
```
python wherethenews/dbconfig.py
```
### Test the scraper
```
python wherethenews/scraper.py
```
### Set up cron job to periodically run scraper
```
crontab -e
```
and add (couldve made it less confusing by calling the subdirectory 'src')
```
20 * * * * /home/bright/wherethenews/bin/python wherethenews/wherethenews/scraper.py -a
```
### Start Flask Server
Followed the instructions at
https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-20-04
