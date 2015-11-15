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
#   Nom fichier     :   Serveur.py
# ##############################################################################

import socket
import random

from snakeChannel import snakeChannel

# Constantes
MAX_CLIENT = 10
UDP_ADD_IP = "127.0.0.1"
UDP_NUM_PORT = 6666
BUFFER_SIZE = 4096
PNUM = 19 # meme valeur que dans enonce
SEQUENCE_OUTBAND = 0xffffff

# Declaration de variables globales

class Serveur:
    def __init__(self, addIp=UDP_ADD_IP, nPort=UDP_NUM_PORT):
        self.clients = {}
        #self.outputs = [] a voir si nécessaire
        self.serveur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addIp = addIp
        self.nPort = nPort
        self.serveur.bind((self.addIp, self.nPort))
        self.connect()
        print 'Serveur ecoute sur le port : ', self.nPort, '...'

    #
    #   gestionMessage est la methode qui s'occupe des messages recus et ceux que le serveur doit envoyer
    #   Les messages sont definit par le cahier des charges selon la manière suivante :
    #       RX  :   0xffffffff (numero de sequence pour initier la connexion)
    #       RX  :   GetToken A Snake
    #       TX  :   Token B A ProtocoleNumber
    #       RX  :   Connect /nom_cles/valeur_cles/.../...
    #       TX  :   Connected B
    #
    def gestionMessages(self):
        while(True):
            try:
                print "En attente de clients ..."
                donnees = self.serveur.recv()
                self.clients[donnees] = 0
                token = donnees.split()
                print "Serveur recoit : ", donnees

                if (token[1] == "GetToken"):
                    # Generation de B de la meme sorte que A
                    B = random.randint(0, (1 << 32) - 1)
                    token = donnees.split()
                    A = token[1]

                    self.serveur.send("Token " + str(B) + " " + str(A) + " " + str(PNUM), SEQUENCE_OUTBAND)
                    print "Serveur envoi : Token ", B, " ", A, " ", PNUM

                elif(token[1] == "Connect"):
                    separateur = token[1].split('/')

                    # Control de la valeur de B
                    if ((len(separateur) < 3) or (int(B) != int(separateur[2]))):
                        print "Suivant...!"
                        continue

                    self.serveur.send("Connected " + str(B), donnees, SEQUENCE_OUTBAND)
                    print "Serveur envoi : Connected ", B
            except:
                print "Erreur dans la gestion des messages..."