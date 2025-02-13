# Import the dependencies.
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base=automap_base()

Base.prepare(autoload_with=engine)

station = Base.classes.station
measurement = Base.classes.measurement

session = Session(engine)

#################################################
# Flask Setup
#################################################

app=Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year = dt.date(2017,8,23)-dt.timedelta(days = 365)
    retrieve = session.query(measurement.date, measurement.prcp).filter(measurement.date>=one_year).all()
    session.close()
    precip = {date: prcp for date, prcp in retrieve}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    results=session.query(station.station).all()
    session.close()
    stations=list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    previous_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    results=session.query(measurement.tobs).filter(measurement.station=='USC00519281').filter(measurement.date>=previous_year).all()
    session.close()
    tobs=list(np.ravel(results))
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None,end=None):
    value=[func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)]
    if not end:
        start=dt.datetime.strptime(start,"%m%d%Y")
        results=session.query(*value).filter(measurement.date>=start).all()
        session.close()
        temps=list(np.ravel(results))
        return jsonify(temps)
    start=dt.datetime.strptime(start,"%m%d%Y")
    end=dt.datetime.strftime(end,"%m%d%Y")
    results = session.query(*value).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()