from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Shows(db.Model):
  __tablename__='Shows'

  id=db.Column(db.Integer, primary_key=True)
  start_time=db.Column(db.DateTime)
  venue_id=db.Column(db.Integer, db.ForeignKey('Venue.id'))
  artist_id=db.Column(db.Integer, db.ForeignKey('Artist.id'))
  venue=db.relationship('Venue',backref='shows_venue',lazy=True)
  artist=db.relationship('Artist',backref='shows_artist',lazy=True)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    
    shows = db.relationship('Shows', backref='Venue', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Shows', backref='Artist', lazy=True)    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
