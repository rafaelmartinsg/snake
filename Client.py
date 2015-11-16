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
UDP_NUM_PORT = 7777
BUFFER_SIZE = 4096
SEQUENCE_OUTBAND = 0xffffff

# Declaration de variables globales

class Client(snakeChannel):
    #constructeur de la class Client
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addIP = UDP_ADD_IP
        self.nPort = UDP_NUM_PORT
        self.socket.settimeout(10) # definit le timeout
        self.socket.connect((self.addIP,self.nPort))

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
        etat = 0
        A = random.randint(0, (1 << 32) - 1)
        B = 0
        while (etat < 3):
            try:
                # Si etat 0
                if (etat == 0):
                    self.socket.connect((self.addIP, self.nPort))
                    print 'Connexion du client...'
                    self.envoi("GetToken " + str(A) + " Snake", (self.addIP, self.nPort), SEQUENCE_OUTBAND)
                    print "Client envoi : GetToken", A
                    etat += 1
                # Si etat 1
                elif (etat == 1):
                    controlToken = self.socket.recv(BUFFER_SIZE)
                    print "Client recoit : ", controlToken
                    if (controlToken is None):
                        etat -= 1
                    else:
                        token = controlToken.split()
                        # Controle du A recu
                        if (token[2] == A):
                            B = token[1]
                            pNum = token[3]
                            self.envoi("Connect /challenge/" + str(B) + "/protocol/" + str(pNum), (self.addIP, self.nPort), None)
                            #self.socket.send("Connect /challenge/" + str(B) + "/protocol/" + str(pNum))
                            print "Client envoi : Connect /challenge/", B, "/protocol/", pNum
                            etat += 1
                        else:
                            etat = 0
                            print "Erreur token, retour etat initial (0)"
                # Si etat 3
                elif (etat == 2):
                    controlConnexion = self.socket.recv(BUFFER_SIZE)
                    print "Client recoit : ", controlConnexion
                    if controlConnexion is None:
                        # Si connexion pas acquitee, on revient a l'etat precedent
                        etat -= 1
                    else:
                        token = controlConnexion.split()
                        if B == token[1]:
                            etat += 1
                else:
                    print "Une erreur est survenue pendant la connexion du client."
            except:
                print("problème au niveau du client")