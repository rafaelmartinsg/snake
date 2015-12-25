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
#   Nom fichier     :   Serveur.py
# ##############################################################################

import socket
import random

from snakeChannel import snakeChannel
from snakePost import snakePost

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
        super(Serveur, self).__init__()
        self.clients = {}
        self.listFood = []
        self.listPlayersInfo = []
        self.snakesDico = {}
        self.sServeur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addIp = addIp
        self.nPort = nPort
        self.sServeur.bind((self.addIp, self.nPort))
        #super(Serveur, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
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
            self.serveurConnexion(self.sServeur, (self.addIp, self.nPort))

    #Methode pour les messages food, listFood => liste avec toute les coordonnées des pommes
    def msgFood(self):
        #formatage des données en JSON
        #Envoie securisé a tout les clients la liste des pommes
        pass

    #envoie la liste des positions du corps de tout les snakes dans la partie, préfixées par l'identifiant
    #du joueur. snakesDico => dicitonnaire nom du joueur, position
    def msgSnakes(self):
        #formatage des données en JSON
        #envoie non fiable
        pass

    #msg contenant toute les infos des joueurs: nom du joueur, sa couleur, son score, ready ou pas
    #listPlayersInfo => liste contenant toute les infos
    def msgPlayers_info(self):
        #formatage JSON
        #envoie fiable
        pass

    #Contient le nom du joueur qui a perdu et qui doit recommencer depuis le debut
    def msgGame_over(nomJoueur):
        #formatage JSON
        #envoie fiable
        pass

    #previens un joueur qu'il est rentrer dans une pomme
    def msgGrow(nomJoueur):
        #formatage JSON
        #envoie fiable
        pass


if __name__=="__main__":
    serv = Serveur()
    serv.gestionMessages()
