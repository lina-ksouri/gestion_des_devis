##################################################
## Class Formule to compute all needed operations
##################################################
## Author: Nassim TLILI
## Copyright: Copyright 2021, {NTLParse}
## Version: v1.1
##################################################

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


	def is_valid(self,debug=False):
		""" validate value """

		if not (self.etage_depart.isnumeric() or self.etage_depart in ["-1", "RDC"]):
			if debug == True:
				print("etage_depart is not valid ")
			return False
			
		if not self.garage_depart in ["oui", "non"]:
			if debug == True:
				print("garage_depart is not valid ")
			return False

		if not self.cave_depart in ["oui", "non"]:
			if debug == True:
				print("cave_depart is not valid ")
			return False

		if not self.cap_asc_depart.isnumeric():
			if debug == True:
				print("cap_asc_depart is not valid ")
			return False
		
		if not self.monte_charge_depart in ["oui", "non"]:
			if debug == True:
				print("monte_charge_depart is not valid ")
			return False
		
		if not self.courette_depart.isnumeric():
			if debug == True:
				print("courette_depart is not valid ")
			return False



		if not (self.etage_arrivee.isnumeric() or self.etage_arrivee == "RDC"):
			if debug == True:
				print("etage_arrivee is not valid ")
			return False
		
		if not self.garage_arrivee in ["oui", "non"]:
			if debug == True:
				print("garage_arrivee is not valid ")
			return False

		if not self.cave_arrivee in ["oui", "non"]:
			if debug == True:
				print("cave_arrivee is not valid ")
			return False

		if not self.cap_asc_arrivee.isnumeric():
			if debug == True:
				print("cap_asc_arrivee is not valid ")
			return False
		
		if not self.courette_arrivee.isnumeric():
			if debug == True:
				print("courette_arrivee is not valid ")
			return False

		if not self.monte_charge_arrivee in ["oui", "non"]:
			if debug == True:
				print("monte_charge_arrivee is not valid ")
			return False

		
		if not self.escale.isnumeric():
			if debug == True:
				print("escale is not valid ")
			return False

		if not self.volume.isnumeric():
			if debug == True:
				print("volume is not valid ")
			return False

		if not self.piano.isnumeric():
			if debug == True:
				print("piano is not valid ")
			return False

		if not self.frigo in ["oui", "non"]:
			if debug == True:
				print("frigo is not valid ")
			return False

		if not self.supp.isnumeric():
			if debug == True:
				print("supp is not valid ")
			return False

		if not self.distance.isnumeric():
			if debug == True:
				print("distance is not valid ")
			return False

		if not self.formule in ["ECO", "STANDARD", "LUXE"]:
			if debug == True:
				print("formule is not valid ")
			return False

		return True

	def calculate(self):

		if not self.is_valid(True):
			print("unable to do calculation, please verify required attributes")
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


validated_data = {
        "etage_depart": "1",
        "garage_depart": "oui",
        "cave_depart": "non",
        "cap_ascenseur_depart": "2",
        "courette_depart": "2",
        "monte_charge_depart": "oui",
        "etage_arrivee": "3",
        "garage_arrivee": "non",
        "cave_arrivee": "non",
        "cap_ascenseur_arrivee": "4",
        "courette_arrivee": "0",
        "monte_charge_arrivee": "non",
        "formule": "STANDARD",
        "surface": "",
        "volume": "50",
        "nb_piano": "1",
        "frigo": "non",
        "nb_escale": "1",
        "supplements": "30",
        "distance": "20",
        "prix_ttc": "",
        "prix_eco": "",
        "prix_std": "",
        "prix_premium": "",
        "arrhes": "",
        "chargement": "",
        "livraison": ""
    }

etage_depart = validated_data.get('etage_depart')
garage_depart = validated_data.get('garage_depart')
cave_depart = validated_data.get('cave_depart')
garage_arrivee = validated_data.get('garage_arrivee')
cave_arrivee = validated_data.get('cave_arrivee')
cap_asc_depart = validated_data.get('cap_ascenseur_depart')
courette_depart = validated_data.get('courette_depart')
courette_arrivee = validated_data.get('courette_arrivee')
monte_charge_depart = validated_data.get('monte_charge_depart')
monte_charge_arrivee = validated_data.get('monte_charge_arrivee')
etage_arrivee = validated_data.get('etage_arrivee')
cap_asc_arrivee = validated_data.get('cap_ascenseur_arrivee')
volume = validated_data.get('volume')
piano = validated_data.get('nb_piano')
frigo = validated_data.get('frigo')
escale = validated_data.get('nb_escale')
supp = validated_data.get('supplements')
distance = validated_data.get('distance')
formule = validated_data.get('formule')




tarif = Formule(
	etage_depart=etage_depart,
	garage_depart=garage_depart ,
	cave_depart=cave_depart,
	cap_asc_depart=cap_asc_depart ,
	monte_charge_depart=monte_charge_depart ,
	courette_depart=courette_depart ,
	
	etage_arrivee=etage_arrivee,
	garage_arrivee=garage_arrivee ,
	cave_arrivee=cave_arrivee,
	cap_asc_arrivee=cap_asc_arrivee,
	monte_charge_arrivee=monte_charge_arrivee,
	courette_arrivee=courette_arrivee ,
	
	piano=piano,
	frigo=frigo,
	escale=escale,
	supp=supp, 
	volume=volume,
	distance=distance,
	formule=formule
	)


if tarif.calculate():
	print(tarif.tarif_ECO())
	print(tarif.tarif_STD())
	print(tarif.tarif_LUXE())
	print(tarif.tarif_TTC())
	print(tarif.tarif_Arrhes())
	print(tarif.tarif_Chargement())
else:
	print ("erreur calcul")
