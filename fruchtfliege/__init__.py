from pathlib import Path


from flask import Flask, Response, g

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('production.py')

# pylint: disable=wrong-import-position, import-outside-toplevel
from fruchtfliege import view

ROOT_PATH = Path(__file__).parent

STATIC_PATH = ROOT_PATH / 'static'
IMAGE_PATH = STATIC_PATH / 'images'
THUMBNAIL_PATH = STATIC_PATH / 'thumbnails'
FILE_PATH = STATIC_PATH / 'flies.csv'


class Sample:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@app.before_request
def before_request() -> None:
    import pandas as pd
    data = pd.read_csv(FILE_PATH, delimiter=',', encoding='utf-8', dtype=str)
    data = data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    data = data[data["participant"] != "?"]

    # Convert Latitude & Longitude to float (if necessary)
    data["Latitude"] = data["Latitude"].astype(float)
    data["Longitude"] = data["Longitude"].astype(float)

    g.df = data
    g.samples = [Sample(**row) for _, row in data.iterrows()]


@app.after_request
def apply_caching(response: Response) -> Response:
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
