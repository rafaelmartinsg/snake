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
#   Nom fichier     :   snakeChannel.py
# ##############################################################################
import socket  # Import socket module
import random

# Constantes
UDP_ADD_IP = "127.0.0.1"
UDP_NUM_PORT = 7777
BUFFER_SIZE = 4096
PNUM = 19 # meme valeur que dans enonce
SEQUENCE_OUTBAND = 0xffffff

#class snakeChannel
class snakeChannel:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serveur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addIP = UDP_ADD_IP
        self.nPort = UDP_NUM_PORT


    def client(self):
        self.client.settimeout(10) # definit le timeout
        self.client.connect((self.addIP,self.nPort))
        etat = 0
        A = random.randint(0, (1 << 32) - 1)
        B = 0
        while(etat < 3):
            try:
                if (etat == 0):
                    self.socket.connect((self.addIP, self.nPort))
                    print 'Connexion du client...'
                    self.socket.send("GetToken " + str(A) + " Snake")
                    print "Client envoi : GetToken", A
                    etat += 1
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
                            self.socket.send("Connect /challenge/" + str(B) + "/protocol/" + str(pNum))
                            print "Client envoi : Connect /challenge/", B, "/protocol/", pNum
                            etat += 1
                        else:
                            etat -=1
                            print "Erreur token, retour etat initial (0)"
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
                            etat -=1
                else:
                        print "Une erreur est survenue pendant la connexion du client."
            except:
                print("problème au niveau du client")


    def serveur(self):
            self.serveur.bind((self.addIp, self.nPort))
            self.serveur.connect((self.addIp,self.nPort))
            print 'Serveur ecoute sur le port : ', self.nPort, '...'

        while(True):
            try:
                print "En attente de clients ..."
                donnees = self.serveur.recv(BUFFER_SIZE)
                self.clients[donnees] = 0
                token = donnees.split()
                print "Serveur recoit : ", donnees

                if (token[1] == "GetToken"):
                    # Generation de B de la meme sorte que A
                    B = random.randint(0, (1 << 32) - 1)
                    token = donnees.split()
                    A = token[1]

                    self.socket.send("Token " + str(B) + " " + str(A) + " " + str(PNUM), SEQUENCE_OUTBAND)
                    print "Serveur envoi : Token ", B, " ", A, " ", PNUM

                elif(token[1] == "Connect"):
                    separateur = token[1].split('/')

                    # Control de la valeur de B
                    if ((len(separateur) < 3) or (int(B) != int(separateur[2]))):
                        print "Suivant...!"
                        continue

                    self.socket.send("Connected " + str(B), donnees, SEQUENCE_OUTBAND)
                    print "Serveur envoi : Connected ", B
            except:
                print "Erreur dans la gestion des messages..."


