from flask import g

from fruchtfliege import app


@app.route('/')
def index() -> str:
    return {"samples": [vars(sample) for sample in g.samples]}
    # return render_template('index.html')


