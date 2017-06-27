from flask import Flask, render_template, send_from_directory
from random import randint
from json import dumps
from uuid import uuid4
from datetime import datetime
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

    # A simple method to support multiple levels of dictionary indirection
    @staticmethod
    def get_i(obj, keys, default=None)
        while len(keys) > 0:
            indirect_key = keys.pop(0)
            obj = obj.get(indirect_key, default)
            if obj is default:
                return default
        return obj
            

    def random_pair(self):
        output = {}
        session = self.session_maker()
        
        post_parameters = request.get_json()
        
        # Check if the user_id is set. If not, we need to give them one
        user_id, user_id_was_set = post_paramters.get("user_id", None), True
        if user_id is None:
            user_id_was_set = False
            # Generate a new user_id to send to the user
            user_id = uuid4()
            session.add(User(userid=user_id))
            output.update({"user_id": user_id})
        else:
            # Check if the quiz_id is set. If not, we need to give them a new one
            quiz_id, quiz_id_was_set = post_parameters.get("quiz_id", None), True
            if quiz_id is None:
                quiz_id_was_set = False
                quiz_id = uuid4()
                session.add(InitialQuiz(quizid=quiz_id, userid=user_id))
            else:
                # Check if the round_id is set. If not, we need to create a new round_id
                round_id, round_id_was_set = post_parameters.get("round_id", None), True
                if round_id is None:
                    round_id_was_set = False
                    round_id = uuid4()
                else:
                    # Check if the round_no is set. If not, we need to create a new round_id because the round is invalid
                    round_no, round_no_was_set = post_parameters.get("round_no", None), True
                    if round_no is None:
                        round_id_was_set, round_no_was_set = False, False
                        round_id = uuid4()
                        round_no = 0
                    else:
                        # We need to create a new round since round no was not set (round was invalid)
                        round_id_was_set, round_no_was_set = False, False
                        round_id = uuid4()
                        round_no = 0
        
        ############################################################################################
        ## SANITY CHECK: after this barrier, each of the following should be defined:              #
        ## user_id                                                                                 #
        ## quiz_id                                                                                 #
        ## round_id                                                                                #
        ## round_no                                                                                #
        ## We can comment this out once we are reasonably sure the logic above has no bugs.        #
        ############################################################################################
        try:
            user_id, quiz_id, round_id, round_no
        except NameError as e:
            print("Logic Error (required variable unset): " + e)
        ############################################################################################
        ## END SANITY CHECK                                                                        #
        ############################################################################################

        if all([quiz_id_was_set, round_id_was_set, round_no_was_set, user_id_was_set]):
            # Check if the user sent output for us to record from a previous round
            preferred_choice = self.get_i(post_parameters, ["preferredChoice", "value"])
            preferred_choice_time = post_parameters.get("preferredChoiceTime")
            upvote_choice = self.get_id(post_parameters, ["upvoteChoice", "value"])
            upvote_choice_time = post_parameters.get("upvoteChoiceTime")
            if all(i is not None for i in [preferred_choice, preferred_choice_time, upvote_choice, upvote_choice_time]):
                # All the necessary data is set, so we can record the information
                
                # TODO:
                #  - ADD ALL THE DATA TO THE ROUND DATABASE OBJECT
                #  - DELETE THE TEMPORARY INITIAL ROUND OBJECT
                
                # This round was successfully recorded, so we can serve the next round
                round_no += 1
        
        # BEGIN GENERATE NEW ROUND STUFF
        
        # Choose two random images
        # TODO: make this more efficient; choose two random images from the same subreddit
        result = session.query(Image)
        count = result.count()
        if count < 2:
            raise LookupError("Not enough information error")

        idx1, idx2 = randint(0, count-1), randint(0, count-1)
        while idx1 == idx2:
            idx2 = randint(0, count-1)

        results = result.all()

#         start_time = datetime()
#         session.add(InitialRound(
#             roundid=round_id,
#             roundno=round_no
#             starttime=start_time,
#             image1id=results[idx1].id,
#             image2id=results[idx2].id,
#         ))

        output.update({
            "image1": {
                "image_id": results[idx1].id,
	            "subreddit": results[idx1].subreddit,
	            "score": results[idx1].score,
	            "title": results[idx1].title,
            	"url": results[idx1].image
            },
            "image2": {
                "image_id": results[idx2].id,
	            "subreddit": results[idx2].subreddit,
	            "score": results[idx2].score,
	            "title": results[idx2].title,
            	"url": results[idx2].image
            }
        })
        
        session.commit()
        return dumps(output)


if __name__ == '__main__':

    engine = create_engine("mysql://scho2:scho2gtk@localhost/gtk")

    session_maker = sessionmaker(engine)

    api = API(session_maker)

    app.route('/random_pair.json', methods=['POST'])(api.random_pair)
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
