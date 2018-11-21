import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite?check_same_thread=False")
#conn = sqlite3.connect('sqlite://hawaii.sqlite', check_same_thread=False)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
#session = scoped_session(sessionmaker(bind=engine))

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/names<br/>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/date/<start_date/"
        f"/api/v1.0/date/<start_date/<end_date></br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of date_prcp
    date_prcp = []
    for measurement in results:
        date_prcp_dict = {}
        date_prcp_dict["date"] = measurement.date
        date_prcp_dict["prcp"] = measurement.prcp
        date_prcp.append(date_prcp_dict)

    return jsonify(date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #query for the dates and temperature observations from a year from the last data point.
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    results = session.query(Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs)\
        .filter(Measurement.date > '2016-08-23').all()

    # Create a dictionary from the row data and append to a list of tobs
    all_tobs = []
    for measurement in results:
        measurement_dict = {}
        measurement_dict["station"] = measurement.station
        measurement_dict["date"] = measurement.date
        measurement_dict["prcp"] = measurement.prcp
        measurement_dict["tobs"] = measurement.tobs
        all_tobs.append(measurement_dict)

    return jsonify(all_tobs)
@app.route("/api/v1.0/date/<start_date>")
@app.route("/api/v1.0/date/<start_date>/<end_date>")
def calc_temps(start_date, end_date='2017-08-23'):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for
    # a given start or start-end range.
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between 
    # the start and end date inclusive.
    #start_date = request.args.get('start_date', None)
    #end_date = request.args.get('start_date', 'end_date')
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
        func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date)\
        .filter(Measurement.date <= end_date).all()

    # Create a dictionary from the row data and append to a list of tobs
    all_starts_ends = []
    measurement_dict = {}
    measurement_dict["TMIN"] = results[0][0]
    measurement_dict["TAVG"] = results[0][1]
    measurement_dict["TMAX"] = results[0][2]
    all_starts_ends.append(measurement_dict)

    return jsonify(all_starts_ends)

if __name__ == '__main__':
    app.run(debug=True)
