import subprocess, time

while True:
	subprocess.call(['scrapy', 'crawl', 'NCHU'])
	print('-----------------------------------')
	print('start sleep')
	print('-----------------------------------')
	time.sleep(600)