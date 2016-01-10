#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#  ##############################################################################
#   Auteurs         :   Gerber Cedric
#                       Martins Gomes Rafael
#   Date de debut   :   28 septembre 2015
#   Date de fin     :   10 janvier 2016
#   Etablissement   :   hepia
#   Filiere         :   3eme ITI
#   Cours           :   Reseau I
#
#   Nom fichier     :   snakePost.py
# ##############################################################################
import random
import pygame
import struct


from timer import *
from constants import *
from pygame.locals import *
from snakeChannel import snakeChannel

# Constantes
MESSAGE_fiable = USEREVENT + 1


class snakePost(snakeChannel):
    def __init__(self, canal, ip, port, couleur='', nickname='', udp=False):
        """

        :param canal: continent les donnes a envoyer
        :param ip: contient l'adresse ip du serveur
        :param port: contient le port du serveur
        :param couleur: contient la couleur du joueur
        :param nickname: correspond au nom du joueur
        :param udp: determine le type de communication (udp ou SnackChannel)
        :return:
        """
        super(snakePost, self).__init__(canal, ip, port, couleur, nickname)

        self.messagesFiables = {}   # Contient tous les messages fiables a envoyer pour chaque client
        self.messagesNormaux = {}   # Contient tous les messages normaux a envoyer pour chaque client
        self.dernierAck = {}  # Contient la valeur du dernier ack recu par les clients
        self.derniereSeq = {}   # Contient le dernier numero de sequence du client
        self.ackRecus = {}  # Permet d'avoir un ensemble des ack recus afin de pouvoir traites les messages fiables
        self.attenteFiableReseau = {}   # Permet de savoir si un client a un message fiable sur le reseau

        pygame.init()
        pygame.time.set_timer(MESSAGE_fiable, 30)
        self.numSeq = 0
        self.horloge = pygame.time.Clock()
        self.tempsActuel = 0
        self.timerAck = Timer(INTERVAL_ACK, 0, True)
        self.udp = udp

    def gestionMessages(self, donnees, canal):
        """

        Methode permettant de traiter les messages en circulation dans le canal. Elle gere le cas du message fiable ou
            du message normal a envoyer. Lorsqu'un message fiable est a envoyer, les ack de celui-ci sont egalement
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

            # Message fiable --> il faut ack
            if seq != 0:
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

        Methode qui met le serveur en ecoute de nouveaux messages via la fonction "serveurConnexion" (snakeChannel).
        Lors de la reception d'un nouveau message, on fait appel a la fonction "gestionMessages" afin de traiter le
            nouveau contenu recu.
        :return None, None: dans le cas ou les donnees ou le canal sont incorrects
        :return payload, canal: donnes a envoyer et sur quel canal on communique
        """
        donnees, canal = self.serveurConnexion()
        if donnees is None and canal is None:
            return None, None
        else:
            payload = self.gestionMessages(donnees, canal)
            return payload, canal

    def envoiSnakePost(self, donnees, canal, fiable=False):
        """

        Methode qui permet l'envoi des messages. Les messages dit "normaux" sont stockes dans un dictionnaire. Les
            messages dit "fiables" sont aussi stockes dans un dictionnaire ayant une taille fixee. Si le dictionnaire
            des messages fiables est plein, un message d'avertissement est envoye au joueur. Avant toute chose, on
            initialise chaque dictionnaire. Au moment de stocker le message dans le dictionnaire, on pack le numero de
            sequence, on le concatène avec les donnees et on le stock sous forme de tuple avec l'adresse du destinataire

        :param donnees: contient les donness a traiter
        :param canal: continent les donnes a envoyer
        :param fiable: indique le type de message
        :return:
        """
        self.initialisation(canal)
        if fiable:
            if len(self.messagesFiables[canal]) < MAX_CLIENT:
                self.derniereSeq[canal].append(random.randint(1, (1 << 16) - 1))
                self.messagesFiables[canal].append(
                    (struct.pack('>2H', self.derniereSeq[canal][-1], 0) + donnees, canal))
            else:
                print "Buffer est plein, ..."
        else:
            self.messagesNormaux[canal].append((struct.pack('>2H', 0, 0) + donnees, canal))

    def receptionPost(self, host, seq, ack, payload):
        """

        :param host: emetteur du message
        :param seq: contient le numero de sequence
        :param ack: contient le numero d'ack
        :param payload: contient les donnees du message
        :return payload: donnees du message
        :return None: Si reception d'un message bidon
        """
        if ack != 0:
            # Si message fiable recu et que ack+payload identique a dans liste
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
                if self.udp:
                        self.canal.sendto(donnees, canal)
                else:
                    self.envoiSnakeChann(donnees, canal)

            elif self.messagesFiables.get(canal) and not self.attenteFiableReseau[canal]:
                donnees = self.messagesFiables[canal][0][0]
                if not self.attenteFiableReseau[canal]:
                    # Attente du ack pour pouvoir envoyer un nouveau message fiable
                    self.ackRecus[canal] = False
                    self.attenteFiableReseau[canal] = True
                    if self.udp:
                        self.canal.sendto(donnees, canal)
                    else:
                        self.envoiSnakeChann(donnees, canal)
                    # timer pour les messages securises
                    self.timerAck.activate(0)
            else:   # message normaux
                if self.messagesNormaux.get(canal):
                    donnees = self.messagesNormaux[canal].pop(0)[0]
                    if self.udp:
                        self.canal.sendto(donnees, canal)
                    else:
                        self.envoiSnakeChann(donnees, canal)

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
        """

        Methode permettant d'envoyer un ack pour le message fiable sur le canal
        :param sequence: contient le n°sequence a ack
        :param canal: destinataire du message
        :return:
        """
        pack = struct.pack('>2H', 0, sequence)
        # Si message a ack et qu'aucun message fiable ne circule sur le reseau
        if self.messagesFiables.get(canal) and not self.attenteFiableReseau.get(canal):
            # message fiable
            pack = struct.pack('>2H', self.derniereSeq[canal][0], sequence)
            pack += self.messagesFiables[canal][0][0]
            self.attenteFiableReseau[canal] = True
            self.ackRecus[canal] = False
        elif self.messagesNormaux.get(canal):
            # Message non fiable
            pack += self.messagesNormaux[canal].pop(0)[0]

        if self.udp:
            self.canal.sendto(pack, canal)
        else:
            self.envoiSnakeChann(pack, canal)
