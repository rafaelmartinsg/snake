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
import sys

import random
import pygame
import struct


from timer import *
from constants import *
from pygame.locals import *
from snakeChannel import snakeChannel

# Constantes
MESSAGE_SECURE = USEREVENT + 1


class snakePost(snakeChannel):
    def __init__(self, canal, ip, port, couleur='', nickname=''):
        """

        :param canal: continent les donnes a envoyer
        :param ip: contient l'adresse ip du serveur
        :param port: contient le port du serveur
        :param couleur: contient la couleur du joueur
        :param nickname: correspond au nom du joueur
        :return:
        """
        super(snakePost, self).__init__(canal, ip, port, couleur, nickname)

        self.messagesFiables = {}   # Contient tous les messages secures a envoyer pour chaque client
        self.messagesNormaux = {}   # Contient tous les messages normaux a envoyer pour chaque client
        self.dernierAck = {}  # Contient la valeur du dernier ack recu par les clients
        self.derniereSeq = {}   # Contient le dernier numero de sequence du client
        self.ackRecus = {}  # Permet d'avoir un ensemble des ack recus afin de pouvoir traites les messages secures
        self.attenteFiableReseau = {}   # Permet de savoir si un client a un message secure sur le reseau

        pygame.init()
        pygame.time.set_timer(MESSAGE_SECURE, 30)
        self.numSeq = 0
        self.horloge = pygame.time.Clock()
        self.tempsActuel = 0
        self.timerAck = Timer(INTERVAL_ACK, 0, True)

    def gestionMessages(self, donnees, canal):
        """

        Methode permettant de traiter les messages en circulation dans le canal. Elle gere le cas du message secure ou
            du message normal a envoyer. Lorsqu'un message secure est a envoyer, les ack de celui-ci sont egalement
            geres. A la reception du message, on separe le numero de sequence et la valeur du ack afin de savoir quel
            type de message nous traitons.

        :param donnees: contient les donness a traiter
        :param canal: continent les donnes a envoyer
        :return None: dans le cas ou les donnees sont incorrectes
        :return payload: dans le cas d'un message a envoyer
        """
        # Si on recoit des donnees
        if donnees is not None and len(donnees) >= 4:
            seq = struct.unpack('>H', donnees[:2])[0]
            ack = struct.unpack('>H', donnees[2:4])[0]

            # Message secure --> il faut ack
            if seq != 0 :
                self.ack(seq, canal)

            # Lorsque l'on recoit un ack
            if ack != 0 and len(self.derniereSeq[canal]) > 0:
                # On le compare avec la valeur de la derniere sequence
                if ack == self.derniereSeq[canal][0]:
                    # Si le ack correspond, on enleve le message de la liste
                    self.messagesFiables[canal].pop(0)
                    self.derniereSeq[canal].pop(0)
                    self.attenteFiableReseau[canal] = False
                    self.ackRecus[canal] = True
                    if seq != 0:
                        self.ack(seq, canal)
                else:
                    self.envoiSnakeChann(self.messagesFiables[canal][0][0], canal)

            if len(donnees[4:]) == 0:
                return None
            else:
                # On retourne le payload
                return donnees[4:]
        else:
            return None

    def ecouteServeur(self):
        """

        Methode qui met le serveur en ecoute de nouveaux messages. via la fonction "serveurConnexion" (snakeChannel)

        Lors de la reception d'un nouveau message, on fait appel a la fonction "gestionMessages" afin de traiter le
            nouveau contenu recu.

        A la reception du message, on separe le numero de sequence et la valeur du ack afin de savoir quel
            type de message nous traitons.

        :return None, None: dans le cas ou les donnees ou le canal sont incorrects
        :return payload, canal: donnes a envoyer et sur quel canal on communique
        """
        donnees, canal = self.serveurConnexion()
        if donnees is not None and canal is not None:
            payload = self.gestionMessages(donnees, canal)
            return payload, canal
        else:
            return None, None

    def envoiSnakePost(self, donnees, canal, secure=False):
        """

        Methode qui permet l'envoi des messages. Les messages dit "normaux" sont stockes dans un dictionnaire. Les
            messages dit "securises" sont aussi stockes dans un dictionnaire ayant une taille fixee. Si le dictionnaire
            des messages securises est plein, un message d'avertissement est envoye au joueur. Avant toute chose, on
            initialise chaque dictionnaire.

        Lors de la reception d'un nouveau message, on fait appel a la fonction "gestionMessages" afin de traiter le
            nouveau contenu recu.

        A la reception du message, on separe le numero de sequence et la valeur du ack afin de savoir quel
            type de message nous traitons.

        :pagitram donnees: contient les donness a traiter
        :param canal: continent les donnes a envoyer
        :param secure: indique le type de message
        :return:
        """
        self.initialisation(canal)
        if not secure:
            self.messagesNormaux[canal].append((struct.pack('>2H', 0, 0) + donnees, canal))
        else:
            if len(self.messagesFiables[canal]) < MAX_CLIENT:
                self.derniereSeq[canal].append(random.randint(1, (1 << 16) - 1))
                self.messagesFiables[canal].append(
                    (struct.pack('>2H', self.derniereSeq[canal][-1], 0) + donnees, canal))
            else:
                print "Buffer est plein, ..."

    def receptionPost(self, host, seq, ack, payload):
        if ack != 0:
            # Si message secure recu et que ack+payload identique a dans liste
            if (ack, payload) == self.messagesFiables[host].get(0):
                self.messagesFiables[host].pop(0)
            # Message bidon, donc on ne fait rien
            else:
                return None
        return payload

    def ecouteClient(self):
        """

        Methode qui met le serveur en ecoute de nouveaux messages. via la fonction "serveurConnexion" (snakeChannel)

        Lors de la reception d'un nouveau message, on fait appel a la fonction "gestionMessages" afin de traiter le
            nouveau contenu recu.

        A la reception du message, on separe le numero de sequence et la valeur du ack afin de savoir quel
            type de message nous traitons.

        :return None, None: dans le cas ou les donnees ou le canal sont incorrects
        :return payload, canal: donnes a envoyer et sur quel canal on communique
        """
        donnees, canal = self.receptionSnakeChann()
        payload = self.gestionMessages(donnees, canal)
        return payload, canal

    def gestionEvennement(self):
        """

        gestionEvennement est le corps de la gestion des messages en ciruclation mais tout particulierement la gestion
            des acquittements des messages securise. Cette methode gere aussi le fait si on communique via UDP ou via
            le canal.

        :return:
        """
        self.tempsActuel += self.horloge.tick(Constants.FPS)
        # On parcoure le dictionnaire de connexions
        for canal in self.connexions:
            if self.attenteFiableReseau.get(canal) and self.timerAck.expired(self.tempsActuel):
                # Pas de ack recu --> on envoi a nouveau le message
                donnees = self.messagesFiables[canal][0][0]
                self.envoiSnakeChann(donnees, canal)

            elif self.messagesFiables.get(canal) and not self.attenteFiableReseau[canal]:
                donnees = self.messagesFiables[canal][0][0]
                if not self.attenteFiableReseau[canal]:
                    # Attente du ack pour pouvoir envoyer un nouveau message secure
                    self.ackRecus[canal] = False
                    self.attenteFiableReseau[canal] = True
                    self.envoiSnakeChann(donnees, canal)

                    # timer pour les messages securises
                    self.timerAck.activate(0)
            else:   # message normaux
                if self.messagesNormaux.get(canal):
                    donnees = self.messagesNormaux[canal].pop(0)[0]
                    self.envoiSnakeChann(donnees, canal)   # sa sent le rouci

    def initialisation(self, canal):
        """

        Methode qui initialise chaque dictionnaire pour un canal donne

        :param canal: contient le canal de communication
        :return:
        """
        if not self.messagesNormaux.get(canal):
            self.messagesNormaux[canal] = []
        if not self.messagesFiables.get(canal):
            self.messagesFiables[canal] = []
        if not self.dernierAck.get(canal):
            self.dernierAck[canal] = None
        if not self.derniereSeq.get(canal):
            self.derniereSeq[canal] = []
        if not self.ackRecus.get(canal):
            self.ackRecus[canal] = None
        if not self.attenteFiableReseau.get(canal):
            self.attenteFiableReseau[canal] = None

    def ack(self, sequence, canal):
        """Send an ack

        :param numSeq: sequence number
        :param canal: destination
        :return:
        """
        pack = struct.pack('>2H', 0, sequence)
        # When sending the ack, send data with the ack, if any
        if self.messagesFiables.get(canal) and \
                not self.attenteFiableReseau.get(canal):
            # Secure message
            # Set a random numSeq
            pack = struct.pack('>2H', self.derniereSeq[canal][0], sequence)
            pack += self.messagesFiables[canal][0][0]
            self.attenteFiableReseau[canal] = True
            self.ackRecus[canal] = False
        elif self.messagesNormaux.get(canal):
            # Normal message
            pack += self.messagesNormaux[canal].pop(0)[0]

        self.envoiSnakeChann(pack, canal)
