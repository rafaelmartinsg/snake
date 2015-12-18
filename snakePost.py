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
from pygame.locals import *

from select import *
from snakeChannel import snakeChannel

#Constantes
LIST_SIZE_MAX = 64
MESSAGE_SECURE =  USEREVENT + 1
class snakePost(snakeChannel):
    def __init__(self):
        super(snakePost, self).__init__() #Appele le constructeur de la classe qu'on hérite
        self.messagesSecure = {} # dictionnaire de host,port qui contient message secure
        pygame.init()
        pygame.time.set_timer(MESSAGE_SECURE, 30)
        self.numSeq = 0

    def envoiNonSecure(self, s, donnees, host):
        #snakeChannel.envoi(s, donnees, host, sequence)
        self.envoi(s, donnees, host, 0)

    def envoiSecure(self, s, donnees, host):
        self.numSeq = ((self.numSeq+1)%2) + 1
        if self.messagesSecure[host] is None:
            self.messagesSecure[host] = [LIST_SIZE_MAX]
            self.messagesSecure[host].append((donnees, self.numSeq))
        elif len(self.messagesSecure) <= LIST_SIZE_MAX:
            #Stock dans une liste de host les messages secures a envoyer
            self.messagesSecure[host].append((donnees, self.numSeq))

    def ackSecureMessage(self, host, donnees, sequence):
        if self.messagesSecure[host].get(0) == (donnees, sequence):
            self.messagesSecure[host].pop(0)


    def receptionPost(self,host,seq,ack,payload):
        if ack == 0:
            pass
        elif ack != 0:
            if ack == self.messagesSecure[host].get(0):
                self.messagesSecure[host].pop(0)
            else:
                return None
        return payload

    def gestionEvennement(self, s):
        continuer = True
        while(continuer):
            for event in pygame.event.get():
                if event.type == MESSAGE_SECURE:
                    #on check dans le dico client si un message secure est a envoyer
                    for key in self.messagesSecure:
                        donnees,seq = self.messagesSecure[key].get(0)
                        self.envoi(s, donnees, key, seq)
                    break
            #Si pas d'evenement, on reste en attente de nouveaux messagess
            snakeChannel.reception(s)
