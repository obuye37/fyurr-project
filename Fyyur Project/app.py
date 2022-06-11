#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from dataclasses import fields
import json
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
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
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI '] ='postgresql://postgres@localhost:5432/fyyurapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#//////////////////////////////////////
#   Venue Table
#/////////////////////////////////////
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    genres = db.Column(db.PickleType(), default=[])
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


#//////////////////////////////////////
#   Artist Table
#/////////////////////////////////////
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.PickleType(), default=[])
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

#//////////////////////////////////////
#   Show Table
#/////////////////////////////////////

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False,)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_date = db.Column(db.DateTime, nullable=False)

# db.create_all();
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  #importing Table data
  real_data = db.session.query(Venue)

  #String Declaration
  rdata=[]
  venues=[]

  #Loop for venues population
  for v in real_data :
    venue = {
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": 0
      } 
    venues.append(venue)

#Venue Listing
  for x in real_data:
    data = {
    "city": x.city,
    "state": x.state,
    "venues": venues
  }
    rdata.append(data)

  return render_template('pages/venues.html', areas=rdata);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venue_data = db.session.query(Venue)
  search_result = request.form.get('value')
  
  query_result = venue_data.all()
  up_coming=venue_data.join(Venue).filter(Show.start_date > datetime.today())

  count = venue_data.count()
  fields = []
  up_count = 0

  for each in query_result:
    data = {
      "id": each.id,
      "name": each.name,
      "num_upcoming_shows":up_count,
    }
    fields.append(data)
    
  response={
    "count": count,
    "data": fields
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

#required db setup
  db_data = Venue.query.get(venue_id)
  shows_data = db.session.query(Show)

  # Declarations
  geners = []
  pastshows = []
  upcomingshows = []
  up_count = 0
  past_count = 0

  for ind in db_data.genres :
    geners.append(ind)

  join_data = shows_data.join(Venue).filter(Show.start_date > datetime.today())
  for each in join_data :
    upcoming = {
      "artist_id": each.artist_id,
      "artist_name": each.Artist.name,
      "artist_image_link": each.Artist.image_link,
      "start_time": each.start_date.strftime("%Y/%m/%d, %H:%M:%S")
    }
    up_count = up_count + 1
    upcomingshows.append(upcoming)

  join_data2 = shows_data.join(Venue).filter(Show.start_date < datetime.today())
  for each in join_data2 :
    past = {
      "artist_id": each.artist_id,
      "artist_name": each.Artist.name,
      "artist_image_link": each.Artist.image_link,
      "start_time": each.start_date.strftime("%Y/%m/%d, %H:%M:%S")
    }
    past_count = past_count + 1
    pastshows.append(past)

  selected={
    "id":db_data.id,
    "name": db_data.name,
    "genres": geners,
    "address": db_data.address,
    "city": db_data.city,
    "state": db_data.state,
    "phone": db_data.phone,
    "website": db_data.website_link,
    "facebook_link": db_data.facebook_link,
    "seeking_talent": True,
    "seeking_description": db_data.seeking_description,
    "image_link": db_data.image_link,
    "past_shows": pastshows,
    "upcoming_shows": upcomingshows,
    "past_shows_count": past_count,
    "upcoming_shows_count": up_count,
  }
  
  
  data = list(filter(lambda d: d['id'] == venue_id, [selected]))[venue_id -1]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  form_name = request.form.get('name')
  form_city = request.form.get('city')
  form_state = request.form.get('state')
  form_address = request.form.get('address')
  form_phone = request.form.get('phone')
  form_genres = request.form.get('genres')
  form_facebook = request.form.get('facebook_link')
  form_image = request.form.get('image_link')
  form_website = request.form.get('website_link')
  form_talent  = request.form.get('seeking_talent')
  form_description = request.form.get('seeking_description')

  try:
    dbAttributes = Venue(
      name = form_name,
      city = form_city,
      state = form_state,
      address = form_address,
      phone = form_phone,
      genres = form_genres,
      facebook_link = form_facebook,
      image_link = form_image,
      website_link = form_website,
      seeking_talent = form_talent,
      seeking_description = form_description
      )
    db.session.add(dbAttributes)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except: 
    db.session.rollback()
    flash('Venue ' + request.form['name'] + ' listen was unsuccessful!')
  finally:
    db.session.close()

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artist_data = db.session.query(Artist)
  search_result = request.form.get('value')
  
  query_result = artist_data.all()
  up_coming=artist_data.join(Artist).filter(Show.start_date > datetime.today())

  count = artist_data.count()
  fields = []
  up_count = 0

  for each in query_result:
    data = {
      "id": each.id,
      "name": each.name,
      "num_upcoming_shows":up_count,
    }
    fields.append(data)
    
  response={
    "count": count,
    "data": fields
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  # setting up required tables
  db_data = Artist.query.get(artist_id)
  shows_data = db.session.query(Show)

  # Declarations
  geners = []
  pastshows = []
  upcomingshows = []
  up_count = 0
  past_count = 0
  
  for ind in db_data.genres :
    geners.append(ind)

  join_data = shows_data.join(Venue).filter(Show.start_date > datetime.today())
  for each in join_data :
    upcoming = {
      "venue_id": each.venue_id,
      "venue_name": each.Venue.name,
      "venue_image_link": each.Venue.image_link,
      "start_time": each.start_date.strftime("%Y/%m/%d, %H:%M:%S")
    }
    up_count = up_count + 1
    upcomingshows.append(upcoming)

  join_data2 = shows_data.join(Venue).filter(Show.start_date < datetime.today())
  for each in join_data2 :
    past = {
      "venue_id": each.venue_id,
      "venue_name": each.Venue.name,
      "venue_image_link": each.Venue.image_link,
      "start_time": each.start_date.strftime("%Y/%m/%d, %H:%M:%S")
    }
    past_count = past_count + 1
    pastshows.append(past)

  selected={
    "id": db_data.id,
    "name": db_data.name,
    "genres": geners,
    "city": db_data.city,
    "state": db_data.state,
    "phone": db_data.phone,
    "website": db_data.website_link,
    "facebook_link": db_data.facebook_link,
    "seeking_venue": db_data.seeking_venues,
    "seeking_description": db_data.seeking_description,
    "image_link": db_data.image_link,
    "past_shows": pastshows,
    "upcoming_shows": upcomingshows,
    "past_shows_count": past_count ,
    "upcoming_shows_count": up_count ,
  }
  
  data = list(filter(lambda d: d['id'] == artist_id, [selected]))[artist_id-1]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_data = Artist.query.get(artist_id)
  
  form.name.data = artist_data.name
  form.genres.data = artist_data.genres
  form.city.data = artist_data.city
  form.state.data = artist_data.state
  form.phone.data = artist_data.phone
  form.website_link.data = artist_data.website_link
  form.facebook_link.data = artist_data.facebook_link
  form.seeking_venue.data = artist_data.seeking_venues
  form.seeking_description.data = artist_data.seeking_description
  form.image_link.data = artist_data.image_link

  artist={
    "id": artist_data.id,
    "name": form.name,
    "genres": form.genres,
    "city": form.city,
    "state": form.state,
    "phone": form.phone,
    "website": form.website_link,
    "facebook_link": form.facebook_link,
    "seeking_venue": form.seeking_venue,
    "seeking_description": form.seeking_description,
    "image_link": form.image_link
  }
  

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  db_data = Artist.query.get(artist_id)

  form_name = request.form.get('name')
  form_city = request.form.get('city')
  form_state = request.form.get('state')
  form_phone = request.form.get('phone')
  form_genres = request.form.get('genres')
  form_facebook = request.form.get('facebook_link')
  form_image = request.form.get('image_link')
  form_website = request.form.get('website_link')
  form_venues  = request.form.get('seeking_venue')
  form_description = request.form.get('seeking_description')

  try:    
    db_data.name = form_name
    db_data.city = form_city
    db_data.state = form_state
    db_data.phone = form_phone
    db_data.generes = form_genres
    db_data.facebook_link = form_facebook
    db_data.image_link = form_image
    db_data.website_link = form_website
    db_data.seeking_venues = form_venues
    db_data.seeking_description = form_description
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except: 
    db.session.rollback()
    flash('Artist ' + request.form['name'] + 'updating was unsuccessfull!')
  finally:
    db.session.close()

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_data = Venue.query.get(venue_id)

  form.name.data = venue_data.name
  form.genres.data = venue_data.genres
  form.address.data = venue_data.address
  form.city.data = venue_data.city
  form.state.data = venue_data.state
  form.phone.data = venue_data.phone
  form.website_link.data = venue_data.website_link
  form.facebook_link.data = venue_data.facebook_link
  form.seeking_talent.data = venue_data.seeking_talent
  form.seeking_description.data = venue_data.seeking_description
  form.image_link.data = venue_data.image_link

  venue={
    "id": venue_data.id,
    "name": form.name,
    "genres": form.genres,
    "city": form.city,
    "state": form.state,
    "phone": form.phone,
    "website": form.website_link,
    "facebook_link": form.facebook_link,
    "seeking_talent": form.seeking_talent,
    "seeking_description": form.seeking_description,
    "image_link": form.image_link
  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  db_data = Venue.query.get(venue_id)

  form_name = request.form.get('name')
  form_city = request.form.get('city')
  form_state = request.form.get('state')
  form_address = request.form.get('address')
  form_phone = request.form.get('phone')
  form_genres = request.form.get('genres')
  form_facebook = request.form.get('facebook_link')
  form_image = request.form.get('image_link')
  form_website = request.form.get('website_link')
  form_talent  = request.form.get('seeking_talent')
  form_description = request.form.get('seeking_description')

  try: 
    db_data.name = form_name
    db_data.city = form_city
    db_data.state = form_state
    db_data.address = form_address
    db_data.phone = form_phone
    db_data.genres = form_genres
    db_data.facebook_link = form_facebook
    db_data.image_link = form_image
    db_data.website_link = form_website
    db_data.seeking_talent = form_talent
    db_data.seeking_description = form_description
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except: 
    db.session.rollback()
    flash('Venue ' + request.form['name'] + ' listen was unsuccessful!')
  finally:
    db.session.close()


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
   # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  
  form_name = request.form.get('name')
  form_city = request.form.get('city')
  form_state = request.form.get('state')
  form_phone = request.form.get('phone')
  form_genres = request.form.get('genres')
  form_facebook = request.form.get('facebook_link')
  form_image = request.form.get('image_link')
  form_website = request.form.get('website_link')
  form_venues  = request.form.get('seeking_venue')
  form_description = request.form.get('seeking_description')

  try:    
    dbAttributes = Artist(
      name = form_name,
      city = form_city,
      state = form_state,
      phone = form_phone,
      genres = form_genres,
      facebook_link = form_facebook,
      image_link = form_image,
      website_link = form_website,
      seeking_venues = form_venues,
      seeking_description = form_description
      )
    db.session.add(dbAttributes)

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except: 
    db.session.rollback()
    flash('Artist ' + request.form['name'] + 'Listen was unsuccessfull!')
  finally:
    db.session.close()

  # on successful db insert, flash success
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  rdata = []
  sd = db.session.query(Show).join(Venue).join(Artist).filter(Show.venue_id == Venue.id and Show.artist_id == Artist.id)
  for each in sd :
    data = {
      "venue_id": each.venue_id,
      "venue_name": each.Venue.name,
      "artist_id": each.artist_id,
      "artist_name": each.Artist.name,
      "artist_image_link": each.Artist.image_link,
      "start_time": each.start_date.strftime("%Y/%m/%d, %H:%M:%S")
    }
    rdata.append(data)
  return render_template('pages/shows.html', shows=rdata)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

  #   Creating Post
  #   ----------------------------------------------------------

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form_artist_id = request.form.get('artist_id')
  form_venue_id  = request.form.get('venue_id')
  form_start_date = request.form.get('start_time')

  try:    
    dbAttributes = Show(
      artist_id = form_artist_id,
      venue_id = form_venue_id,
      start_date = form_start_date
      )
    db.session.add(dbAttributes)
    db.session.commit()
    flash('Show was successfully listed!')
  except: 
    db.session.rollback()
    flash('Show Listen was unsuccessfull!')
  finally:
    db.session.close()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


# Search Show
# ---------------------------------------------------------------------------

@app.route('/show/search', methods=['POST'])
def search_shows():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  show_data = db.session.query(Show)
  search_result = request.form.get('value')
  
  search=show_data.join(Venue).join(Artist).filter(Show.artist_id == Artist.id and Show.venue_id==Venue.id)

  count = show_data.count()
  fields = []
  up_count = 0

  for each in search:
    data = {
      "venue_id": each.Venue.id,
      "artist_id": each.Artist.id,
      "venue_name": each.Venue.name,
      "artist_name": each.Artist.name,
      "num_upcoming_shows":up_count,
    }
    fields.append(data)
    
  response={
    "count": count,
    "data": fields
  }
  return render_template('pages/search_shows.html', results=response, search_term=request.form.get('search_term', ''))
  

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
