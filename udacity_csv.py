import json,urllib,datetime
from pymongo import MongoClient
import csv

client = MongoClient()
db = client['udacity_cache']
courses = db['courses']
tracks = db['tracks']
degrees = db['degrees']

now=datetime.datetime.now()
one_week_ago=now-datetime.timedelta(days=7)

def write_dict(dicts,keys,out):
	with open(out, 'wb') as output_file:
	    dict_writer = csv.DictWriter(output_file, keys)
	    dict_writer.writeheader()
	    dict_writer.writerows(dicts)

def get_from_www():
	response=urllib.urlopen('https://www.udacity.com/public-api/v0/courses')
	json_response=json.loads(response.read())
	j_courses=json_response['courses']
	j_tracks=json_response['tracks']
	j_degrees=json_response['degrees']
	return [j_courses,j_tracks,j_degrees]

def get_csv_from_db(collection,keys):
	order_str=''
	for key in keys:
		order_str+=key+','
	retval=[order_str[:-1]]
	for doc in collection.find():
		doc_str=''
		for key in keys:
			if key in doc:
				try:
					doc_str+=doc[key].encode('ascii','ignore')+','
				except:
					doc_str+=str(doc[key])+','
			else:
				doc_str+=','
		retval.append(doc_str[:-1].replace('\n','<br/>'))
	return retval

def write_csv():
	cache=courses.find_one()
	if not cache:
		j_courses=get_from_www()[0]
		for course in j_courses:
			course.update({'cached_time':now})
			courses.insert_one(course)
	elif one_week_ago > cache['cached_time']:
		j_courses=get_from_www()[0]
		for course in j_courses:
			course.update({'cached_time':now})
			courses.insert_one(course)
	keys=set()
	for course in courses.find():
		keys.update(course.keys())
	keys.discard('_id')
	data=get_csv_from_db(courses,keys)
	with open('out.csv','w') as f:
		for line in data:
			f.write('%s\n'%line)

write_csv()
