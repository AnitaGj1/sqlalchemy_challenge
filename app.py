# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

# reflect an existing database into a new model
engine = create_engine('sqlite:///Resources/hawaii.sqlite', echo=False)

# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# (/) Start the homepage. List all the available routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
     # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
     # Perform a query to retrieve the data and precipitation scores
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()

    precipitation = []
    for date, prcp in data:
        precipitation_data = {}
        precipitation_data['date'] = date
        precipitation_data['prcp'] = prcp
        precipitation.append(precipitation_data)

    return jsonify(precipitation)

# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Design a query to calculate the total number of stations in the dataset
    total_stations = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()


    stations = []
    for station, name, latitude, longitude, elevation in total_stations:
        stations_data = {}
        stations_data['station'] = station
        stations_data['name'] = name
        stations_data['latitude'] = latitude
        stations_data['longitude'] = longitude
        stations_data['elevation'] = elevation
        stations.append(stations_data)

    return jsonify(stations)

# /api/v1.0/tobs
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def temperature():
     # Create our session (link) from Python to the DB
    session = Session(engine)
    # Using the most active station id query the last 12 months of temperature observation data for this station 
      # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_temp = session.query(Measurement.tobs, Measurement.date).filter(Measurement.station == 'USC00519281', Measurement.date >= one_year_ago).all()

    session.close()

    temperature_observation = list(np.ravel(year_temp))

    return jsonify(temperature_observation)

# Define the temperature statistics route for a specified start date
@app.route('/api/v1.0/<start>')
def temp_stats_start(start):
    # Retrieve the temperature data for all dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= dt.datetime.strptime(start, "%m-%d-%Y")).all()
    session.close()

    temp_stats_start = list(np.ravel(results))
    return jsonify(temp_stats_start)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    # Perform a query to retrieve MIN, AVG, and MAX for all dates between start and end date, inclusive
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= dt.datetime.strptime(start, "%m-%d-%Y")).filter(Measurement.date <= dt.datetime.strptime(end, "%m-%d-%Y")).all()
    session.close()

    temp_stats_start_end = list(np.ravel(results))
    return jsonify(temp_stats_start_end)

if __name__ == '__main__':
    app.run(debug=True)