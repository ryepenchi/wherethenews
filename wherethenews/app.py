import sys
import random
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil import parser as dp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from dbconfig import Article, Place

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/points')
def points():
    # defaults to today
    from_date = request.args.get("from_date", datetime.now())
    print("Received from_date: ", from_date)
    from_date = dp.parse(from_date)
    from_date = datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0)
    to_date = request.args.get("to_date", datetime.now())
    print("Receibed to_date: ", to_date)
    to_date = dp.parse(to_date)
    to_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59)
    print("Parsed dates: ", from_date, to_date)
    points = Place.query.join(Place.articles).filter(from_date <= Article.pub_date, Article.pub_date <= to_date, Article.places != None).all()
    articles = Article.query.filter(from_date <= Article.pub_date, Article.pub_date <= to_date, Article.places != None).all()
    print("Found {} places and {} articles".format(len(points), len(articles)))
    p = []
    for point in points:
        links = [a.link for a in point.articles]
        p.append({"word":point.word, "links":links, "lat":point.lat, "lon":point.lon})
    a = []
    for article in articles:
        words = [p.word for p in article.places]
        a.append({"title":article.title, "words":words, "link":article.link})
    return jsonify({"points": p, "articles": a})

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'mkdb':
            db.create_all()
    else:
        app.run(host="0.0.0.0", debug=True)
