
from fruchtfliege import app

@app.route('/')
def home():
    return "Welcome to the Flask + Dash app!"
