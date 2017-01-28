from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

import geocoder
import urllib2
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__= 'users'
    uid = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(88))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique = True)
    pwdhash = db.Column(db.String(54))

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email.lower()
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

class LocationPoint(object):
    def distance_meters(self, meters):
        #80m = 1 min walk
        return int(meters/80)

    def wiki(self, slug):
        return urllib2.urlparse.urljoin("http://en.wikipedia.org/wiki/",
                slug.replace(" ", '-'))

    def loc_lat_long(self, loc):
        location = geocoder.google(loc)
        return (location.lat, location.lng)

    def query(self, loc):
        lat, lng = self.loc_lat_long(loc)
        print lat, lng

        URL = 'https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gsradius=5000&gscoord={0}%7C{1}&gslimit=20&format=json'.format(lat, lng)
        x = urllib2.urlopen(URL)
        results = x.read()
        x.close()

        data = json.loads(results)
        print data

        places = []
        for place in data['query']['geosearch']:
            name = place['title']
            meters = place['dist']
            lat = place['lat']
            lng = place['lon']

            wiki_url = self.wiki(name)
            walk_time = self.distance_meters(meters)

            d_obj = {
                'name': name,
                'url': wiki_url,
                'time': walk_time,
                'lat': lat,
                'lng': lng

            }

            places.append(d_obj)

        return places
