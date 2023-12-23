#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from flask import jsonify
from model import db, Venue, Artist, Show
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  data = []
  for venue in venues:
    data.append({
      "city": venue.city,
      "state": venue.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 0,
      }]
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_item = request.form.get('search_term', '')
  search = "%{}%".format(search_item)
  venues = Venue.query.filter(Venue.name.ilike(search)).all()
  formatted_venues = []
  for venue in venues:
    formatted_venues.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": 0,
    })
  response={ 
    "count": len(venues),
    "data": formatted_venues
  }
  return render_template('pages/search_venues.html', results=response, search_term= search_item)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  show_venue = Venue.query.get(venue_id)
  data = {
     
    "id": show_venue.id,
    "name": show_venue.name,
    "genres": show_venue.genres,
    "address": show_venue.address,
    "city": show_venue.city,
    "state": show_venue.state,
    "phone": show_venue.phone,
    "website": show_venue.website,
    "facebook_link": show_venue.facebook_link,
    "seeking_talent": show_venue.seeking_talent,
    "seeking_description": show_venue.seeking_description,
    "image_link": show_venue.image_link,
    "past_shows": [{
      "artist_id": show_venue.id,
      "artist_name": show_venue.name,
      "artist_image_link": show_venue.image_link,
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": show_venue.id,
      "artist_name": show_venue.name,
      "artist_image_link": show_venue.image_link,
      "start_time": "2035-04-01T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  venue = Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'], phone=request.form['phone'], genres=request.form['genres'], facebook_link=request.form['facebook_link'], image_link=request.form['image_link'], website=request.form['website'], seeking_talent=request.form['seeking_talent'], seeking_description=request.form['seeking_description'])
  try:
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      db.session.close()
  except:
      # TODO: on unsuccessful db insert, flash an error instead.
      db.session.rollback() 
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.close()
      print(sys.exc_info())
  finally:
      db.session.close()
      return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  venue = Venue.query.get(venue_id)
  if venue:
    try:
       
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully deleted!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
    finally:
      db.session.close()
      return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/artists.html', artists=data)
  
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_artists = request.form.get('search_term', '')
  search = "%{}%".format(search_artists)
  artists = Artist.query.filter(Artist.name.ilike(search)).all()
  formatted_artists = []
  for artist in artists:
    formatted_artists.append({
      "id": artist.id,
      "name": artist.name,
    })

  response={
    "count": len(artists),
    "data": formatted_artists
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=search_artists)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_found = Artist.query.get(artist_id)
  if not artist_found:
    return render_template('errors/404.html')
  
  data = {
    "id": artist_found.id,
    "name": artist_found.name,
    "genres": artist_found.genres,
    "city": artist_found.city,
    "state": artist_found.state,
    "phone": artist_found.phone,
    "website": artist_found.website,
    "facebook_link": artist_found.facebook_link,
    "seeking_venue": artist_found.seeking_venue,
    "seeking_description": artist_found.seeking_description,
    "image_link": artist_found.image_link,
    "past_shows": [{
      "venue_id": artist_found.id,
      "venue_name": artist_found.name,
      "venue_image_link": artist_found.image_link,
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [{
      "venue_id": artist_found.id,
      "venue_name": artist_found.name,
      "venue_image_link": artist_found.image_link,
      "start_time": "2035-04-01T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  artist_found = Artist.query.get(artist_id)
  if not artist_found:
    return render_template('errors/404.html')
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.genres = request.form['genres']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.website = request.form['website']
  artist.seeking_venue = request.form['seeking_venue']
  artist.seeking_description = request.form['seeking_description']
  artist.image_link = request.form['image_link']
  db.session.commit()
  flash('Artist ' + request.form['name'] + ' was successfully updated!')
  db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm()
  venue_found = Venue.query.get(venue_id)

  # check if venue exists
  if not venue_found:
    return render_template('errors/404.html')
  
  venue={
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
    "image_link": venue.image_link
  }
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
      
      venue = Venue.query.get(venue_id)
      # check if venue exists
      if not venue:
        return render_template('errors/404.html')

      venue.name = request.form['name']
      venue.genres = request.form['genres']
      venue.address = request.form['address']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.phone = request.form['phone']
      venue.facebook_link = request.form['facebook_link']
      venue.website = request.form['website']
      venue.seeking_talent = request.form['seeking_talent']
      venue.seeking_description = request.form['seeking_description']
      venue.image_link = request.form['image_link']
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  artist = Artist(name=request.form['name'], city=request.form['city'], state=request.form['state'], phone=request.form['phone'], genres=request.form['genres'], facebook_link=request.form['facebook_link'], image_link=request.form['image_link'], website=request.form['website'], seeking_venue=request.form['seeking_venue'], seeking_description=request.form['seeking_description'])
  try:
      db.session.add(artist)
      db.session.commit()
       # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      db.session.close()
  except:
     # TODO: on unsuccessful db insert, flash an error instead.
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.close()
      print(sys.exc_info())
  finally:
      db.session.close()
      return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  show = Show.query.all()
  data = []
  for show in show:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue_name,
      "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": show.start_time,
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  show = Show(venue_id=request.form['venue_id'], artist_id=request.form['artist_id'], start_time=request.form['start_time'])
  try:
      db.session.add(show)
      db.session.commit()
      db.session.close()
       # on successful db insert, flash success
      flash('Show was successfully listed!')
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()
 
  return render_template('forms/new_show.html', form=form)

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
