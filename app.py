#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import os
import dateutil.parser
import babel
import logging
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from forms import *
from flask_migrate import Migrate
from flask import jsonify
from model import db, Venue, Artist, Show
import sys
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
logger = logging.getLogger(__name__)

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
  show_venue = Venue.query.get_or_404(venue_id)

  past_shows = []
  upcoming_shows = []
  for show in show_venue:
    tmp_show = {
      "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    if show.start_time >= datetime.now():
      upcoming_shows.append(tmp_show)
    else:
      past_shows.append(tmp_show)
    
  data = vars(show_venue)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
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
  if form.validate():
    venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data, phone=form.phone.data, genres=form.genres.data, facebook_link=form.facebook_link.data, image_link=form.image_link.data, website=form.website_link.data, seeking_talent=form.seeking_talent.data, seeking_description=form.seeking_description.data)
    try:
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        db.session.rollback() 
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
        return render_template('pages/home.html')
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
    flash('An error occurred. Venue ' + form.name.data + ' , '.join(message))
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)
  
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
  artist_found = Artist.query.get_or_404(artist_id)
  past_vernues = []
  upcoming_vernues = []
  for venue in artist_found:
    tmp_venue = {
      "venue_id": venue.venue_id,
      "venue_name": venue.venue_name,
      "venue_image_link": venue.venue_image_link,
      "start_time": venue.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    if venue.start_time >= datetime.now():
      upcoming_vernues.append(tmp_venue)
    else:
      past_vernues.append(tmp_venue)
  
  data =vars(artist_found)
  data['past_shows'] = past_vernues
  data['upcoming_shows'] = upcoming_vernues
  data['past_shows_count'] = len(past_vernues)
  data['upcoming_shows_count'] = len(upcoming_vernues)
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
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
        artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data, genres=form.genres.data, facebook_link=form.facebook_link.data, image_link=form.image_link.data, website=form.website.data, seeking_venue=form.seeking_venue.data, seeking_description=form.seeking_description.data)
  
        db.session.add(artist)
        db.session.commit()
    except:
     # TODO: on unsuccessful db insert, flash an error instead.
        db.session.rollback()
    finally:
      db.session.close()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed. ' + ', '.join(message))
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # query show according to Show, Artist, Venue and join Artist and Venue filter by show time larger than current time
  shows = db.session.query(Show, Artist, Venue).join(Artist).join(Venue).filter(Show.start_time > datetime.now()).all()
  data = []
  for show in shows:
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
  form = ShowForm(request.form, meta={'csrf': False})
  if form.validate():
    show = Show(venue_id=form.venue_id.data, artist_id=form.artist_id.data, start_time=form.start_time.data)
    try:
        db.session.add(show)
        db.session.commit()
    except:
      db.session.rollback()
    finally:
      flash('Show was successfully listed!')
      db.session.close()
      return render_template('pages/home.html')
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
    flash('An error occurred. Show could not be listed. ' + ', '.join(message))
    form = ShowForm()
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


