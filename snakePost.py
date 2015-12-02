#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#  ##############################################################################
#   Auteurs         :   Gerber Cedric
#                       Martins Gomes Rafael
#   Date de debut   :   28 septembre 2015
#   Date de fin     :   04 janvier 2016
#   Etablissement   :   hepia
#   Filiere         :   3eme ITI
#   Cours           :   Reseau I
#
#   Nom fichier     :   snakePost.py
# ##############################################################################
import socket  # Import socket module
import random
import json
import pygame

from select import *

from snakeChannel import snakeChannel

class snakePost(snakeChannel):
    def __init__(self):
        self.messagesSecure = {}
        self.pygame.init()
        self.pygame.time.set_timer("MESSAGE_SECURE", 30)

    def envoiNonSecure(self, s, donnees, host, sequence):
        snakeChannel.envoi(s, donnees, host, sequence)

    def envoiSecure(self, s, donnees, host, sequence):
        if self.messagesSecure[host] is None:
            self.messagesSecure[host] = []
            self.messagesSecure[host].append((donnees, sequence))
        else:
            #Stock dans une liste de host les messages secures a envoyer
            self.messagesSecure[host].append((donnees, sequence))

    def Ack(self, host, donnees, sequence):
        if self.messagesSecure[host].get(0) == (donnees, sequence):
            self.messagesSecure[host].pop(0)

    def gestionEvennement(self, s):
        continuer = True
        while(continuer):
            for event in pygame.event.get():
                if event.type == "MESSAGE_SECURE":
                    for key in self.messagesSecure:
                        donnees,seq = self.messagesSecure[key].get(0)
                        snakeChannel.envoi(self, s, donnees, key, seq)
                    break
                    #on check dans le dico client si un message secure est a envoyer

                    pass
                #Si pas d'evenement
                else:
                    #On reste en attente de nouveaux messages et on les traites
                    snakeChannel.reception(s)
                    pass
