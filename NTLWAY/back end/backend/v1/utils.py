import time
import imaplib
import email
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email.header import decode_header
import os
import sys
import json
import PyPDF2

from bs4 import BeautifulSoup

from pyvirtualdisplay import Display
import pdfkit

from jinja2 import Environment, FileSystemLoader, Template
from PyPDF2 import PdfFileMerger
from weasyprint import HTML

class Gmail:

	def __init__(self, username,password):
		self.username = username
		self.password = password
		self.imap_server = imaplib.IMAP4_SSL(host="imap.gmail.com")
		self.imap_server.login(username,password)
		self.imap_server.select()

		self.smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context())
		self.smtp_server.login(username,password)

	def parse_mail_body(self,body):
		"""parse email body to extract table content"""
		soup = BeautifulSoup(body, 'html.parser')
		tables = soup.findAll("table")
		if tables:
			for table in tables:
				output_rows = []
				for table_row in table.findAll('tr'):
					columns = table_row.findAll('td')
					output_row = []
					for column in columns:
						output_row.append(column.text)
					output_rows.append(output_row)
			return output_rows
		return None

	def convert_to_json(self, rows):
		"""Convert a parsed table output into json"""
		if not rows:
			return None


		# client infos
		client = {}
		for i in rows[0]:
			client[i[0]] = i[1]

		# departure
		departure = {}
		for i in rows[1]:
			departure[i[0]] = i[1]

		# arrival infos
		arrival = {}
		for i in rows[2]:
			arrival[i[0]] = i[1]

		# additional
		additional = {}
		for i in rows[3]:
			additional[i[0]] = i[1]
		data = {
			"client":client,
			"departure":departure,
			"arrival":arrival,
			"additional":additional
		}
		return data

	def get_messages_ids(self, search_criteria,search_value):

		_, message_numbers_raw = self.imap_server.search(None,search_criteria,search_value)
		multipart_messages = []
		#messages_numbers = [int(x) for x in  message_numbers_raw[0].split()]
		#messages_numbers.reverse()
		messages_ids = message_numbers_raw[0].split()
		messages_ids.reverse()
		return messages_ids

	def fetch_mail_data_by_id(self,mail_id):
		data = {}
		_, msg = self.imap_server.fetch(mail_id, '(RFC822)')
		message = email.message_from_bytes(msg[0][1])
		thread_msgs = []
		if message.is_multipart():
			for part in message.walk():
				if part.get_content_type() == "text/html":
					body = part.get_payload(decode=True) #to control automatic email-style MIME decoding (e.g., Base64, uuencode, quoted-printable)
					body = body.decode()
					soup = BeautifulSoup(body, 'html.parser')
					tables = soup.findAll("table")
					if tables:
						for table in tables:
							output_rows = []
							for table_row in table.findAll('tr'):
								columns = table_row.findAll('td')
								output_row = []
								for column in columns:
									output_row.append(column.text)
								output_rows.append(output_row)
							thread_msgs.append(output_rows)
	
		data = {
			"id": int(mail_id),
			"subject": message.get('subject'),
			"from": message["from"],
			"to": message["to"],
			"cc": message["cc"],
			"bcc": message["bcc"],
			"content_type":message.get_content_type(),
			"multipart": message.is_multipart(),
			"messages" : self.convert_to_json(thread_msgs)
		}
		return data

	def fetch_messages(self, search_criteria,search_value):

		_, message_numbers_raw = self.imap_server.search(None,search_criteria,search_value)
		multipart_messages = []
		for message_number in message_numbers_raw[0].split():
			try:
				_, msg = self.imap_server.fetch(message_number, '(RFC822)')
				message = email.message_from_bytes(msg[0][1])
				thread_msgs = []
				if message.is_multipart():
					for part in message.walk():
						if part.get_content_type() == "text/html":
							body = part.get_payload(decode=True) #to control automatic email-style MIME decoding (e.g., Base64, uuencode, quoted-printable)
							body = body.decode()
							soup = BeautifulSoup(body, 'html.parser')
							tables = soup.findAll("table")
							if tables:
								for table in tables:
									output_rows = []
									for table_row in table.findAll('tr'):
										columns = table_row.findAll('td')
										output_row = []
										for column in columns:
											output_row.append(column.text)
										output_rows.append(output_row)
									thread_msgs.append(output_rows)
			
				data = {
					"id": int(message_number),
					"subject": message.get('subject'),
					"from": message["from"],
					"to": message["to"],
					"cc": message["cc"],
					"bcc": message["bcc"],
					"content_type":message.get_content_type(),
					"multipart": message.is_multipart(),
					"messages" : self.convert_to_json(thread_msgs)
				}

				multipart_messages.append(data)
			except:
				pass
		return multipart_messages
	
	def send_mail(self, receiver_email, attachement_filename=None):
		subject = "An email with attachment from Python"
		body = "This is an email with attachment sent from Python"

		# Create a multipart message and set headers
		message = MIMEMultipart()
		message["From"] = self.username
		message["To"] = receiver_email
		message["Subject"] = subject
		message["Bcc"] = receiver_email  # Recommended for mass emails

		# Add body to email
		message.attach(MIMEText(body, "plain"))

		# Open PDF file in binary mode
		with open(attachement_filename, "rb") as attachment:
			# Add file as application/octet-stream
			# Email client can usually download this automatically as attachment
			part = MIMEBase("application", "octet-stream")
			part.set_payload(attachment.read())

		# Encode file in ASCII characters to send by email    
		encoders.encode_base64(part)

		# Add header as key/value pair to attachment part
		part.add_header(
			"Content-Disposition",
			"attachment; filename="+str(attachement_filename),
		)

		# Add attachment to message and convert message to string
		message.attach(part)
		text = message.as_string()

		# Log in to server using secure context and send email
		context = ssl.create_default_context()
		self.smtp_server.sendmail(self.username, receiver_email, text)

class DevisUtils:

	TEMPLATES_DIR = "templates"
	OUTPUTS_DIR = "outputs"
	COMMON_DIR = str(os.path.dirname(os.path.abspath(__file__)))+"/common"
	TEMPLATE1 = "template1.html"
	TEMPLATE2 = "template2.html"
	
	
	PAGE2 = "condition_general.pdf"
    
	PAGE3 = "page3.pdf"
	
    
	def __init__(self,data,file_basename):

		# we need a virtual display so the pdfkit works
		#self.display = Display(visible=0, size=(800, 600))
		self.data = data
		self.file_basename = file_basename

		self.devis_page1_html_filename = str(self.COMMON_DIR)+"/"+str(self.OUTPUTS_DIR)+"/"+str(self.file_basename)+"_page1.html"
		self.devis_page1_pdf_filename = str(self.COMMON_DIR)+"/"+str(self.OUTPUTS_DIR)+"/"+str(self.file_basename)+"_page1.pdf"

		
		self.devis_page2_pdf_filename = str(self.COMMON_DIR)+"/"+str(self.OUTPUTS_DIR)+"/"+str(self.PAGE2)
		
		   
		self.devis_page3_pdf_filename = str(self.COMMON_DIR)+"/"+str(self.OUTPUTS_DIR)+"/"+str(self.PAGE3)
        
		
		self.devis_filename = str(self.COMMON_DIR)+"/"+str(self.OUTPUTS_DIR)+"/"+str(self.file_basename)+".pdf"

		#self.display.start()

	def process_data(self,data):
		for key in data.keys():
			if data[key] is None or data[key] == "None":
				data[key] = ""

		return data
	def delete_file(self,file):
		if os._exists(file):
    			os.removedirs(file)
		else:
  			print("The file does not exist")

	def template_to_html(self,data,template_name,output_filename,):
		"""render a html template with provided data """
		processed_data = self.process_data(data)	
		j2_env = Environment( loader = FileSystemLoader(str(self.COMMON_DIR)+"/"+str(self.TEMPLATES_DIR)+"/") )		
		template = j2_env.get_template(template_name)

		with open(output_filename, 'w', encoding='UTF-8' ) as fh:       
			fh.write(template.render(processed_data))
	
	

	def html_to_pdf(self,input_filename,output_filename):
		""" convert html to pdf """

		# generate a pdf devis from the template
		#pdfkit.from_file(input_filename,output_filename)
		HTML(filename=input_filename).write_pdf(output_filename)
	
	def generate_devis_page1(self):
	
		"""Generating the First Page"""
	
		# template 1 => html 1
		self.template_to_html(self.data,template_name=self.TEMPLATE1,output_filename=self.devis_page1_html_filename)

		# html 1 => pdf 1
		self.html_to_pdf(input_filename=self.devis_page1_html_filename,output_filename=self.devis_page1_pdf_filename)

	def fusion_pdf_files(self,file1,file2,file3,output_file):	
		
		merger = PdfFileMerger(strict=False)
        
		
		merger.append(file1)
		merger.append(file2)
		merger.append(file3)

		merger.write(output_file)
		merger.close()

		
	def generate_devis(self):

		# generate page 1
		self.generate_devis_page1()
		

		
		
		# fusion two files 

		self.fusion_pdf_files(file1=self.devis_page1_pdf_filename,file2=self.devis_page2_pdf_filename,file3=self.devis_page3_pdf_filename,output_file=self.devis_filename) 
		
		# cleanup ( delete tmp files )

		self.delete_file(self.devis_page1_html_filename)
		self.delete_file(self.devis_page1_pdf_filename)

		
		

		return self.devis_filename
		
	

	def send_devis(self,sender_email, sender_password, receiver_email):
		"""send devis by mail""" 

		# establish smtp connection

		self.smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context())
		self.smtp_server.login(sender_email,sender_password)

		subject = "Hayadem Devis"
		body = "This is an auto-generated email with attachment the Devis from Hayadem"

		# Create a multipart message and set headers
		message = MIMEMultipart()
		message["From"] = sender_email
		message["To"] = receiver_email
		message["Subject"] = subject

		# Add body to email
		message.attach(MIMEText(body, "plain"))

		attachement_filename = self.devis_filename
		# Open PDF file in binary mode
		with open(attachement_filename, "rb") as attachment:
			# Add file as application/octet-stream
			# Email client can usually download this automatically as attachment
			part = MIMEBase("application", "octet-stream")
			part.set_payload(attachment.read())

		# Encode file in ASCII characters to send by email    
		encoders.encode_base64(part)

		# Add header as key/value pair to attachment part
		part.add_header(
			"Content-Disposition",
			"attachment; filename="+str(os.path.basename(attachement_filename)),
		)

		# Add attachment to message and convert message to string
		message.attach(part)
		text = message.as_string()

		# Log in to server using secure context and send email
		context = ssl.create_default_context()
		self.smtp_server.sendmail(sender_email, receiver_email, text)

#partie siwar
class LettreUtils:
    
	TEMPLATES_DIR = "templates"
	OUTPUTS_DIR = "outputs"
	COMMON_DIR = str(os.path.dirname(os.path.abspath(__file__)))+"/common"
	Lettre = "lettre-de-voiture.html"

	def __init__(self,data,file_basename):

		# we need a virtual display so the pdfkit works
		#self.display = Display(visible=0, size=(800, 600))
		self.data = data
		self.file_basename = file_basename

		self.lettre_de_voiture_html_filename = str(self.COMMON_DIR)+"/"+str(self.OUTPUTS_DIR)+"/"+str(self.file_basename)+".html"
		self.lettre_de_voiture_pdf_filename = str(self.COMMON_DIR)+"/"+str(self.OUTPUTS_DIR)+"/"+str(self.file_basename)+".pdf"

		self.lettre_de_voiture_filename = str(self.COMMON_DIR)+"/"+str(self.OUTPUTS_DIR)+"/"+str(self.file_basename)+".pdf"

		#self.display.start()

	def process_data(self,data):
		for key in data.keys():
			if data[key] is None or data[key] == "None":
				data[key] = ""

		return data
	def delete_file(self,file):
		
		if os._exists(file):
			os.removedirs(file)
		else:
  			print("The file does not exist")

	def template_to_html(self,data,template_name,output_filename,):
		"""render a html template with provided data """
		processed_data = self.process_data(data)	
		j2_env = Environment( loader = FileSystemLoader(str(self.COMMON_DIR)+"/"+str(self.TEMPLATES_DIR)+"/") )		
		template = j2_env.get_template(template_name)
		
		with open(output_filename, 'w', encoding='UTF-8') as fh:
			fh.write(template.render(processed_data))

	def html_to_pdf(self,input_filename,output_filename):
		""" convert html to pdf """

		# generate a pdf devis from the template
		#pdfkit.from_file(input_filename,output_filename)
		HTML(filename=input_filename).write_pdf(output_filename)
	
	def generate_lettre(self):
	
		"""Generating the First Page"""
	
		# lettre de voiture => html 1
		self.template_to_html(self.data,template_name=self.Lettre,output_filename=self.lettre_de_voiture_html_filename)

		# html 1 => pdf 1
		self.html_to_pdf(input_filename=self.lettre_de_voiture_html_filename,output_filename=self.lettre_de_voiture_pdf_filename)

		

		return self.lettre_de_voiture_filename

def send_lettre(self,sender_email, sender_password, receiver_email):
		"""send lettre by mail""" 

		# establish smtp connection

		self.smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context())
		self.smtp_server.login(sender_email,sender_password)

		subject = "Hayadem Lettre De Voiture"
		body = "This is an auto-generated email with attachment the  from Hayadem"

		# Create a multipart message and set headers
		message = MIMEMultipart()
		message["From"] = sender_email
		message["To"] = receiver_email
		message["Subject"] = subject

		# Add body to email
		message.attach(MIMEText(body, "plain"))

		attachement_filename = self.lettre_de_voiture_filename
		# Open PDF file in binary mode
		with open(attachement_filename, "rb") as attachment:
			# Add file as application/octet-stream
			# Email client can usually download this automatically as attachment
			part = MIMEBase("application", "octet-stream")
			part.set_payload(attachment.read())

		# Encode file in ASCII characters to send by email    
		encoders.encode_base64(part)

		# Add header as key/value pair to attachment part
		part.add_header(
			"Content-Disposition",
			"attachment; filename="+str(os.path.basename(attachement_filename)),
		)

		# Add attachment to message and convert message to string
		message.attach(part)
		text = message.as_string()

		# Log in to server using secure context and send email
		context = ssl.create_default_context()
		self.smtp_server.sendmail(sender_email, receiver_email, text)

class Formule:

	# les constantes
	_MONTE_CH = 209
	_PIANO = 200
	_GARAGE = 30
	_ETAGE = 3
	_DEM = 150
	_CAMION = 160
	_ESCOURETTE = 50

	def __init__(self, etage_depart, garage_depart, cave_depart, cap_asc_depart, monte_charge_depart, courette_depart, etage_arrivee, garage_arrivee, cave_arrivee, cap_asc_arrivee, courette_arrivee, monte_charge_arrivee, escale, volume, piano, frigo, supp, distance, formule):

		self.errors = []
		self.etage_depart = etage_depart
		self.garage_depart = garage_depart
		self.cave_depart = cave_depart
		self.cap_asc_depart = cap_asc_depart
		self.monte_charge_depart = monte_charge_depart
		self.courette_depart = courette_depart

		self.etage_arrivee = etage_arrivee
		self.garage_arrivee = garage_arrivee
		self.cave_arrivee= cave_arrivee
		self.cap_asc_arrivee = cap_asc_arrivee
		self.courette_arrivee  = courette_arrivee
		self.monte_charge_arrivee = monte_charge_arrivee
		
		self.escale = escale
		self.volume = volume
		self.piano = piano
		self.frigo = frigo
		self.supp = supp
		self.distance = distance
		self.formule = formule

		self._pTotal = 0


	def is_valid(self):
		""" validate value """
		# check if all attributes are not nontypes:
		
		if not (self.etage_depart.isnumeric() or self.etage_depart in ["-1", "RDC"]):
			self.errors.append("etage_depart is not valid ")
			
		if not self.garage_depart in ["oui", "non"]:
			self.errors.append("garage_depart is not valid ")

		if not self.cave_depart in ["oui", "non"]:
			self.errors.append("cave_depart is not valid ")

		if not self.cap_asc_depart.isnumeric():
			self.errors.append("cap_asc_depart is not valid ")

		if not self.monte_charge_depart in ["oui", "non"]:
			self.errors.append("monte_charge_depart is not valid ")
		
		if not self.courette_depart.isnumeric():
			self.errors.append("courette_depart is not valid ")

		if not (self.etage_arrivee.isnumeric() or self.etage_arrivee in ["-1", "RDC"]):
			self.errors.append("etage_arrivee is not valid ")

		if not self.garage_arrivee in ["oui", "non"]:
			self.errors.append("garage_arrivee is not valid ")

		if not self.cave_arrivee in ["oui", "non"]:
			self.errors.append("cave_arrivee is not valid ")

		if not self.cap_asc_arrivee.isnumeric():
			self.errors.append("cap_asc_arrivee is not valid ")

		if not self.courette_arrivee.isnumeric():
			self.errors.append("courette_arrivee is not valid ")

		if not self.monte_charge_arrivee in ["oui", "non"]:
			self.errors.append("monte_charge_arrivee is not valid ")

		if not self.escale.isnumeric():
			self.errors.append("escale is not valid ")

		if not self.volume.isnumeric():
			self.errors.append("volume is not valid ")

		if not self.piano.isnumeric():
			self.errors.append("piano is not valid ")

		if not self.frigo in ["oui", "non"]:
			self.errors.append("frigo is not valid ")

		if not self.supp.isnumeric():
			self.errors.append("supp is not valid ")

		if not self.distance.isnumeric():
			self.errors.append("distance is not valid ")


		if not self.formule in ["ECO", "STANDARD", "LUXE"]:
			self.errors.append("formule is not valid ")

		return False if self.errors else True


	def calculate(self):

		if not self.is_valid():

			self.errors = append("unable to do calculation, please verify required attributes")
			
			return False

		self.etage_depart = 0 if self.etage_depart == "RDC" else abs(int(self.etage_depart))
		self.garage_depart = 1 if self.garage_depart == "oui" else  0
		self.cave_depart = 1 if self.cave_depart == "oui" else  0
		self.cap_asc_depart = int(self.cap_asc_depart)
		self.monte_charge_depart = 1 if self.monte_charge_depart == "oui" else  0
		self.courette_depart = int(self.courette_depart)

		self.etage_arrivee = 0 if self.etage_arrivee == "RDC" else abs(int(self.etage_arrivee)) 
		self.garage_arrivee = 1 if self.garage_arrivee == "oui" else  0
		self.cave_arrivee = 1 if self.cave_arrivee == "oui" else  0
		self.cap_asc_arrivee = int(self.cap_asc_arrivee)
		self.monte_charge_arrivee = 1 if self.monte_charge_arrivee == "oui" else  0
		self.courette_arrivee = int(self.courette_arrivee)

		self.escale = int(self.escale)
		self.volume = int(self.volume)
		self.piano = int(self.piano)
		self.frigo = 1 if self.frigo == "oui" else  0
		self.supp = int(self.supp)
		self.distance = int(self.distance)
		
		""" the calcul """

		self.cave_garage_total = self.garage_depart + self.cave_depart + self.garage_arrivee + self.cave_arrivee
		self.courette_total = self.courette_depart + self.courette_arrivee
		self.monte_charge_total = self.monte_charge_depart + self.monte_charge_arrivee

		prix_monte_charge = self._prix_monte_charge()
		prix_piano = self._prix_piano()
		prix_cave_garage = self._prix_cave_garage()
		prix_escale_courette = self._prix_escale_courette()
		prix_etage_total = self._prix_etage_total()
		prix_dem = self._prix_dem(self.distance, self.volume)
		prix_km = self._prix_km(self.distance, self.volume)

		self._pTotal = prix_monte_charge + prix_piano + prix_cave_garage + prix_escale_courette + prix_etage_total + prix_dem + prix_km + self._CAMION
		self._tarif_eco = self._pTotal * 1.2 + self.supp
		self._tarif_std = self._tarif_eco * 1.35 + self.supp
		self._tarif_luxe = self._tarif_eco * 1.90 + self.supp

		return True
	
	def _prix_monte_charge (self):
		return self.monte_charge_total * self._MONTE_CH

	def _prix_piano (self,):
		return self.piano  * self._PIANO

	def _prix_cave_garage (self):
		return  self.cave_garage_total * self._GARAGE

	def _prix_escale_courette (self):
		return ((self.escale + self.courette_total) * self._ESCOURETTE)

	def _prix_etage_total (self):
		prix_depart = self._prix_etage(self.etage_depart, self.cap_asc_depart, self.volume)
		prix_arrivee = self._prix_etage(self.etage_arrivee,  self.cap_asc_arrivee, self.volume)
		return (prix_depart + prix_arrivee)

	def _prix_etage (self, etage:int, cap_asc:int, volume:int):
		prix = 0
		if (etage == 1):
			prix = volume * 3 * 1.5
		else:
			prix = volume * 3 * etage

		if (cap_asc > 0):
			prix = prix / (cap_asc * 0.777)

		return prix

	def _prix_dem (self, distance:int, volume:int):
		if (distance < 900):
			return int((distance * 1 * self._DEM * volume) / 8)
		elif ((distance >= 900) and (distance < 1400)):
			return int((distance * 2 * self._DEM * volume) / 8)
		elif ((distance >= 1400) and (distance < 2000)):
			return int((distance * 3 * self._DEM * volume) / 8)
		elif ((distance >= 2000) and (distance < 3000)):
			return int((distance * 4 * self._DEM * volume) / 8)
		else:
			return int((distance * 5 * self._DEM * volume) / 8)

	def _prix_km (self, distance:int, volume:int):
		if (volume < 32):
			return 0.7 * distance
		elif ((volume >= 32) and (volume < 54)):
			return 0.91 * distance
		elif ((volume >= 54) and (volume < 84)):
			return 1.155 * distance
		elif ((volume >= 84) and (volume < 105)):
			return 1.2915 * distance
		else:
			return 1.5225 * distance

	def tarif_ECO (self):
		return round(self._tarif_eco, 2)

	def tarif_STD (self):
		return round(self._tarif_std, 2)

	def tarif_LUXE (self):
		return round(self._tarif_luxe, 2)

	def tarif_TTC (self):
		if (self.formule == "ECO"):
			return round(self._tarif_eco, 2)
		elif (self.formule == "STANDARD"):
			return round(self._tarif_std, 2)
		else:
			return round(self._tarif_luxe, 2)

	def tarif_Arrhes(self):
		return round((self.tarif_TTC() * 30) / 100, 2)

	def tarif_Chargement(self):
		return round((self.tarif_TTC() * 70) / 200, 2)
