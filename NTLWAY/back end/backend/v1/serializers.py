from django.db.models import fields
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from .models import Devis

import datetime as dt
import json
import imaplib

from base64 import b64decode, b64encode
from .utils import Gmail

#
# User
#
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
   
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['username'] = user.username
        return token

class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'role')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
        #extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if (attrs['role'] != "Collaborateur") and (attrs['role'] != "Admin"):
            raise serializers.ValidationError({"role": "Invalid role"})
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        group = Group.objects.get(name=validated_data['role']) 
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        group.user_set.add(user)

        return user

#class AccountSerializer(serializers.ModelSerializer):
    #class Meta:
        #model = Account
        #fields = ['username','password']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField('get_role_from_group')
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role','is_active']

    def get_role_from_group(self, obj):
            l = obj.groups.values_list('name',flat = True)          # QuerySet Object
            l_as_list = list(l)                                    # QuerySet to `list`
            if len(l_as_list) > 0:
                return l_as_list[0]
            else:
                return "none"

class UserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role','is_active']

    def validate(self, attrs):
        if (attrs['role'] != "Collaborateur") and (attrs['role'] != "Admin"):
            raise serializers.ValidationError({"role": "Invalid role"})
        return attrs

    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        instance.is_active = validated_data['is_active']
        group_id = 2
        if validated_data['role']=="Admin":
            group_id = 1

        instance.groups.set([group_id])
        instance.save()

        return instance

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    # def validate_old_password(self, value):
    #     user = self.context['request'].user
    #     if not user.check_password(value):
    #         raise serializers.ValidationError({"old_password": "Old password is not correct"})
    #     return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance

#
# Devis
#

class DevisStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devis

        fields = [
        'num_devis',
        'status',
        'modified_in',
        'belongs_to',
        'namebelongs_to'
        ]
  
        
class DevisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devis

        fields = [
        'num_devis',
        'id_mail',
        'id_CRM',
        'expediteur',
        'objet',
        'status',
        'modified_in',
        'belongs_to',
        'namebelongs_to',
        'num_lettre',
        

        
        'nom',
        'prenom',
        'mail',
        'tel',
        
        'code_postal_depart',
        'pays_depart',
        'ville_depart',
        'rue_depart',
        'etage_depart',
        'acces_depart',
        'isGarage_depart',
        'garage_depart',
        'isCave_depart',
        'cave_depart',
        'cap_ascenseur_depart',
        'isCourette_depart',
        'courette_depart',
        'isEscal_depart',
        'address_escale_depart',
        'isMonte_charge_depart',
        
        'code_postal_arrivee',
        'pays_arrivee',
        'ville_arrivee',
        'rue_arrivee',
        'etage_arrivee',
        'acces_arrivee',
        'isGarage_arrivee',
        'garage_arrivee',
        'isCave_arrivee',
        'cave_arrivee',
        'cap_ascenseur_arrivee',
        'isCourette_arrivee',
        'courette_arrivee',
        'isEscal_arrivee',
        'address_escale_arrivee',
        'isMonte_charge_arrivee',
        
        # info generale
        'date_dem',
        'date_liv',
        'date_crea_devis',
        'isProvisoir',
        'formule',
        'surface',
        'volume',
        'isPiano',
        'nb_piano',
        'type_piano',
        'poid_piano',
        'isMoto',
        'nb_moto',
        'info_moto',
        'isCoffre_fort',
        'nb_coffre_fort',
        'poids_coffre_fort',
        'isGardinage',
        'nb_gardinage',
        'isObjet_sp',
        'objet_sp',
        'frigo',
        'fournisseur',
        'commentaires',
        
        # tarifs
        'supplements',
        'distance',
        'prix_ttc',
        'prix_confort',
        'prix_standard',
        'prix_luxe',
        'arrhes',
        'chargement',
        'livraison',
        
        
        ]

class DevisDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
    
        model = Devis
        fields = [
            'num_devis',
        #'id',
        'id_mail',
        'expediteur',
        'objet',
        'status',

        'nom',
        'prenom',
        'mail',
        'tel',

        'code_postal_depart',
        'pays_depart',
        'ville_depart',
        'rue_depart',
        'etage_depart',
        'acces_depart',
        'garage_depart',
        'cave_depart',
        'cap_ascenseur_depart',
        'courette_depart',
        'monte_charge_depart',

        'code_postal_arrivee',
        'pays_arrivee',
        'ville_arrivee',
        'rue_arrivee',
        'etage_arrivee',
        'acces_arrivee',
        'garage_arrivee',
        'cave_arrivee',
        'cap_ascenseur_arrivee',
        'courette_arrivee',
        'monte_charge_arrivee',

        # info generale
        'date_dem',
        'formule',
        'surface',
        'volume',
        'nb_piano',
        'frigo',
        'nb_escale',
        'address_escale',
        'type_client',
        'commentaires',

        # tarifs
        'supplements',
        'distance',
        'prix_ttc',
        'prix_eco',
        'prix_std',
        'prix_premium',
        'arrhes',
        'chargement',
        'livraison',

        #'belongs_to'
        ]

class DevisUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Devis
        fields = [
        'num_devis',
        #'id',
        'expediteur',
        'objet',

        'nom',
        'prenom',
        'mail',
        'tel',

        'code_postal_depart',
        'pays_depart',
        'ville_depart',
        'rue_depart',
        'etage_depart',
        'acces_depart',
        'garage_depart',
        'cave_depart',
        'cap_ascenseur_depart',
        'courette_depart',
        'monte_charge_depart',

        'code_postal_arrivee',
        'pays_arrivee',
        'ville_arrivee',
        'rue_arrivee',
        'etage_arrivee',
        'acces_arrivee',
        'garage_arrivee',
        'cave_arrivee',
        'cap_ascenseur_arrivee',
        'courette_arrivee',
        'monte_charge_arrivee',

        # info generale
        'date_dem',
        'formule',
        'surface',
        'volume',
        'nb_piano',
        'frigo',
        'nb_escale',
        'address_escale',
        'type_client',
        'commentaires',

        # tarifs
        'supplements',
        'distance',
        'prix_ttc',
        'prix_eco',
        'prix_std',
        'prix_premium',
        'arrhes',
        'chargement',
        'livraison',

        ]

class DevisCalculateSerializer(serializers.Serializer):

    etage_depart = serializers.CharField(max_length=200,allow_blank =True)
    garage_depart = serializers.CharField(max_length=200,allow_blank =True)
    cave_depart = serializers.CharField(max_length=200,allow_blank =True)
    cap_ascenseur_depart = serializers.CharField(max_length=200,allow_blank =True)
    courette_depart = serializers.CharField(max_length=200,allow_blank =True)
    monte_charge_depart = serializers.CharField(max_length=200,allow_blank =True)

    etage_arrivee = serializers.CharField(max_length=200,allow_blank =True)
    garage_arrivee = serializers.CharField(max_length=200,allow_blank =True)
    cave_arrivee = serializers.CharField(max_length=200,allow_blank =True)
    cap_ascenseur_arrivee = serializers.CharField(max_length=200,allow_blank =True)
    courette_arrivee = serializers.CharField(max_length=200,allow_blank =True)
    monte_charge_arrivee = serializers.CharField(max_length=200,allow_blank =True)

    # info generale
    formule = serializers.CharField(max_length=200,allow_blank =True)
    #surface = serializers.CharField(max_length=200,allow_blank =True)
    volume = serializers.CharField(max_length=200,allow_blank =True)
    nb_piano = serializers.CharField(max_length=200,allow_blank =True)
    frigo = serializers.CharField(max_length=200,allow_blank =True)
    nb_escale = serializers.CharField(max_length=200,allow_blank =True)
    supplements = serializers.CharField(max_length=200,allow_blank =True)
    distance = serializers.CharField(max_length=200,allow_blank =True)
