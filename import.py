import csv
from urllib import urlretrieve
from os.path import splitext
from dataModel import *
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime

class IdGenerator:
    def __init__(self, session):
        self.session = session
        self.id_cursors = {}
    
    def __call__(self, subreddit):
        if subreddit in self.id_cursors:
            self.id_cursors[subreddit] += 1
            return self.id_cursors[subreddit]
        print("Looking up subreddit=", subreddit)
        start_number = self.session.query(func.max(Image.id)).filter(Image.subreddit==subreddit).one()[0]
        start_number = int(start_number) if start_number is not None else 0
        self.id_cursors[subreddit] = start_number
        return start_number 


def main(csv_file):
    engine = create_engine("mysql://scho2:scho2gtk@localhost/gtk")
    session_maker = sessionmaker(engine)
    session = session_maker()
    
    id_generator = IdGenerator(session)
    
    with open(csv_file, 'rb') as f:
        row_reader = csv.reader(f, delimiter=',')
    
        # Skip header
        next(row_reader, None)
    
        for row in row_reader:
            this_id = id_generator(row[0])
            _, ext = splitext(row[4])
            path = "images/%s.%d%s" % (row[0], this_id, ext)
            
            print(path, row[4])
            urlretrieve(row[4], path)
            session.add(Image(id=this_id, subreddit=row[0], score=row[2], title=row[3], image=path, date=datetime.fromtimestamp(int(row[8]))))
        
        session.commit()

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1]))
    
    