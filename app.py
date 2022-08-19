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
import sys
from models import *


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
  data = []

  all_locations = db.session.query((Venue.city), Venue.state).all()

  today = datetime.now()

  for location in all_locations:
      city = location[0]
      state = location[1]

      venues = Venue.query.filter_by(city=city, state=state).all()
      
      venue_location = {"city": city, "state": state, "venues": []}          

      for venue in venues:
          venue_name = venue.name
          venue_id = venue.id

          upcoming_shows = (
              Show.query.filter_by(venue_id=venue_id)
              .filter(Show.start_time > today)
              .all()
          )

          venue_data = {
              "id": venue_id,
              "name": venue_name,
              "num_upcoming_shows": len(upcoming_shows),
          }

          venue_location["venues"].append(venue_data)

      data.append(venue_location)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_word = request.form.get('search_term', None)
    searched_venue = Venue.query.filter(Venue.name.ilike(f'%{search_word}%'))

    data = []
    for venue in searched_venue.all():

        data.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': Show.query
            .filter(Show.venue_id == venue.id)
            .filter(Show.start_time > datetime.now())
            .count()
        })
        print(data)

    response = {
        "count": searched_venue.count(),
        "data": data
    }
  
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
        data = {}

        single_venue = Venue.query.get(venue_id)

        shows = Show.query.filter_by(venue_id=venue_id)

        today = datetime.now()
        
        past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
        past_shows = []
        
        all_past_shows = shows.filter(Show.start_time < today).all()
        past_shows = []
        for show in all_past_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            past_shows.append(show_data)

        all_upcoming_shows = shows.filter(Show.start_time >= today).all()
        upcoming_shows = []
        for show in all_upcoming_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            upcoming_shows.append(show_data)

        data = {
            "id": single_venue.id,
            "name": single_venue.name,
            "genres": single_venue.genres.split(","),
            "address": single_venue.address,
            "city": single_venue.city,
            "state": single_venue.state,
            "phone": single_venue.phone,
            "website": single_venue.website_link,
            "facebook_link": single_venue.facebook_link,
            "seeking_talent": single_venue.seeking_talent,
            "image_link": single_venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

  except:
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")

  finally:
        db.session.close()

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
  try:    
        new_venue = Venue(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          address=form.address.data,
          phone=form.phone.data,
          image_link=form.image_link.data,
          facebook_link=form.facebook_link.data,
          genres=", ".join(form.genres.data),
          website_link=form.website_link.data,
          seeking_talent=form.seeking_talent.data,
          seeking_description=form.seeking_description.data,
        )
        db.session.add(new_venue)
        db.session.commit()
      # TODO: modify data to be the data object returned from db insertion
      # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')  
  except:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
        db.session.rollback()
      
  finally:
        db.session.close() 
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
  artist = Artist.query.all()
  return render_template('pages/artists.html', artists=artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
    search_word = request.form.get('search_term', None)

    searched_artist = Artist.query.filter(Artist.name.ilike(f'%{search_word}%'))

    data = []
    for result in searched_artist.all():

        data.append({
            'id': result.id,
            'name': result.name,
            'num_upcoming_shows': Show.query
            .filter(Show.artist_id == result.id)
            .filter(Show.start_time > datetime.now())
            .count()
        })
        print(data)

    response = {
        "count": searched_artist.count(),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    try:
        data = {}

        single_artist = Artist.query.get(artist_id)
        
        shows = Show.query.filter_by(artist_id=artist_id)

        today = datetime.now()

        all_past_shows = shows.filter(Show.start_time < today).all()
        past_shows = []
        for show in all_past_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            past_shows.append(show_data)

        all_upcoming_shows = shows.filter(Show.start_time >= today).all()
        upcoming_shows = []
        for show in all_upcoming_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            upcoming_shows.append(show_data)

      
        data = {
            "id": single_artist.id,
            "name": single_artist.name,
            "genres": single_artist.genres.split(","),
            "city": single_artist.city,
            "state": single_artist.state,
            "phone": single_artist.phone,
            "website": single_artist.website_link,
            "facebook_link": single_artist.facebook_link,
            "seeking_venue": single_artist.seeking_venue,
            "seeking_description": single_artist.seeking_description,
            "image_link": single_artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }
    except:
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")

    finally:
        db.session.close()
       
        return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)  # auto pre populate field

    # TODO: populate form with fields from artist with ID <artist_id>

    form.genres.data = artist.genres.split(", ") 
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm()
        artist = Artist.query.get(artist_id)

        artist.name = form.name.data
        artist.genres = ", ".join(form.genres.data)
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website_link = form.website_link.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data

        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))
 

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  
  form.genres.data = venue.genres.split(",")
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        
        
        venue.name = form.name.data
        venue.address = form.address.data
        venue.genres = ", ".join(form.genres.data)
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website_link = form.website_link.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_venue = form.seeking_venue.data
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data

        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

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
  form = ArtistForm(request.form)
  try:    
      new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        genres=", ".join(form.genres.data),
        website_link=form.website_link.data,
        seeking_venue =form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
      )
      db.session.add(new_artist)
      db.session.commit()
      # TODO: modify data to be the data object returned from db insertion
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!') 
  except:
        # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
      db.session.rollback()
      
  finally:
      db.session.close() 
      return render_template('pages/home.html')
  # on successful db insert, flash success

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  
  shows = Show.query.all()
  venue = db.session.query(Venue)
  artist = db.session.query(Artist)
  
  for show in shows:
    all_show = {
       "venue_id": show.venue_id,
        "venue_name": venue.get(show.venue_id).name,
        "artist_id": show.artist_id,
        "artist_name": artist.get(show.artist_id).name,
        "artist_image_link": artist.get(show.artist_id).image_link,
        "start_time": f'{show.start_time}'
    }
    data.append(all_show)
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
  try:
    new_show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(new_show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    # print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close() 
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
