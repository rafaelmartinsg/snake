#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#  ##############################################################################
#   Auteurs         :   Gerber Cedric
#                       Martins Gomes Rafael
#   Date de debut   :   28 septembre 2015
#   Date de fin     :   XX janvier 2016
#   Etablissement   :   hepia
#   Filiere         :   3eme ITI
#   Cours           :   Reseau I
#
#   Nom fichier     :   Client.py
# ##############################################################################


import socket  # Import socket module
import random

from snakeChannel import snakeChannel

# Constantes
UDP_ADD_IP = "127.0.0.1"
UDP_NUM_PORT = 6667
BUFFER_SIZE = 4096
SEQUENCE_OUTBAND = 0xffffff

# Declaration de variables globales

class Client(snakeChannel):
    #constructeur de la class Client
    def __init__(self):
        super(Client, self).__init__()
        self.sClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addIP = UDP_ADD_IP
        self.nPort = UDP_NUM_PORT

        #super(Client, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        #self.socket.settimeout(10) # definit le timeout
        #self.socket.connect((self.addIP,self.nPort))

    #
    #   connexion est la methode qui permettra au client de se connecter au serveur
    #   Cette methode suit une machine d'etat definie par le cahier des charges de la maniere suivante :
    #       TX  :   0xffffffff (numero de sequence pour initier la connexion)
    #       TX  :   GetToken A Snake (envoi a interval regulier tant que le serveur ne repond pas)
    #       RX  :   Token B A ProtocoleNumber
    #       TX  :   Connect /nom_cles/valeur_cles/.../...
    #       RX  :   Connected B
    #
    def connexion(self):
        self.sClient.connect((self.addIP, self.nPort))
        etatConnexion = False
        print 'Connexion du client...'
        # Tant que la connexion n'est pas etablie
        while not etatConnexion:
            etatConnexion = self.clientConnexion(self.sClient)
        print"Connexion etablie."

        #Envoi des donnees





if __name__=="__main__":
    c = Client()
    c.connexion()
