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
import json

# Constantes
MAX_CLIENT = 10
UDP_ADD_IP = "127.0.0.1"
UDP_NUM_PORT = 6667
BUFFER_SIZE = 4096
PNUM = 19 # meme valeur que dans enonce
SEQUENCE_OUTBAND = 0xffffff

#class snakeChannel
class snakeChannel(object):
    def __init__(self):
        #self.s = hostSocket
        self.connexions = {}
        self.host = (UDP_ADD_IP, UDP_NUM_PORT)


    def clientConnexion(self,s):
        etat = 0
        A = random.randint(0, (1 << 32) - 1)
        B = 0
        while (etat < 3):
            #try:
            # Si etat 0
            if (etat == 0):
                self.envoi(s, "GetToken " + str(A) + " Snake", (UDP_ADD_IP, UDP_NUM_PORT), SEQUENCE_OUTBAND)
                print "Client envoi : GetToken", A
                etat += 1
            # Si etat 1
            elif (etat == 1):
                controlToken, client  = self.reception(s)
                print "Client recoit : ", controlToken
                if (controlToken is None):
                    etat -= 1
                else:
                    token = controlToken.split()
                    # Controle du A recu
                    if (token[2] == str(A)):
                        B = token[1]
                        pNum = token[3]
                        self.envoi(s, 'Connect /challenge/' + str(B) + '/protocol/' + str(pNum), self.host, SEQUENCE_OUTBAND)
                        print 'Client envoi : Connect /challenge/', B, '/protocol/', pNum
                        etat += 1
                    else:
                        etat = 0
                        print "Erreur token, retour etat initial (0)"
            # Si etat 3
            elif (etat == 2):
                controlConnexion, client = self.reception(s)
                print "Client recoit : ", controlConnexion
                if controlConnexion is None:
                    # Si connexion pas acquitee, on revient a l'etat precedent
                    etat -= 1
                else:
                    token = controlConnexion.split()
                    print B
                    if B == token[1]:
                        etat += 1
                        return True
            else:
                print "Une erreur est survenue pendant la connexion du client."
                return False
            #except:
                #print("problème au niveau du client")


    def serveurConnexion(self, s, serveur):
        clients = {}

        print 'Serveur ecoute sur le port : ', self.nPort, '...'
        while(True):
            #try:
            print "En attente de clients ..."
            donnees, client = self.reception(s)
            token = donnees.split()
            print "Serveur recoit : ", donnees

            if (token[0] == "GetToken"):
                # Generation de B de la meme sorte que A
                A = random.randint(0, (1 << 32) - 1)
                #token = donnees.split()
                B = token[1]

                self.envoi(s, "Token " + str(A) + " " + str(B) + " " + str(PNUM), client, SEQUENCE_OUTBAND)
                print "Serveur envoi : Token ", A, " ", B, " ", PNUM

            elif(token[0] == "Connect"):
                separateur = token[1].split('/')
                print "separateur == ", separateur

                # Control de la valeur de B
                if ((len(separateur) < 3) or (int(A) != int(separateur[2]))):
                    print "Suivant...!"
                    continue

                self.envoi(s, "Connected " + str(A), client, SEQUENCE_OUTBAND)
                print "Serveur envoi : Connected ", A
        #except:
            #print "Erreur dans la gestion des messages..."


    def reception(self, s):
        #try:
        donnees, client = s.recvfrom(BUFFER_SIZE)
        donneesJSon = json.loads(donnees)
        NumeroSequence, payload = donneesJSon['sequence'], donneesJSon['donnees']
        #self.connexions[client] = 0

        if (self.connexions.get(client) is None):
        #if (self.connexions[client] == None):
            self.connexions[client] = SEQUENCE_OUTBAND

        if ((NumeroSequence == SEQUENCE_OUTBAND) or
            (self.connexions[client] < NumeroSequence)):
            return payload, client

        #except socket.error:
            #print "Erreur de communication via le socket"
            #pass

        return None, None

    #
    #   envoi
    #
    #   Parametres  :   - donnees   : continent les donnes a envoyer
    #                   - client    : tuple avec adresse IP et n°port
    #                   - sequence  : utile uniquement pour l'envoi de sequence hors bande
    #
    def envoi(self, s, donnees, host, sequence):

        # Sequence de connexion
        if (sequence == SEQUENCE_OUTBAND):
            self.connexions[host] = sequence
        elif (sequence == None):
            print"test sequence == none"
            self.connexions[host]= 0
            self.connexions[host] = (self.connexions[host] + 1)

        # Envoi de donnees au format JSON
        #   cause : le type de string envoye varia a chaque fois et il est donc difficile
        #           de facilement recuperer les donnees envoyer avec unpack.
        #           Avec l'utilisation de JSON, on formate nos envois et facilite la reception
        s.sendto(json.dumps({'sequence': self.connexions[host], 'donnees': donnees}), host)
