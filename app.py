import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the Climate App<br/>"
        f"Available routes are: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/input start date Format: yyyy-m-dd <br/>"
        f"/api/v1.0/input start date/input end date Format: yyyy-m-dd"
        )

@app.route("/api/v1.0/precipitation")
def prcp():

    start_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    end_date = dt.date(2017,8,23)

# Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date <= end_date , Measurement.date >= start_date).all()
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)
    session.close()

    return jsonify(prcp_list= prcp_list)

@app.route("/api/v1.0/stations")
def station():
    stat = session.query(Station.station).all()

    session.close()

    return jsonify(stat=stat)

@app.route("/api/v1.0/tobs")
def tobs():
    sel = [Measurement.station, func.count(Measurement.station)]
    count = session.query(*sel).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station = count[0][0]

    start_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    end_date = dt.date(2017,8,23)

    result = session.query(Measurement.tobs).\
            filter(Measurement.station == most_active_station).\
            filter(Measurement.date <= end_date , Measurement.date >= start_date).all()
    temp = list(np.ravel(result))

    session.close()

    return jsonify(temp = temp)

@app.route("/api/v1.0/<start>")
def startdate(start):
    start_date = start

    sel = [func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]

    temperatures = session.query(*sel).filter(Measurement.date >= start_date).all()
    temp = list(np.ravel(temperatures))
    session.close()

    return jsonify(temp=temp)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    start_date = start
    end_date = end

    sel = [func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]

    temperatures = session.query(*sel).filter(Measurement.date <= end_date , Measurement.date >= start_date).all()
    temp = list(np.ravel(temperatures))

    session.close()

    return jsonify(temp=temp)


if __name__ == "__main__":
    app.run(debug=True)
