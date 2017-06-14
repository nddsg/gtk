from flask import Flask, render_template, send_from_directory
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

@app.route('/images/<path:path>')
def send_img(path):
    return send_from_directory('images', path)


class API():
    def __init__(self, session_maker):
        self.session_maker = session_maker

    def dropdown_populate(self):
        session = self.session_maker()
        result = session.query(Image.subreddit).distinct()
        output = dumps({
	        "subreddit": [i for j in list(result) for i in j]
        })
        
        return output

    def random_pair(self):
        session = self.session_maker()

        result = session.query(Image)

        count = result.count()
        if count < 2:
            raise LookupError("Not enough information error")

        idx1, idx2 = randint(0, count-1), randint(0, count-1)
        while idx1 == idx2:
            idx2 = randint(0, count-1)

        results = result.all()

        output = dumps({
            "image1": {
	            "subreddit": results[idx1].subreddit,
	            "score": results[idx1].score,
	            "title": results[idx1].title,
            	"url": results[idx1].image
            },
            "image2": {
	            "subreddit": results[idx2].subreddit,
	            "score": results[idx2].score,
	            "title": results[idx2].title,
            	"url": results[idx2].image
            }
        })

        return output


if __name__ == '__main__':

    engine = create_engine("mysql://scho2:scho2gtk@localhost/gtk")

    session_maker = sessionmaker(engine)

    api = API(session_maker)

    app.route('/random_pair.json')(api.random_pair)
    app.route('/dropdown_populate.json')(api.dropdown_populate)

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
