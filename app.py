from flask import Flask, render_template, send_from_directory, request
from random import choice
from json import dumps
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine, func, or_
from sqlalchemy.orm import sessionmaker
from itertools import combinations, islice

from dataModel import *

app = Flask(__name__)

debug = True


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/index.js')
def js():
    return render_template('index.js')

@app.route('/demographic_survey.html')
def survey():
    return render_template('demographic_survey.html')


@app.route('/images/<path:path>')
def send_img(path):
    return send_from_directory('images', path)


def prime_generator(start=2, max=None):
    primes = [start]
    i = start
    yield start
    while max is None or i <= max:
        i += 1
        if any([i % p == 0 for p in primes]): continue
        primes.append(i)
        yield i


def least_coprime(a):
    p = prime_generator(max=a - 1)
    while True:
        potential = next(p)
        if a % potential != 0:
            return potential


def nth(iterable, n, default=None):
    return next(islice(iterable, n, None), default)


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

    @staticmethod
    def choose_random_subreddit(session):
        subreddits = session.query(Image.subreddit).group_by(Image.subreddit).all()
        subreddit, = choice(subreddits)
        if debug:
            print("Choose random subreddit=", subreddit)
        return subreddit

    @staticmethod
    def generate_new_user(session, commit=True):
        user_id = str(uuid4())
        session.add(User(userid=user_id))
        if debug:
            print("Created new user with id=", user_id)
        if commit:
            session.commit()
        return user_id

    @staticmethod
    def generate_new_initial_quiz(session, user_id, subreddit=None, commit=True):
        quiz_id = str(uuid4())
        if subreddit is None:
            subreddit = API.choose_random_subreddit(session)
        if debug:
            print("Created new quiz with id=", quiz_id)
        session.add(Quiz(userid=user_id, quizid=quiz_id, subreddit=subreddit, maturity="partial"))
        if commit:
            session.commit()
        return quiz_id

    @staticmethod
    def generate_new_initial_round(session, quiz_id, round_no=0, start_time=None, commit=True):
        round_id = str(uuid4())

        if debug:
            print("Looking up information for quiz with id=", quiz_id)

        subreddit, = session.query(Quiz.subreddit).filter(Quiz.quizid == quiz_id).one()

        if debug:
            print("Detected subreddit=", subreddit)

        count, = session.query(func.count(1)).filter(Image.subreddit == subreddit).one()

        if debug:
            print("Found ", count, " images in this subreddit.")

        if count is None or subreddit is None:
            raise RuntimeError("Likely no quiz found when creating round (possibly other error with database state)")
        elif count < 5:  # (x choose 2) >= 10 => x >= 5
            raise RuntimeError("Not enough images in this subreddit to go 10 rounds.")

        # OLD WAY
        # idx1, idx2 = randint(0, count-1), randint(0, count-1)
        # while idx1 == idx2:
        #     idx2 = randint(0, count-1)

        # Better way : a deterministic method to generate non-repeated pairs of image indices based on quiz_id and round_no
        pair_count = (count * (count - 1)) / 2 # pair_count = (count choose 2)
        stride = round_no * least_coprime(pair_count)
        index = (hash(quiz_id) + stride) % pair_count
        idx1, idx2 = nth(combinations(range(count), 2), index)
        
        if debug:
            print("Initial round: ", pair_count, " possible combinations;")
            print("Initial round: using index=", index, " with offset from base=", stride)
            print("Chosen tuple is (", idx1, ",", idx2, ")")

        image1, image2 = session.query(Image).filter(Image.subreddit == subreddit, or_(Image.id == idx1, Image.id == idx2)).all()

        if start_time is None:
            start_time = datetime.now()

        session.add(InitialRound(
            quizid=quiz_id,
            roundid=round_id,
            roundno=round_no,
            starttime=start_time,
            image1id=image1.id,
            image2id=image2.id,
        ))

        if commit:
            session.commit()

        return round_id, round_no, image1, image2, subreddit

    @staticmethod
    def upgrade_round_to_full(
            session, round_id, preferred_choice, preferred_choice_time,
            upvote_choice, upvote_choice_time, correct, commit=True
    ):
        if debug:
            print("Upgrading round_id ", round_id, " to full round.")
        
        partial_round = session.query(InitialRound).filter(InitialRound.roundid == round_id).one()

        session.add(Round(
            roundid=round_id,
            roundno=partial_round.roundno,
            quizid=partial_round.quizid,
            starttime=partial_round.starttime,
            image1id=partial_round.image1id,
            image2id=partial_round.image2id,
            preferredchoicetime=preferred_choice_time,
            upvotechoicetime=upvote_choice_time,
            preferredchoice=preferred_choice,
            upvotechoice=upvote_choice,
            correct=correct,
        ))
        session.delete(partial_round)

        if commit:
            session.commit()

    @staticmethod
    def upgrade_quiz_to_full(session, quiz_id, commit=True):
        if debug:
            print("Upgrading quiz with quiz_id=", quiz_id)
        quiz = session.query(Quiz).filter(Quiz.quizid == quiz_id).one()
        quiz.maturity = "Complete"
        if commit:
            session.commit()

    def random_pair(self):
        session = self.session_maker()

        if debug:
            print("Request parameters: ", {i: request.form[i] for i in request.form})

        post_parameters = request.form

        if post_parameters is None:
            if debug:
                print("Initializing with default settings...")

            user_id = self.generate_new_user(session=session)
            quiz_id = self.generate_new_initial_quiz(session=session, user_id=user_id)
        else:
            user_id = post_parameters.get("user_id", None)
            user_id_was_set = (user_id is not None)

            if not user_id_was_set:
                user_id = self.generate_new_user(session=session)
            
            if debug:
                if user_id_was_set:
                    print("(User id was set=",user_id,")")
                else:
                    print("(User id was not set.)")

            quiz_id = post_parameters.get("quiz_id", None)
            quiz_id_was_set = (quiz_id is not None)

            if not quiz_id_was_set:
                quiz_id = self.generate_new_initial_quiz(session=session, user_id=user_id)
            
            if debug:
                if quiz_id_was_set:
                    print("(Quiz id was set=",quiz_id,")")
                else:
                    print("(Quiz id was not set.)")

            round_id = post_parameters.get("round_id", None)
            round_id_was_set = (round_id is not None)
            
            if debug:
                if round_id_was_set:
                    print("(Round id was set=",round_id,")")
                else:
                    print("(Round id was not set.)")

            round_no = post_parameters.get("round_no", 0)
            round_no_was_set = (round_no is not 0 and round_no is not None)

            if round_no_was_set:
                round_no = int(round_no)

            if debug:
                if round_no_was_set:
                    print("(Round number was set=",round_no,")")
                else:
                    print("(Round number was not set.)")

            preferred_choice = post_parameters.get("preferredChoice[value]", None)
            preferred_choice_was_set = (preferred_choice is not None)
            
            if debug:
                if preferred_choice_was_set:
                    print("(Preferred choice was set=",preferred_choice,")")
                else:
                    print("(Preferred chocie was not set.)")

            preferred_choice_time = post_parameters.get("preferredChoiceTime", None)
            preferred_choice_time_was_set = (preferred_choice_time is not None)
            
            if debug:
                if preferred_choice_time_was_set:
                    print("(Preferred choice time was set=",preferred_choice_time,")")
                else:
                    print("(Preferred choice time was not set.)")

            upvote_choice = post_parameters.get("upvoteChoice[value]", None)
            upvote_choice_was_set = (upvote_choice is not None)
            
            if debug:
                if upvote_choice_was_set:
                    print("(Upvote choice was set=",upvote_choice,")")
                else:
                    print("(Upvote choice  was not set.)")

            upvote_choice_time = post_parameters.get("upvoteChoiceTime", None)
            upvote_choice_time_was_set = (upvote_choice_time is not None)
            
            if debug:
                if upvote_choice_time_was_set:
                    print("(Upvote choice time number was set=",upvote_choice_time,")")
                else:
                    print("(Upvote choice time number was not set.)")

            correct_choice = post_parameters.get("correct", None)
            correct_choice_was_set = (correct_choice is not None)
            
            if debug:
                if correct_choice_was_set:
                    print("(Correct was set=",correct_choice,")")
                else:
                    print("(Correct was not set.)")

            if all([
                preferred_choice_was_set,
                preferred_choice_time_was_set,
                upvote_choice_was_set,
                upvote_choice_time_was_set,
                correct_choice_was_set,
                round_id_was_set,
                round_no_was_set
            ]):
                self.upgrade_round_to_full(
                    session=session,
                    round_id=round_id,
                    preferred_choice=preferred_choice,
                    preferred_choice_time=preferred_choice_time,
                    upvote_choice=upvote_choice,
                    upvote_choice_time=upvote_choice_time,
                    correct=correct_choice
                )
                if round_no >= 9:
                    self.upgrade_quiz_to_full(session, quiz_id)
                    quiz_id = self.generate_new_initial_quiz(session, user_id)
                    round_no = 0
                else:
                    round_no += 1

        round_id, round_no, image1, image2, subreddit = self.generate_new_initial_round(session=session, quiz_id=quiz_id, round_no=round_no)
        output = dumps({
            'user_id': user_id,
            'quiz_id': quiz_id,
            'round_id': round_id,
            'round_no': round_no,
            'subreddit': subreddit,
            'image1': {
                'id': image1.id,
                'score': image1.score,
                'title': image1.title,
                'url': image1.image,
            },
            'image2': {
                'id': image2.id,
                'score': image2.score,
                'title': image2.title,
                'url': image2.image,
            },
        })
        
        if debug:
            print("Sending response:", output)
            
        return output


if __name__ == '__main__':
    engine = create_engine("mysql://scho2:scho2gtk@localhost/gtk")

    session_maker = sessionmaker(engine)

    api = API(session_maker)

    app.route('/random_pair.json', methods=['POST'])(api.random_pair)
    app.route('/dropdown_populate.json')(api.dropdown_populate)

    app.run(host='0.0.0.0')
