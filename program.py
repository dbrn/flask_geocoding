import pandas as pd
from flask import Flask, render_template, request, Markup
from geopy.geocoders import arcgis
from pandas.errors import ParserError
from os import remove

app = Flask(__name__)


def create_table(pandasobj):
    coordinates = []
    latitude = []
    longitude = []
    gis = arcgis.ArcGIS()
    pandasobj = pandasobj.rename(str.lower, axis="columns")
    for address in pandasobj["address"]:
        coordinates.append(gis.geocode(address, timeout=2000)[1])
    for coord in coordinates:
        latitude.append(coord[0])
        longitude.append(coord[1])
    pandasobj["latitude"] = latitude
    pandasobj["longitude"] = longitude
    pandasobj.to_csv("static/geocoordinates.csv")
    return Markup(pandasobj.to_html(index=False, justify="center"))


@app.route("/")
def index():
    try:
        remove("static/geocoordinates.csv")
    except FileNotFoundError:
        pass
    return render_template("index.html")


@app.route("/answer", methods=["POST"])
def answer():
    if request.files["file_command"]:
        file = request.files["file_command"]
        try:
            contents = pd.read_csv(file)
        except (UnicodeDecodeError, ParserError):
            return render_template("answer.html",
                                   error="ERROR: the file doesn't contain valid"
                                         " unicode text")
        for key in contents.keys():
            if str(key).lower() == "address":
                table = create_table(contents)
                break
        else:
            return render_template("answer.html",
                                   error="ERROR: The CSV file doesn't "
                                         "contain a column named 'address'")
        return render_template("answer.html",
                               error=f"OPENED FILE: "
                                     f"{request.files['file_command'].filename}"
                               , table=table)
    else:
        return render_template("answer.html", error="NO FILE CHOSEN")


if __name__ == "__main__":
    app.debug = True
    app.run()
