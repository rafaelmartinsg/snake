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
    def __init__(self, hostSocket):
        self.s = hostSocket
        self.connexions = {}

    def reception(self):
        return self.s.recv(BUFFER_SIZE)

    def envoi(self, data, ipDest, portDest):
        socket.socket.sendto(data, (ipDest, portDest))
        pass
