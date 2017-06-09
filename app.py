from flask import Flask, render_template
from random import randint
from json import dumps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dataModel import *

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/index.js')
def js():
    return render_template('index.js')


class API():
    def __init__(self, session_maker):
        self.session_maker = session_maker

    def random_pair(self):
        session = self.session_maker()

        result = session.query(Image.image)

        count = result.count()
        if count < 2:
            raise LookupError("Not enough information error")

        idx1, idx2 = randint(0, count-1), randint(0, count-1)
        while idx1 == idx2:
            idx2 = randint(0, count-1)

        results = result.all()

        output = dumps({
            "image1": results[idx1][0],
            "image2": results[idx2][0]
        })

        return output


if __name__ == '__main__':

    engine = create_engine("sqlite:///gtk.db")

    session_maker = sessionmaker(engine)

    api = API(session_maker)

    app.route('/random_pair.json')(api.random_pair)

    app.run(host='0.0.0.0')



#@app.route('/api/random')
# def random():
#     with open("GTK_images.csv", encoding="latin-1") as f:
#         lines = [line.strip() for line in f.readlines()]
#         line = lines[randint(0, len(lines) - 1)].split(",")
#         return dumps({
#             "subreddit": line[0],
#             "id": line[0],
#             "score": line[1],
#             "title": line[2],
#             "url": line[3],
#             "year": line[4],
#             "month": line[5],
#             "day": line[6],
#             "created": line[7],
#             "date": line[8]
#         })
