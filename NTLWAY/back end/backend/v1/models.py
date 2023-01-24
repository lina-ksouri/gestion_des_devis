from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser
from django.db.models.fields import AutoField, DateField
from django.forms import widgets
import datetime
from rest_framework.fields import ChoiceField

from rest_framework.utils.serializer_helpers import ReturnList
STATUS_CHOICES = (
    ("NOUVEAU", "NOUVEAU"),
    ("interessé", "interessé"),
    ("rejeté", "rejeté"),
    ("confirmé", "confirmé")
    ) 
BOX2_CHOICES = (
    ("STANDARD","STANDARD"),
    ("CONFORT","CONFORT"),
    ("LUXE","LUXE")
)
#class Account(models.Model):
    #password = models.CharField(max_length=60)
    #username = models.EmailField(unique=True)

    #def __str__(self):
        #return str(self.username)

def increment():
    last_devis = Devis.objects.all().order_by('num_devis').last()
    if not last_devis :
        return ('Haya_'+str(datetime.date.today().year)+'_00000')
    devis_id = last_devis.num_devis
    devis_id = int(devis_id[10:])+1
    devis_id = '0'*(5-len(str(devis_id)))+str(devis_id)
    return ('Haya_'+str(datetime.date.today().year)+'_'+devis_id)
def increment1():
    last_devis = Devis.objects.all().order_by('num_lettre').last()
    if not last_devis :
        return ('LV_'+str(datetime.date.today().year)+'_00000')
    devis_id = last_devis.num_devis
    devis_id = int(devis_id[10:])+1
    devis_id = '0'*(5-len(str(devis_id)))+str(devis_id)
    return ('LV_'+str(datetime.date.today().year)+'_'+devis_id)

class Devis(models.Model):
    num_devis = models.CharField(max_length=60,default=increment,blank=True,primary_key=True)
    id_mail = models.IntegerField(default=0)  
    id_CRM = models.IntegerField(blank=True,null=True,default=-1)   # `id` int(11) NOT NULL,
    expediteur = models.CharField(max_length=60,default=None,blank=True,null=True)
    objet = models.CharField(max_length=255,default=None,blank=True,null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='NOUVEAU',blank=True,null=True)
    modified_in = models.DateTimeField(auto_now= True, blank = True)    #date de la derniere modification
    belongs_to = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,default=1)   #clé etrangere
    namebelongs_to = models.CharField(max_length=255,blank=True)
    num_lettre = models.CharField(max_length=60,default=increment1,blank=True,unique=True)

    # info perso
    nom = models.CharField(max_length=60,default=None,blank=True,null=True)
    prenom = models.CharField(max_length=60,default=None,blank=True,null=True)
    mail = models.CharField(max_length=60,default=None,blank=True,null=True)
    tel = models.CharField(max_length=60,default=None,blank=True,null=True)

    # adresse_depart 
    
    code_postal_depart = models.CharField(max_length=60,default=None,blank=True,null=True)
    pays_depart = models.CharField(max_length=60,default=None,blank=True,null=True)
    ville_depart = models.CharField(max_length=60,default=None,blank=True,null=True)
    rue_depart = models.TextField(default=None,blank=True,null=True)
    etage_depart = models.CharField(max_length=60,default=None,blank=True,null=True) # `étage` int(11) DEFAULT NULL,
    acces_depart = models.CharField(max_length=60,default=None,blank=True,null=True) # `accès` varchar(20) DEFAULT NULL,
    isGarage_depart = models.BooleanField(default=False,blank=True,null=True)
    garage_depart = models.CharField(max_length=60,default=None,blank=True,null=True) # `garage` tinyint(1) DEFAULT NULL,
    isCave_depart = models.BooleanField(default=False,blank=True,null=True)
    cave_depart = models.CharField(max_length=60,default=None,blank=True,null=True)  # `cave` tinyint(1) DEFAULT NULL,
    cap_ascenseur_depart = models.CharField(max_length=60,default="sans ascenseur",blank=True,null=True) # `cap_ascenseur` tinyint(4) DEFAULT NULL,
    isCourette_depart = models.BooleanField(default=False,blank=True,null=True)
    courette_depart = models.CharField(max_length=60,default=None,blank=True,null=True) # `courette` tinyint(4) DEFAULT NULL,
    isEscal_depart =  models.BooleanField(default=False,blank=True,null=True)
    address_escale_depart =  models.CharField(max_length=60,default=None,blank=True,null=True)
    isMonte_charge_depart =  models.BooleanField(default=False,blank=True,null=True)
    # adresse arrivee

    code_postal_arrivee = models.CharField(max_length=60,default=None,blank=True,null=True)
    pays_arrivee = models.CharField(max_length=60,default=None,blank=True,null=True)
    ville_arrivee = models.CharField(max_length=60,default=None,blank=True,null=True)
    rue_arrivee = models.TextField(default=None,blank=True,null=True)
    etage_arrivee = models.CharField(max_length=60,default=None,blank=True,null=True) # `étage` int(11) DEFAULT NULL,
    acces_arrivee = models.CharField(max_length=60,default=None,blank=True,null=True) # `accès` varchar(20) DEFAULT NULL,
    isGarage_arrivee = models.BooleanField(default=False,blank=True,null=True)
    garage_arrivee = models.CharField(max_length=60,default=None,blank=True,null=True) # `garage` tinyint(1) DEFAULT NULL,
    isCave_arrivee =  models.BooleanField(default=False,blank=True,null=True)
    cave_arrivee = models.CharField(max_length=60,default=None,blank=True,null=True)  # `cave` tinyint(1) DEFAULT NULL,
    cap_ascenseur_arrivee = models.CharField(max_length=60,default="sans ascenseur",blank=True,null=True) # `cap_ascenseur` tinyint(4) DEFAULT NULL,
    isCourette_arrivee =  models.BooleanField(default=False,blank=True,null=True)
    courette_arrivee = models.CharField(max_length=60,default=None,blank=True,null=True) # `courette` tinyint(4) DEFAULT NULL,
    isEscal_arrivee =  models.BooleanField(default=False,blank=True,null=True)
    address_escale_arrivee =  models.CharField(max_length=60,default=None,blank=True,null=True)
    isMonte_charge_arrivee =  models.BooleanField(default=False,blank=True,null=True)
    
    # info generale 
    date_dem = models.CharField(max_length=60,blank=True) #`date_dem` date NOT NULL,
    date_liv = models.DateField(default=datetime.date.today)
    date_crea_devis = models.DateField(default=datetime.date.today)
    isProvisoir = models.BooleanField(default=False,blank=True,null=True)
    formule = models.CharField(max_length=20,choices=BOX2_CHOICES,default='STANDARD',blank=True,null=True) # `formule` varchar(11) NOT NULL, # (1, 'ECO') (2, 'STANDARD') (3, 'PREMIUM');
    surface = models.CharField(max_length=60,default=None,blank=True,null=True)
    volume = models.CharField(max_length=60,default="20",blank=True,null=True) #`volume` int(11) NOT NULL, 
    isPiano = models.BooleanField(default=False,blank=True,null=True)
    nb_piano = models.CharField(max_length=60,default=None,blank=True,null=True) # `poid_piano` varchar(11) DEFAULT NULL,  # (1, 'moins de 120 kg'), (2, 'entre 120 et 200 kg'), (3, 'plus de 200 kg');
    type_piano = models.CharField(max_length=60,default=None,blank=True,null=True) 
    poid_piano = models.CharField(max_length=60,default=None,blank=True,null=True)
    isMoto =  models.BooleanField(default=False,blank=True,null=True)
    nb_moto = models.CharField(max_length=60,default=None,blank=True,null=True)
    info_moto = models.CharField(max_length=60,default=None,blank=True,null=True)
    isCoffre_fort =  models.BooleanField(default=False,blank=True,null=True)
    nb_coffre_fort = models.CharField(max_length=60,default=None,blank=True,null=True)
    poids_coffre_fort = models.CharField(max_length=60,default=None,blank=True,null=True)
    isGardinage =  models.BooleanField(default=False,blank=True,null=True)
    nb_gardinage = models.CharField(max_length=60,default=None,blank=True,null=True)
    isObjet_sp = models.BooleanField(default=False,blank=True,null=True)
    objet_sp=models.CharField(max_length=60,default=None,blank=True,null=True)
    frigo = models.CharField(max_length=60,default=None,blank=True,null=True)
    fournisseur = models.CharField(max_length=60,default=None,blank=True,null=True)
    commentaires = models.TextField(default=None,blank=True,null=True) #`commentaire` text DEFAULT NULL
    
    
    # tarifs

    supplements = models.CharField(max_length=60,default=None,blank=True,null=True)
    distance = models.CharField(max_length=60,default=None,blank=True,null=True) #`distance` float NOT NULL,
    prix_ttc = models.CharField(max_length=60,default="0",blank=True,null=True) #`prix_ttc` float NOT NULL, # not found in mail
    prix_confort = models.CharField(max_length=60,default="0",blank=True,null=True) # `prix_eco` float NOT NULL, # not found in mail
    prix_standard = models.CharField(max_length=60,default="0",blank=True,null=True) # `prix_std` float NOT NULL, # not found in mail
    prix_luxe = models.CharField(max_length=60,default="0",blank=True,null=True) # `prix_premium` float NOT NULL, # not found in mail
    arrhes = models.CharField(max_length=60,default="0",blank=True,null=True) # `arrhes` float NOT NULL,
    chargement = models.CharField(max_length=60,default="0",blank=True,null=True)
    livraison =  models.CharField(max_length=60,default="0",blank=True,null=True)



    


    def __str__(self):
        return str(self.objet)
    