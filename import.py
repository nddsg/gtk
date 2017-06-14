import csv
from urllib import urlretrieve
from os.path import splitext
from dataModel import *
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime

class IdGenerator:
	def __init__(self, start_id_cursor_value):
		self.id_cursor = start_id_cursor_value - 1;
	
	def __call__(self):
		self.id_cursor += 1
		return self.id_cursor
	


def main(csv_file):
	engine = create_engine("mysql://scho2:scho2gtk@localhost/gtk")
	session_maker = sessionmaker(engine)
	session = session_maker()
	
	result = session.query(func.max(Image.id)).one()
	start_id = int(result[0] if result[0] else 0)

	
	id_generator = IdGenerator(start_id + 1)
	
	with open(csv_file, 'rb') as f:
		row_reader = csv.reader(f, delimiter=',')
	
		# Skip header
		next(row_reader, None)
	
		for row in row_reader:
			this_id = id_generator()
			_, ext = splitext(row[4])
			path = "images/%d%s" % (this_id, ext)
			
			print(path, row[4])
			urlretrieve(row[4], path)
			session.add(Image(id=this_id, subreddit=row[0], score=row[2], title=row[3], image=path, date=datetime.fromtimestamp(int(row[8]))))
		
		session.commit()

if __name__ == "__main__":
	import sys
	sys.exit(main(sys.argv[1]))
	
	