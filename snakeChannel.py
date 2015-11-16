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
#UDP_ADD_IP = "127.0.0.1"
#UDP_NUM_PORT = 7777
BUFFER_SIZE = 4096
#PNUM = 19 # meme valeur que dans enonce
SEQUENCE_OUTBAND = 0xffffff

#class snakeChannel
class snakeChannel:
    def __init__(self, hostSocket):
        self.s = hostSocket
        self.connexions = {}

    def reception(self):
        return self.s.recv(BUFFER_SIZE)

    #
    #   envoi
    #
    #   Parametres  :   - donnees   : continent les donnes a envoyer
    #                   - client    : tuple avec adresse IP et n°port
    #                   - sequence  : utile uniquement pour l'envoi de sequence hors bande
    #
    def envoi(self, donnees, client, sequence):
        # Sequence de connexion
        if (sequence == SEQUENCE_OUTBAND):
            self.connexions[client] = sequence
        elif (sequence == None):
            self.connexions[client] = self.connexions[client] + 1

        # Envoi de donnees au format JSON
        #   cause : le type de string envoye varia a chaque fois et il est donc difficile
        #           de facilement recuperer les donnees envoyer avec unpack.
        #           Avec l'utilisation de JSON, on formate nos envois et facilite la reception
        self.s.sendto(json.dumps({'sequence': self.connexions[client], 'donnees': donnees}), client)
