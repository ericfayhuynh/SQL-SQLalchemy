# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask
#################################################
app = Flask(__name__)

@app.route('/')
def home():
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    stations_list = [station[0] for station in results]
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    most_active_station = 'USC00519281'
    most_recent_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    tobs_data = session.query(Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()
    session.close()
    tobs_list = [tobs[0] for tobs in tobs_data]
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def start_date(start):
    return temperature_data(start, None)

@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end):
    return temperature_data(start, end)


def temperature_data(start, end):
    session = Session(engine)
    if end:
        temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
    else:
        temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    return jsonify({"TMIN": temps[0][0], "TAVG": temps[0][1], "TMAX": temps[0][2]})

if __name__ == '__main__':
    app.run(debug=True)
