from tkinter import CENTER
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

#create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect the tables
base = automap_base()
base.prepare(engine, reflect=True)

#save references to each table
measurement = base.classes.measurement
station = base.classes.station

#create our session (link) from Python to DB
session = Session(engine)

@app.route("/")
def home():
    return(
        f"<Center><h2> Welocome to Hawaii Climate Analysis Local API</h2></center>"
        f"<center><h3>Select from available routes below:</h3></center>"
        f"<center>/api/v1.0/precipitaion</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
        )

#/api/v1.0/precipitaion route
@app.route("/api/v1.0/precipitaion")
def precipitaion():
    #return prev years precipitaion as a json
    #calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #perform a query to retrieve the data
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= previousYear).all()

    session.close()
    #dictionary with date as the key and precipitaion as the value
    precipitaion ={date: prcp for date, prcp in results}
    #convert to jsonation
    return jsonify(precipitaion)

    #/api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    session.close()

    stationList = list(np.ravel(results))
    return jsonify(stationList)

#/api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def temperatures():

    #return previous year's temps
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #query to get the temperatures from most active station for the last year
    results = session.query(measurement.tobs).\
    filter(measurement.station =='USC00519281').\
    filter(measurement.date >= previousYear).all()  

    session.close()

    tempList = list(np.ravel(results))
    return jsonify(tempList)

#/api/v1.0/start/end, /api/v1.0/start routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):

    selection = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]

    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(measurement.date >= startDate).all()

        session.close()

        tempList = list(np.ravel(results))
        return jsonify(tempList)

    else:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*selection)\
            .filter(measurement.date >= startDate)\
            .filter(measurement.date <= endDate).all()

        session.close()

        tempList = list(np.ravel(results))
        return jsonify(tempList)

if __name__=="__main__":
    app.run(debug=True)