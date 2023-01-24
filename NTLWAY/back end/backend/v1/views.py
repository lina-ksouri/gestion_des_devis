from django.shortcuts import render
from django.contrib.auth.models import User
from django.template import response
from django.template.loader import render_to_string
from django.http import Http404, HttpResponse, FileResponse
from django.core.files import File
import requests
from requests.structures import CaseInsensitiveDict
from requests.sessions import Request

from rest_framework import viewsets, status, generics, exceptions
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_pdf.response import PDFFileResponse

from wsgiref.util import FileWrapper

from .serializers import *
#from .models import Account

#partie ajoute
from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from v1.models import Devis
from v1.serializers import DevisSerializer
from django.http import QueryDict

from pprint import pprint
from base64 import b64decode, b64encode
import sys
import os
import io
from .utils import Gmail, DevisUtils, Formule, LettreUtils

from django.core.files.storage import FileSystemStorage
from reportlab.pdfgen import canvas

#
# User Management
#

class Register(APIView):
	
	permission_classes = (IsAuthenticated,)
	
	def post(self, request, format=None):
		serializer = RegisterSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairView(TokenObtainPairView):
		 serializer_class = MyTokenObtainPairSerializer


class ListUser(APIView):

	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		userSet = User.objects.exclude(username = 'admin')
		serializer = UserSerializer(userSet, many=True)
		return Response(serializer.data)

class CurrentUser(APIView):
	
	permission_classes = (IsAuthenticated,)
	
	def get(self, request):
		serializer = UserSerializer(request.user)
		return Response(serializer.data)

class UserDetail(APIView):

	#permission_classes = (IsAuthenticated,)

	def get_object(self, pk):
		try:
			return User.objects.get(pk=pk)
		except User.DoesNotExist:
			raise Http404


	def get(self, request, pk, format=None):
		userSet = User.objects.filter(id=pk)
		serializer = UserSerializer(userSet, many=True)
		return Response(serializer.data)

	def post(self, request, pk, format=None):
		userSet = self.get_object(pk)
		serializer = UserUpdateSerializer(userSet, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDelete(APIView):

	permission_classes = (IsAuthenticated,)

	def get_object(self, pk):
		try:
			return User.objects.get(pk=pk)
		except User.DoesNotExist:
			raise Http404

	def post(self, request, pk, format=None):
		userSet = self.get_object(pk)
		#serializer = UserUpdateSerializer(userSet, data=request.data)
		userSet.delete()
		return Response({'deleted user': pk})
	

class ChangePassword(APIView):

	permission_classes = (IsAuthenticated,)

	def get_object(self, pk):
		try:
			return User.objects.get(pk=pk)
		except User.DoesNotExist:
			raise Http404

	def post(self, request, pk, format=None):
		userSet = self.get_object(pk)
		serializer = ChangePasswordSerializer(userSet, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'updated user password': pk})
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
# Devis
#

 # afficher  liste des devis ou creer new devis
class ListDevis(APIView):
    
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
         devisSet = Devis.objects.all()
         serializer = DevisSerializer(devisSet, many=True)
         return Response(serializer.data)
	def post(self, request, format=None):

		d=request.data
		
		d._mutable=True     

		d['belongs_to']= request.user.id
		
		d['namebelongs_to'] = request.user.username
        
		c =list(d.keys())

		for i in c:
			if (d[i]=="undefined"):
				del(d[i])
		
		
		serializer = DevisSerializer(data=d)
        
		if serializer.is_valid():
         
			 serializer.save()
			 
			 return Response(serializer.data, status=status.HTTP_201_CREATED)
        
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			 
			 

			 

		
#ajouter et afficher un devis avec numdevis		
class DevisDetail(APIView):
   
	permission_classes = (IsAuthenticated,)
     
	def get_object(self, pk):
         try:
             return Devis.objects.get(pk=pk)
         except Devis.DoesNotExist:
             raise Http404

	def get_username(self,pk):
    		
			userset = User.objects.get(id=pk)
			
			return userset.email
    
	def get(self, request, pk, format=None):
         deviss = self.get_object(pk)
         serializer = DevisSerializer(deviss)
         return Response(serializer.data)
    
	def post(self, request, pk, format=None):
         
		deviss = self.get_object(pk)
		

		d = request.data
		#d._mutable = True  
		d['belongs_to']= request.user.id
		d['namebelongs_to'] = request.user.username
        
		ch = "Prénom :" + d['prenom'] + "\nNom : " + d['nom'] + " \nE-mail : " + d['mail'] + "\nMobile :" +d['tel']
		
		CRMData = {'amount': d['prix_ttc'] , 'title' : pk ,  'description' : ch ,'estimated_closing_date' : d['date_dem'] }
		
		username = self.get_username(request.user.id)

		
		r1= requests.get('https://ntlway-2.nocrm.io/api/v2/auth/log_as?user_id='+str(username),
		headers={"X-API-KEY":"fa368e319744b177feadd77111fc3f0c99810d0e0417bed2"})
		 
		user_token = r1.json()['token']
		
		r=requests.put('https://ntlway-2.nocrm.io/api/v2/leads/'+str(deviss.id_CRM),
		headers={"X-USER-TOKEN":str(user_token)},params= CRMData) 
		serializer = DevisSerializer(deviss, d)


		if serializer.is_valid():
         
		     serializer.save()
         
		     return JsonResponse(serializer.data)
         
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#l'api Statut devis 
class DevisStatus(APIView):
   
	permission_classes = (IsAuthenticated,)
     
	def get_status(self, pk):
         try:
             return Devis.objects.get(pk=pk)
         except Devis.DoesNotExist:
             raise Http404
			    
	def get(self, request, pk, format=None): 
		 deviss = self.get_status(pk)
		 serializer = DevisStatutSerializer(deviss)
		 return Response(serializer.data)

    
	def post(self, request, pk, format=None):
         
		 deviss = self.get_status(pk)

		 d = request.data
		 
		 d._mutable = True  #backend erreur 'dict' object has no attribute '_mutable'  par contre pour que modification Status frontend travaille il faut ajouter ce ligne 

		 
		 d['belongs_to']= request.user.id
		 d['namebelongs_to'] = request.user.username
         
		 serializer = DevisStatutSerializer(deviss, d)

		 if serializer.is_valid():
         
		     serializer.save()
         
		     return JsonResponse(serializer.data)
         

		 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#envoi du devis vers noCRM
class DevisSendCRM(APIView):
    		
	permission_classes = (IsAuthenticated,)

	def get_object(self, pk):
         try:
             return Devis.objects.get(pk=pk)
         except Devis.DoesNotExist:
             raise Http404

	def get_username(self,pk):
    		
			userset = User.objects.get(id=pk)
			
			return userset.email

	def get(self, request, pk, format=None):
         
		 deviss = self.get_object(pk)
         
		 serializer = DevisSerializer(deviss)
         
		 if serializer.data['id_CRM'] != -1:
    			 return Response({"message":"devis existe"}, status=status.HTTP_404_NOT_FOUND)
		 
		 ch = ''
         
		 CRMData = {}
		
		 if 'prenom' in serializer.data:
    				ch = "Prénom :" + str(serializer.data['prenom']) 
		
		 if 'nom' in serializer.data:
    				ch = ch +  "\nNom : " + str(serializer.data['nom'])
    	
		 if 'mail' in serializer.data:
    				ch = ch + " \nE-mail : " + str(serializer.data['mail']) 
    	
		 if 'tel' in serializer.data:
    				ch = ch +  "\n Télephone :" +str(serializer.data['tel'])
			 
		 CRMData['title'] = serializer.data['num_devis']
         
		
		 if ch :
    				CRMData['description'] = ch
         
		 username = self.get_username(request.user.id)
		 #print(username)
		 r1= requests.get('https://ntlway-2.nocrm.io/api/v2/auth/log_as?user_id='+str(username),
		 headers={"X-API-KEY":"fa368e319744b177feadd77111fc3f0c99810d0e0417bed2"})
		 
		 user_token = r1.json()['token']
		 
		 
		 r=requests.post('https://ntlway-2.nocrm.io/api/v2/leads',headers={"X-USER-TOKEN": str(user_token) },params= CRMData) 
			
		 dd={}

		 dd['id_CRM']=r.json()['id']
		 dd['num_devis']= serializer.data['num_devis']
		 dd['id_mail']	 =serializer.data['id_mail']
			
		 deviss = Devis.objects.get(  pk= dd['num_devis'])
		 ser = DevisSerializer(deviss, dd)
		 if not ser.is_valid():
    			 print (ser.errors)

		 if ser.is_valid():
    			
				ser.save()
			    
				return Response(ser.data, status=status.HTTP_201_CREATED)
        
		 return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

#Télecharger devis 
class DevisDownload(APIView):
    
	def get(self, request, pk, format=None):

		# get the devis data from db
		#deviss = Devis.objects.filter(id=pk,belongs_to=request.user.id)
		deviss = Devis.objects.filter(num_devis=pk)
		serializer = DevisSerializer(deviss, many=True)
		if not deviss:
			return Response({"message":"file not found "}, status=status.HTTP_404_NOT_FOUND)

		serializer = DevisSerializer(deviss, many=True)
		devis_data = json.loads(json.dumps(serializer.data))[0]

		#devis_page1_filename = "devis_"+str(devis_data['num_devis'])
		devis_page1_filename = "devis_x_"+str(devis_data['num_devis'])
		
		# class DevisUtils to manage generating and sending devis
		
		utils = DevisUtils(data=devis_data,file_basename=devis_page1_filename)
		# generate html from template
		generated_devis_filename = utils.generate_devis()
		

		fs = FileSystemStorage(str(os.path.dirname(os.path.abspath(__file__)))+"/common")
		
		response = FileResponse(open(generated_devis_filename, 'rb'), content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename='+str(generated_devis_filename)
		
		# delete the devis after response 
		utils.delete_file(generated_devis_filename)
		return response

#Télecharger lettre de voiture (Siwar) 
class LettreDownload(APIView):
	
	def get(self, request, pk, format=None):
		
		deviss = Devis.objects.filter(num_devis=pk)
		
		serializer = DevisSerializer(deviss, many=True)
		
		if not deviss:
			return Response({"message":"file not found"}, status=status.HTTP_404_NOT_FOUND)
		

		serializer = DevisSerializer(deviss, many=True)
		devis_data = json.loads(json.dumps(serializer.data))[0]

		lettre_de_voiture_filename = "lettre_"+str(devis_data['num_devis'])
		
		# class LettreUtils to manage generating and sending devis
		
		utils = LettreUtils(data=devis_data,file_basename=lettre_de_voiture_filename)
		
		generated_lettre_filename = utils.generate_lettre()
		# generate html from template

		fs = FileSystemStorage(str(os.path.dirname(os.path.abspath(__file__)))+"/common")
		
		response = FileResponse(open(generated_lettre_filename, 'rb'), content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename='+str(generated_lettre_filename)
		
		# delete the devis after response 
		utils.delete_file(generated_lettre_filename)
		return response


class DevisSend(APIView):
	permission_classes = (IsAuthenticated,)
	def get(self, request, pk, format=None):
		
		#deviss = Devis.objects.filter(id=pk,belongs_to=request.user.id)
		deviss = Devis.objects.filter(num_devis=pk)

		#deviss = Devis.objects.filter(id=pk)
		serializer = DevisSerializer(deviss, many=True)
		if not deviss:
			return Response({"message":"file not found"}, status=status.HTTP_404_NOT_FOUND)

		serializer = DevisSerializer(deviss, many=True)
		devis_data = json.loads(json.dumps(serializer.data))[0]
		
		#devis_page1_filename = "devis_"+"_"+str(devis_data['id'])
		devis_page1_filename = "devis_"+str(devis_data['num_devis'])+str(devis_data['belongs_to'])
		
		# class DevisUtils to manage generating and sending devis
		
		utils = DevisUtils(data=devis_data,file_basename=devis_page1_filename)
		generated_devis_filename = utils.generate_devis()

		account = User.objects.get(username=request.user.username)
		sender_email = account.username
		sender_password = b64decode(account.password.encode('ascii')).decode('ascii')

		receiver_email = devis_data['mail']
		try:

			utils.send_devis(sender_email=sender_email, sender_password=sender_password, receiver_email=receiver_email)
			#utils.delete_file(generated_devis_filename)
			return Response({"message": "devis has been sent successfully to "+str(receiver_email)},status=status.HTTP_200_OK)
		
		except:
			return Response({"message": "unable to send devis"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DevisCalculate(APIView):


	def post(self, request, format=None):
		serializer = DevisCalculateSerializer(data=request.data)
		if serializer.is_valid():
			etage_depart = serializer.data.get('etage_depart')
			garage_depart = serializer.data.get('garage_depart')
			cave_depart = serializer.data.get('cave_depart')
			garage_arrivee = serializer.data.get('garage_arrivee')
			cave_arrivee = serializer.data.get('cave_arrivee')
			cap_asc_depart = serializer.data.get('cap_ascenseur_depart')
			courette_depart = serializer.data.get('courette_depart')
			courette_arrivee = serializer.data.get('courette_arrivee')
			monte_charge_depart = serializer.data.get('monte_charge_depart')
			monte_charge_arrivee = serializer.data.get('monte_charge_arrivee')
			etage_arrivee = serializer.data.get('etage_arrivee')
			cap_asc_arrivee = serializer.data.get('cap_ascenseur_arrivee')
			
			volume = serializer.data.get('volume')
			piano = serializer.data.get('nb_piano')
			frigo = serializer.data.get('frigo')
			escale = serializer.data.get('nb_escale')
			
			supp = serializer.data.get('supplements')
			distance = serializer.data.get('distance')
			formule = serializer.data.get('formule')
			
			tarif = Formule(etage_depart, garage_depart, cave_depart, cap_asc_depart, monte_charge_depart, courette_depart, etage_arrivee, garage_arrivee, cave_arrivee, cap_asc_arrivee, courette_arrivee, monte_charge_arrivee, escale, volume, piano, frigo, supp, distance, formule)
			if tarif.is_valid():
				tarif.calculate()
				prix_eco = tarif.tarif_ECO()
				prix_std = tarif.tarif_STD()
				prix_premium = tarif.tarif_LUXE()
				prix_ttc = tarif.tarif_TTC()
				arrhes = tarif.tarif_Arrhes()
				chargement = tarif.tarif_Chargement()
				livraison = tarif.tarif_Chargement()
				return Response(
					{
						"prix_eco": prix_eco,
						"prix_std": prix_std,
						"prix_premium": prix_premium,
						"prix_ttc": prix_ttc,
						"arrhes": arrhes,
						"chargement": chargement,
						"livraison": livraison
					}, 
					status=status.HTTP_200_OK
				)

			return Response({"errors":tarif.errors}, status=status.HTTP_400_BAD_REQUEST)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# archived
class DevisRefreshback(APIView):
	permission_classes = (IsAuthenticated,)
	
	def get(self, request, format=None):
		
		# get username and password from database 

		account = User.objects.get(username=request.user.username)

		# refresh database with the script before listing
		username = account.username
		decrypted_password = b64decode(account.password.encode('ascii')).decode('ascii')

		gmail = Gmail(username,decrypted_password)
		search_criteria = "FROM"

		search_value = "contact@lesartisansdemenageurs.fr"
		list_mails = gmail.fetch_messages(search_criteria,search_value)		
		for mail in list_mails:
			if not mail['messages']:
				continue
			mail_data = {
				"id_mail": mail['id'],
				"expediteur": str(mail['from']),
				"objet": str(mail.get('subject')),
				'id_devis': str(mail['id']),
				'prenom': str(mail['messages']['client'].get('Prénom')),
				'nom':str(mail['messages']['client'].get('Nom')),
				'mail': str(mail['messages']['client'].get('Adresse email')),
				'tel': str(mail['messages']['client'].get('Téléphone fixe')),

				'rue_depart': str(mail['messages']['departure'].get('Adresse')),
				'code_postal_depart': str(mail['messages']['departure'].get('Code Postal')),
				'pays_depart': str(mail['messages']['departure'].get('Pays')),
				'ville_depart': str(mail['messages']['departure'].get('Ville')),
				'surface_depart': str(mail['messages']['departure'].get('Surface en m2')),
				
				'rue_arrivee': str(mail['messages']['arrival'].get('Adresse')),
				'code_postal_arrivee': str(mail['messages']['arrival'].get('Code Postal')),
				'pays_arrivee': str(mail['messages']['arrival'].get('Pays')),
				'ville_arrivee': str(mail['messages']['arrival'].get('Ville')),
				
				'date_dem': str(mail['messages']['additional'].get('Date de déménagement')),
				'volume': str(mail['messages']['additional'].get('Estimation du volume')),
				'commentaires': str(mail['messages']['additional'].get('Commentaires')),
				#'belongs_to': request.user.id
			}


			# create a mail object 

			devis_serializer = DevisSerializer(data=mail_data)
			devis_serializer.is_valid()
			if devis_serializer.is_valid():
				#snippets = Devis.objects.filter(id_mail=mail_data.get("id_mail"),belongs_to=request.user.id)
				snippets = Devis.objects.filter(id_mail=mail_data.get("id_mail"))
				if len(snippets) == 0:
					devis_serializer.save()

			
		

			# create mail data object

		#snippets = Devis.objects.filter(belongs_to=request.user.id)
		snippets = Devis.objects.all()
		serializer = DevisSerializer(snippets, many=True)
		return Response(serializer.data)


class DevisRefresh(APIView):
	permission_classes = (IsAuthenticated,)
	
	def get(self, request, format=None):
		
		# get username and password from database 

		# account = User.objects.get(username="source")

		# refresh database with the script before listing
		username = "nassim.devis@gmail.com"
		password = "ntlnassim_parsing321."
		#decrypted_password = b64decode(password.encode('ascii')).decode('ascii')
		gmail = Gmail(username,password)
		search_criteria = "FROM"
		#search_value = "contact@lesartisansdemenageurs.fr"
		search_value = "talelkrimi2015@gmail.com"

		# get mails id already parsed in database
		print("Getting list of mail IDs from database...")
		parsed_mails_id = list(Devis.objects.values_list('id_mail',flat=True))
	
		# get all messages id from gmail
		print("Getting all mail IDs from inbox...")
		messages_id = gmail.get_messages_ids(search_criteria,search_value)

		for msg_id in messages_id:
			
			# check if the msg_id exists in the database before proceeding

			if int(msg_id) in parsed_mails_id:
				continue

			data = gmail.fetch_mail_data_by_id(msg_id)

			if not data['messages']:
				continue

			print("fetching : " + data.get('subject'))
			mail_data = {
				"id_mail": data['id'],
				"expediteur": str(data['from']),
				"objet": str(data.get('subject')),
				'prenom': str(data['messages']['client'].get('Prénom')),
				'nom':str(data['messages']['client'].get('Nom')),
				'mail': str(data['messages']['client'].get('Adresse email')),
				'tel': str(data['messages']['client'].get('Téléphone fixe')),
				'rue_depart': str(data['messages']['departure'].get('Adresse')),
				'code_postal_depart': str(data['messages']['departure'].get('Code Postal')),
				'pays_depart': str(data['messages']['departure'].get('Pays')),
				'ville_depart': str(data['messages']['departure'].get('Ville')),
				'surface_depart': str(data['messages']['departure'].get('Surface en m2')),
				
				'rue_arrivee': str(data['messages']['arrival'].get('Adresse')),
				'code_postal_arrivee': str(data['messages']['arrival'].get('Code Postal')),
				'pays_arrivee': str(data['messages']['arrival'].get('Pays')),
				'ville_arrivee': str(data['messages']['arrival'].get('Ville')),
				
				'date_dem': str(data['messages']['additional'].get('Date de déménagement')),
				'volume': str(data['messages']['additional'].get('Estimation du volume')),
				'commentaires': str(data['messages']['additional'].get('Commentaires')),
			}


			# create a mail object 

			devis_serializer = DevisSerializer(data=mail_data)
			if devis_serializer.is_valid():
				deviss = Devis.objects.filter(id_mail=mail_data.get("id"))
				if len(deviss) == 0:
					devis_serializer.save()
			else:
				print(devis_serializer.errors)
		
		print("Returning All deviss data from databases ....")
		# return mail data object
		devisSet = Devis.objects.all()
		serializer = DevisSerializer(devisSet, many=True)
		return Response(serializer.data)