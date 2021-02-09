#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from models import db, Shows, Venue, Artist
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate=Migrate(app,db)
# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=Venue.query.all()
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()
  response = {
      "count": len(venues),
      "data": []
  }
  for venue in venues:
      response["data"].append({
          'id': venue.id,
          'name': venue.name,
      })
  return render_template(
      'pages/search_venues.html',
      results=response,
      search_term=request.form.get('search_term', '')
  )

@app.route('/venues/<int:venue_id>')
def shows_venue(venue_id):

    venue = Venue.query.get(venue_id)
    if not venue:
      return render_template('errors/404.html')
    else:
      past_shows_query = db.session.query(Shows).join(Artist).filter(
          Shows.venue_id == venue_id).filter(Shows.start_time < datetime.now()).all()

      past_shows = []

      for shows in past_shows_query:
          past_shows.append({
              'artist_id': shows.artist_id,
              'artist_name': shows.artist.name,
              'artist_image_link': shows.artist.image_link,
              "start_time": shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
          })
      upcoming_shows_query = db.session.query(Shows).join(Artist).filter(
          Shows.venue_id == venue_id).filter(Shows.start_time > datetime.now()).all()

      upcoming_shows = []

      for shows in upcoming_shows_query:
          upcoming_shows.append({
              'artist_id': shows.artist_id,
              'artist_name': shows.artist.name,
              'artist_image_link': shows.artist.image_link,
              "start_time": shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
          })

      data = {
          "id": venue.id,
          "name": venue.name,
          "genres": venue.genres,
          "address": venue.address,
          "city": venue.city,
          "state": venue.state,
          "phone": venue.phone,
          "website": venue.website,
          "facebook_link": venue.facebook_link,
          "seeking_talent": venue.seeking_talent,
          "seeking_description": venue.seeking_description,
          "image_link": venue.image_link,
          "past_shows": past_shows,
          "upcoming_shows": upcoming_shows,
          "past_shows_count": len(past_shows),
          "upcoming_shows_count": len(upcoming_shows),
      }

      if not data:
          return render_template('errors/404.html')

    # add things for upcoming and past shows

    return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form=VenueForm(request.form, csrf_enabled=False)
  if form.validate():
    try:
      venue=Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data
      )
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
      print(e)
      flash('Venue ' + request.form['name'] + ' listing was unsuccessful!')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  if not venue:
    return redirect(url_for('index'))
  else:
    error_on_delete = False
    venue_name = venue.name
    try:
      db.session.delete(venue)
      db.session.commit()
    except:
      error_on_delete = True
      db.session.rollback()
    finally:
      db.session.close()
    if error_on_delete:
      flash(f'An error occurred deleting venue {venue_name}.')
      print("Error in delete_venue()")
      abort(500)
    else:
      return jsonify({'deleted': True,'url': url_for('venues')})
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
 

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()
  response = {
      "count": len(artists),
      "data": []
  }
  for artist in artists:
      response["data"].append({
          'id': artist.id,
          'name': artist.name,
      })
  return render_template(
      'pages/search_artists.html',
      results=response,
      search_term=request.form.get('search_term', '')
  )
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def shows_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
      return render_template('errors/404.html')
    else:
      past_shows_query = db.session.query(Shows).join(Venue).filter(
          Shows.artist_id == artist_id).filter(Shows.start_time < datetime.now()).all()

      past_shows = []

      for shows in past_shows_query:
          past_shows.append({
              'artist_id': shows.artist_id,
              'artist_name': shows.artist.name,
              'artist_image_link': shows.artist.image_link,
              "start_time": shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
          })
      upcoming_shows_query = db.session.query(Shows).join(Artist).filter(
          Shows.artist_id == artist_id).filter(Shows.start_time > datetime.now()).all()

      upcoming_shows = []

      for shows in upcoming_shows_query:
          upcoming_shows.append({
              'artist_id': shows.artist_id,
              'artist_name': shows.artist.name,
              'artist_image_link': shows.artist.image_link,
              "start_time": shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
          })

      data = {
          "id": artist.id,
          "name": artist.name,
          "genres": artist.genres,
          "city": artist.city,
          "state": artist.state,
          "phone": artist.phone,
          "website": artist.website,
          "facebook_link": artist.facebook_link,
          "seeking_venue": artist.seeking_venue,
          "seeking_description": artist.seeking_description,
          "image_link": artist.image_link,
          "past_shows": past_shows,
          "upcoming_shows": upcoming_shows,
          "past_shows_count": len(past_shows),
          "upcoming_shows_count": len(upcoming_shows),
      }

      if not data:
          return render_template('errors/404.html')

    return render_template('pages/show_artist.html', artist=data)#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    #form.image_link.data = artist.image_link
    #form.website.data = artist.website
    #form.seeking_venue.data = artist.seeking_venue
    #form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False  
  artist = Artist.query.get(artist_id)

  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    #artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    #artist.website = request.form['website']
    #artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    #artist.seeking_description = request.form['seeking_description']

    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Artist could not be changed.')
  if not error: 
    flash('Artist was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    #form.image_link.data = venue.image_link
    #form.website.data = venue.website
    #form.seeking_talent.data = venue.seeking_talent
    #form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False  
  venue = Venue.query.get(venue_id)

  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    #venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    #venue.website = request.form['website']
    #venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    #venue.seeking_description = request.form['seeking_description']

    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash(f'An error occurred. Venue could not be changed.')
  if not error: 
    flash(f'Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

      
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form=ArtistForm(request.form, csrf_enabled=False)
  if form.validate():
    try:
      artist=Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data
      )
      form.populate_obj(artist)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
      print(e)
      flash('Artist ' + request.form['name'] + ' listing was unsuccessful!')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  shows=Shows.query.all()
  for show in shows:
    data.append({
              "venue_id": show.venue.id,
              "venue_name": show.venue.name,
              "artist_id": show.artist.id,
              "artist_name": show.artist.name,
              "artist_image_link": show.artist.image_link,
              "start_time": format_datetime(str(show.start_time))
          })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form=ShowForm(request.form, csrf_enabled=False)
  if form.validate():
    try:
      show=Shows()
      form.populate_obj(show)
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
    except ValueError as e:
      print(e)
      flash('Show listing was unsuccessful!')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
