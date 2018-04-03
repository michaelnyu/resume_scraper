import requests
import re 
import os
import csv
import urllib
import ssl
import PyPDF2
from PyPDF2 import PdfFileReader

def main():
	if not os.path.exists('resumes/'):
		os.makedirs('resumes/')

	with open('resumeurls.csv', newline='',encoding='utf-8', errors='ignore') as f:
		csv_reader = csv.reader(f)
		csv_headings = next(csv_reader)

		# for i in range(0, 1430):
		line = next(csv_reader)

		name = 1
		while line != "":
			if name < 0:
				name += 1
				line = next(csv_reader)
			else:
				if len(line) > 0:
					file_link = line[0]
					print(file_link, name)

					# test if it's a valid url
					request = urllib.request.Request(file_link)
					try:
						response = urllib.request.urlopen(request)
					except:
						line = next(csv_reader)
						continue

					if bool(re.search(r'.pdf$', file_link)):
						# is .pdf extension
						if (download_pdf(file_link, name)):
							name += 1
					elif bool(re.search(r'google.com', file_link)) and bool(re.search(r'[-\w]{25,}', file_link)):
						# is google drive link
						file_id = re.search(r'[-\w]{25,}', file_link).group()
						destination = 'resumes/' + str(name) + '.pdf'
						if (download_google_drive(file_id, destination)):
							name += 1

				line = next(csv_reader)

def download_pdf(download_url, name):
	r = requests.head(download_url)
	if r.status_code >= 300:
		return False

	response = urllib.request.urlopen(download_url)
	file = open("resumes/" + str(name) + ".pdf", 'wb')
	file.write(response.read())
	file.close()
	return True

def download_google_drive(id, destination):
	URL = "https://docs.google.com/uc?"

	session = requests.Session()

	response = session.get(URL, params = { 'id' : id }, stream = True)
	token = get_confirm_token(response)

	if token:
		params = { 'id' : id, 'confirm' : token }
		response = session.get(URL, params = params, stream = True)

	save_response_content(response, destination)    

	try:
		swag = PyPDF2.PdfFileReader(open(destination, "rb"))
	except:
		print("invalid PDF file")
		os.remove(destination, dir_fd=None)
		return False

	return True



def get_confirm_token(response):
	for key, value in response.cookies.items():
		if key.startswith('download_warning'):
			return value

	return None

def save_response_content(response, destination):
	CHUNK_SIZE = 32768

	with open(destination, "wb") as f:
		for chunk in response.iter_content(CHUNK_SIZE):
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)

if __name__ == "__main__":

	requests.packages.urllib3.disable_warnings()
	try:
		_create_unverified_https_context = ssl._create_unverified_context
	except AttributeError:
		pass
	else:
		# Handle target environment that doesn't support HTTPS verification
		ssl._create_default_https_context = _create_unverified_https_context

	main()
	