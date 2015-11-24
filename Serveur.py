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
UDP_NUM_PORT = 6667
BUFFER_SIZE = 4096
PNUM = 19 # meme valeur que dans enonce
SEQUENCE_OUTBAND = 0xffffff

# Declaration de variables globales

class Serveur(snakeChannel):
    def __init__(self, addIp=UDP_ADD_IP, nPort=UDP_NUM_PORT):
        self.clients = {}
        super(Serveur, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        self.addIp = addIp
        self.nPort = nPort
        self.s.bind((self.addIp, self.nPort))

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
            #try:
            print "En attente de clients ..."
            donnees, client = self.reception()
            token = donnees.split()
            print "Serveur recoit : ", donnees

            if (token[0] == "GetToken"):
                # Generation de B de la meme sorte que A
                A = random.randint(0, (1 << 32) - 1)
                #token = donnees.split()
                B = token[1]

                self.envoi("Token " + str(A) + " " + str(B) + " " + str(PNUM), client, SEQUENCE_OUTBAND)
                print "Serveur envoi : Token ", A, " ", B, " ", PNUM

            elif(token[0] == "Connect"):
                separateur = token[1].split('/')
                print "separateur == ", separateur

                # Control de la valeur de B
                if ((len(separateur) < 3) or (int(A) != int(separateur[2]))):
                    print "Suivant...!"
                    continue

                self.envoi("Connected " + str(A), client, SEQUENCE_OUTBAND)
                print "Serveur envoi : Connected ", A
        #except:
            #print "Erreur dans la gestion des messages..."

if __name__=="__main__":
    serv = Serveur()
    serv.gestionMessages()
