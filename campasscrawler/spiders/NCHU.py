# -*- coding: utf-8 -*-
import scrapy
from campasscrawler.items import CampasscrawlerItem
from timetable.models import Course

class NchuSpider(scrapy.Spider):
	name = "NCHU"
	allowed_domains = ["onepiece.nchu.edu.tw/cofsys/plsql/json_for_course?p_career="]
	start_urls = [
		'https://onepiece.nchu.edu.tw/cofsys/plsql/json_for_course?p_career=W',
		'https://onepiece.nchu.edu.tw/cofsys/plsql/json_for_course?p_career=U',
		'https://onepiece.nchu.edu.tw/cofsys/plsql/json_for_course?p_career=G',
		'https://onepiece.nchu.edu.tw/cofsys/plsql/json_for_course?p_career=D',
		'https://onepiece.nchu.edu.tw/cofsys/plsql/json_for_course?p_career=N',
		'https://onepiece.nchu.edu.tw/cofsys/plsql/json_for_course?p_career=O'
	]

	errCourse = {
		"U":[],
		"G":[],
		"D":[],
		"N":[],
		"O":[],
		"W":[]
	}

	def parse(self, response):
		import json
		data = json.loads(response.text)

		Course.objects.all().delete()

		CourseList = []
		CodeSet = set()
		school='NCHU'
		semester = '1052'

		for c in data["course"]:
			try:

				time = ''
				for i in c['time_parsed']:
					time += str(i['day']) + '-'
					for j in i['time']:
						time += str(j) + '-'
					time = time[:-1]
					time += ','

				if c['code'] not in CodeSet:
					CodeSet.add(c['code'])

					CourseList.append( 
						Course(
							**CampasscrawlerItem(
								school=school.upper(),
								semester=str(semester),
								code=c['code'],
								credits=c['credits'],
								title='{},{}'.format(
									c['title_parsed']['zh_TW'],
									c['title_parsed']['en_US']
								),
								department=c['department'],
								professor=c['professor'],
								time=time[:-1],
								intern_location=c['intern_location'][0],
								location=c['location'][0],
								obligatory=c['obligatory_tf'],
								language=c['language'],
								prerequisite=c['prerequisite'],
								note=c['note'],
								discipline=c['discipline']
							)
						)
					)
			except Exception as e:
				print('----------------------')
				print(response.url)
				print(str(e))
				print('----------------------')

		return {'array':CourseList}

	def truncateNewLineSpace(self, line):
		tmp = ""
		for i in line:
			if i != "\n" and i != " ":
				tmp+=i
		return tmp

	def validateTmpJson(self, tmpFile, degree):
		# truncate invalid char to turn it into json
		jsonStr = ""
		with open('json/'+tmpFile, 'r', encoding='UTF-8') as f:
			for line in f:
				tmp = self.truncateNewLineSpace(line)
				jsonStr +=tmp
		jsonStr = self.checkDegree(jsonStr, degree)
		return jsonStr

	def checkDegree(self, jsonStr, degree):
		# correct those Course which were placed in wrong degree dict.
		jsonDict = json.loads(jsonStr)
		degreeTable = {"U":["1","2","3","4","5","1A","1B","2A","2B","3A","3B", "4A", "4B", "5A", "5B"],"G":["6", "7"], "D":["8", "9"], "N":["1","2","3","4","5"],"O":["0","1","2","3","4","5"], "W":["6", "7"]}
		cleanDict = {'course':[]}
		for index, value in enumerate(jsonDict['course']):
			if value['class'] not in degreeTable[degree]:
				if value['class'] in degreeTable['D']:
					self.errCourse['D'].append(value)
				elif '在職' in value['for_dept'] or '碩士專班' in value['for_dept']:
					self.errCourse['W'].append(value)
				elif '碩士' in value['for_dept'] :
					self.errCourse['G'].append(value)
				elif '進修' in value['for_dept']:
					self.errCourse['N'].append(value)
				elif value['class'] in degreeTable['U']:
					self.errCourse['U'].append(value)
				elif value['class'] == 0 or value['for_dept'].find('全校共同')!=-1:
					self.errCourse['O'].append(value)
				elif '研究所' in value['for_dept']:
					self.errCourse['G'].append(value)
				else:
					print(value)
					raise Exception('clean ERR')
			elif degree == 'G':
				if '碩士專班' in value['for_dept']:
					self.errCourse['W'].append(value)
				else:
					cleanDict['course'].append(value)
			else:
				cleanDict['course'].append(value)

		return json.dumps(cleanDict)
