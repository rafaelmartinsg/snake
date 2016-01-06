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
import random
import pygame
import struct

from constants import *
from pygame.locals import *
from snakeChannel import snakeChannel

# Constantes
MESSAGE_SECURE = USEREVENT + 1


class snakePost(snakeChannel):
    def __init__(self, canal, ip, port, couleur='', nickname='', udp=False):
        """

        :param canal: continent les donnes a envoyer
        :param ip: contient l'adresse ip du serveur
        :param port: contient le port du serveur
        :param couleur: contient la couleur du joueur
        :param nickname: correspond au nom du joueur
        :param udp: indique si l'on veut communiquer par UDP (avec socket)
        :return:
        """
        super(snakePost, self).__init__(canal, ip, port, couleur, nickname)

        self.messagesSecures = {}   # Contient tous les messages secures a envoyer pour chaque client
        self.messagesNormaux = {}   # Contient tous les messages normaux a envoyer pour chaque client
        self.dernierAck = {}  # Contient la valeur du dernier ack recu par les clients
        self.derniereSeq = {}   # Contient le dernier numero de sequence du client
        self.ackRecus = {}  # Permet d'avoir un ensemble des ack recus afin de pouvoir traites les messages secures
        self.attenteSecureReseau = {}   # Permet de savoir si un client a un message secure sur le reseau

        pygame.init()
        pygame.time.set_timer(MESSAGE_SECURE, 30)
        self.numSeq = 0
        self.commUDP = udp

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

            print "SEQ_NUMBER : " + str(seq) + " - ACK_NUMBER " + str(ack)

            # Message secure --> il faut ack
            if seq != 0 and ack == 0:
                self.ack(seq, canal)

            # Lorsque l'on recoit un ack
            if ack != 0 and len(self.last_seq[canal]) > 0:
                # On le compare avec la valeur de la derniere sequence
                if ack == self.derniereSeq[canal][0]:
                    # Si le ack correspond, on enleve le message de la liste
                    self.messagesSecures[canal].pop(0)
                    self.derniereSeq[canal].pop(0)
                    self.attenteSecureReseau[canal] = False
                    self.ackRecus[canal] = True
                    if seq != 0:
                        self.ack(seq, canal)
                else:
                    if self.udp:
                        self.channel.sendto(self.messagesSecures[canal][0][0], canal)
                    else:
                        self.envoiSnakeChann(self.messagesSecures[canal][0][0], canal)

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
        self.inistialisation(canal)
        if not secure:
            self.messagesNormaux[canal].append((struct.pack('>2H', 0, 0) + donnees, canal))
            # print "[send] Not secure : donnees = ", donnees, " - to : ", canal
        else:
            if len(self.messagesSecures[canal]) < MAX_CLIENT:
                self.last_seq[canal].append(random.randint(1, (1 << 16) - 1))
                self.messagesSecures[canal].append(
                    (struct.pack('>2H', self.last_seq[canal][-1], 0) + donnees, canal))
                print "SEQ_NUMBER : " + str(self.last_seq[canal][-1]) + " - ACK_NUMBER " + str(0)
            else:
                print "Buffer est plein, ..."

    def envoiNonSecure(self, s, donnees, host):
        self.envoi(s, donnees, host, 0)

    def receptionPost(self, host, seq, ack, payload):
        if ack != 0:
            # Si message secure recu et que ack+payload identique a dans liste
            if (ack, payload) == self.messagesSecures[host].get(0):
                self.messagesSecures[host].pop(0)
            # Message bidon, donc on ne fait rien
            else:
                return None
        return payload

    def gestionEvennement(self):
        """

        gestionEvennement est le corps de la gestion des messages en ciruclation mais tout particulierement la gestion
            des acquittements des messages securise. Cette methode gere aussi le fait si on communique via UDP ou via
            le canal.

        :return:
        """
        self.current_time += self.clock.tick(Constants.FPS)
        # On parcoure le dictionnaire de connexions
        for canal in self.connexions:
            if self.attenteSecureReseau.get(canal) and self.attenteSecureReseau[canal] and not self.ackRecus[canal] \
                    and self.ack_timer.expired(self.current_time):
                # Pas de ack recu --> on envoi a nouveau le message
                donnees = self.messagesSecures[canal][0][0]

                if self.commUDP:
                    self.canal.sendto(donnees, canal)
                else:
                    self.envoiSnakeChann(donnees, canal)

            elif self.messagesSecures.get(canal) and self.messagesSecures[canal] \
                    and not self.attenteSecureReseau[canal]:
                donnees = self.messagesSecures[canal][0][0]
                if not self.attenteSecureReseau[canal]:
                    # Attente du ack pour pouvoir envoyer un nouveau message secure
                    self.ackRecus[canal] = False
                    self.attenteSecureReseau[canal] = True

                    if self.commUDP:
                        self.canal.sendto(donnees, canal)
                    else:
                        self.envoiSnakeChann(donnees, canal)
                        print donnees

                    # timer pour les messages securises
                    self.ack_timer.activate(0)
            else:   # message normaux
                if self.messagesNormaux.get(canal) and \
                        self.messagesNormaux[canal]:
                    donnees = self.messagesNormaux[canal].pop(0)[0]

                    if self.commUDP:
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
        if not self.messagesSecures.get(canal):
            self.messagesSecures[canal] = []
        if not self.dernierAck.get(canal):
            self.dernierAck[canal] = None
        if not self.derniereSeq.get(canal):
            self.derniereSeq[canal] = []
        if not self.ackRecus.get(canal):
            self.ackRecus[canal] = None
        if not self.attenteSecureReseau.get(canal):
            self.attenteSecureReseau[canal] = None
