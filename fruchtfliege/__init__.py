from pathlib import Path

import pandas as pd
from flask import Flask, Response, g
from flask_babel import Babel

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('production.py')
babel = Babel(app)

# pylint: disable=wrong-import-position, import-outside-toplevel
from fruchtfliege import view

ROOT_PATH = Path(__file__).parent

STATIC_PATH = ROOT_PATH / 'static'
IMAGE_PATH = STATIC_PATH / 'images'
THUMBNAIL_PATH = STATIC_PATH / 'thumbnails'
FILE_PATH = STATIC_PATH  / 'flies.csv'


class Sample:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@app.before_request
def before_request() -> None:
    df = pd.read_csv(FILE_PATH, delimiter=',', encoding='utf-8', dtype=str)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    df = df[df["participant"] != "?"]

    # Convert Latitude & Longitude to float (if necessary)
    df["Latitude"] = df["Latitude"].astype(float)
    df["Longitude"] = df["Longitude"].astype(float)

    g.df = df
    g.samples = [Sample(**row) for _, row in df.iterrows()]


@app.after_request
def apply_caching(response: Response) -> Response:
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

