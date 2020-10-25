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

#BASECOORDS = [-13.9626, 33.7741]
BASECOORDS = [48.210033,16.363449]

# class Point(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     latitude_off = db.Column(db.Float)
#     longitude_off = db.Column(db.Float)
#     district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
#     district = db.relationship("District")

#     def __init__(self, id, district, lat, lng):
#         self.id = id
#         self.district = district
#         self.latitude_off = lat
#         self.longitude_off = lng

#     def __repr__(self):
#         return "<Point %d: Lat %s Lng %s>" % (self.id, self.latitude_off, self.longitude_off)

#     @property
#     def latitude(self):
#         return self.latitude_off + self.district.latitude

#     @property
#     def longitude(self):
#         return self.longitude_off + self.district.longitude


# class District(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80))
#     latitude = db.Column(db.Float)
#     longitude = db.Column(db.Float)

#     def __init__(self, id, name, lat, lng):
#         self.id = id
#         self.name = name
#         self.latitude = lat
#         self.longitude = lng


@app.route('/')
def index():
    # districts = District.query.all()
    # return render_template('index.html', districts=districts)
    # places = Place.query.all()
    return render_template('index.html')

@app.route('/points')
def points():
    # defaults to today
    from_date = request.args.get("from_date", datetime.now())
    from_date = dp.parse(from_date)
    to_date = request.args.get("to_date", datetime.now())
    to_date = dp.parse(to_date)
    print(from_date, to_date)
    # points = Place.query.select_from(Place,Article).filter(from_date < Article.pub_date, Article.pub_date < to_date).all()
    points = Place.query.all()
    print(points)
    coords = []
    for point in points:
        pointname = "<b>" + point.word + "</b><br>"
        links = "".join([f"<a href='{a.link}' target='_blank'>{a.title[:30]}...</a><br>" for a in point.articles])
        markertext = pointname + links
        coords.append([point.lat, point.lon, markertext, point.word, links])
    return jsonify({"data": coords})

# @app.route('/district/<int:district_id>')
# def district(district_id):
#     points = Place.query.all()
#     coords = []
#     for point in points:
#         pointname = "<b>" + point.word + "</b><br>"
#         links = "".join([f"<a href='{a.link}' target='_blank'>{a.title[:30]}...</a><br>" for a in point.articles])
#         markertext = pointname + links
#         coords.append([point.lat, point.lon, markertext])
#     return jsonify({"data": coords})


# def make_random_data(db):
#     NDISTRICTS = 5
#     NPOINTS = 10
#     for did in range(NDISTRICTS):
#         district = District(did, "District %d" % did, BASECOORDS[0], BASECOORDS[1])
#         db.session.add(district)
#         for pid in range(NPOINTS):
#             lat = random.random() - 0.5
#             lng = random.random() - 0.5
#             row = Point(pid + NPOINTS * did, district, lat, lng)
#             db.session.add(row)
#     db.session.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'mkdb':
            db.create_all()
            # make_random_data(db)
    else:
        app.run(host="0.0.0.0", debug=True)
