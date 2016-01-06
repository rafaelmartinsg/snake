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
FPS = 60


class snakePost(snakeChannel):
    def __init__(self, channel, ip, port, color='', nickname='', udp=False):
        # Appelle le constructeur de la classe qu'on hérite
        super(snakePost, self).__init__(channel, ip, port, color, nickname)

        self.messagesSecures = {} # Contient tous les messages secures a envoyer pour chaque client
        self.messagesNormaux = {} # Contient tous les messages normaux a envoyer pour chaque client
        self.last_ack = {}  # Contient la valeur du dernier ack recu par les clients
        self.last_seq = {}  # Contient le dernier numero de sequence du client
        self.ackRecus = {} # Permet d'avoir un ensemble des ack recus afin de pouvoir traites les messages secures
        self.attenteSecureReseau = {} # Permet de savoir si un client a un message secure sur le reseau

        pygame.init()
        pygame.time.set_timer(MESSAGE_SECURE, 30)
        self.numSeq = 0
        self.commUDP = udp

    def gestionMessages(self, donnees, canal):
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
                # Compare the ack with the last seq
                if ack == self.last_seq[canal][0]:
                    # If the ack is correct, remove the secure message from the list
                    self.messagesSecures[canal].pop(0)
                    self.last_seq[canal].pop(0)
                    self.attenteSecureReseau[canal] = False
                    self.ackRecus[canal] = True
                    if seq != 0:
                        self.ack(seq, canal)
                else:
                    if self.udp:  # on udp
                        self.channel.sendto(self.messagesSecures[canal][0][0], canal)
                    else:  # on snake_channel
                        self.envoiSnakeChann(self.messagesSecures[canal][0][0], canal)

            if len(donnees[4:]) == 0:
                return None
            else:
                return donnees[4:]  # Return the payload
        else:
            return None
        
    def ecouteServeur(self):
        donnees, canal = self.serveurConnexion()
        if donnees is not None and canal is not None:
            payload = self.gestionMessages(donnees, canal)
            return payload, canal
        else:
            return None, None
    
    def envoiSnakePost(self, donnees, canal, secure=False):
        self.initialisation(canal)
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

    def gestionEvennement(self, s):
        #s =True
        continuer = True
        while(continuer):
            for event in pygame.event.get():
                if event.type == MESSAGE_SECURE:
                    # on check dans le dico client si un message secure est a envoyer
                    for key in self.messagesSecures:
                        donnees, seq = self.messagesSecures[key].get(0)
                        self.envoiNonSecure(s, donnees, key)
                    break
            # Si pas d'evenement, on reste en attente de nouveaux messagess
                self.receptionPost(key, seq, seq, donnees)
            # snakeChannel.reception(s)

    def process_buffer(self):
        """Check buffer from each canal and send a message

        Secure message have the highest priority

        If the timer for the ack is expired, we resend the previous secure message
        The last secure message is not pop yet, we wait for the ack

        :return:
        """
        self.current_time += self.clock.tick(FPS)
        for canal in self.connexions:
            if self.attenteSecureReseau.get(canal) and self.attenteSecureReseau[canal] and not self.ackRecus[canal] \
                    and self.ack_timer.expired(self.current_time):
                # RE-send SECURE
                # If we didn't received ack for secure message, resend the message
                data = self.messagesSecures[canal][0][0]

                if self.udp:  # on udp
                    self.channel.sendto(data, canal)
                else:  # on snake_channel
                    self.send_channel(data, canal)

            elif self.messagesSecures.get(canal) and self.messagesSecures[canal] and not self.attenteSecureReseau[canal]:
                # Send SECURE
                # Get the first secure packet to send
                # We don't pop it because we will wait for the ack
                data = self.messagesSecures[canal][0][0]
                if not self.attenteSecureReseau[canal]:
                    # We are sending a secure message, we need to receive a ack and
                    # we can't have two secure message at the same time on the same channel
                    self.ackRecus[canal] = False
                    self.attenteSecureReseau[canal] = True

                    if self.udp:  # on udp
                        self.channel.sendto(data, canal)
                    else:  # on snake_channel
                        self.send_channel(data, canal)
                        print data

                    # Activate the timer in order to resend the message if it expires
                    self.ack_timer.activate(0)
            else:
                # Send NORMAL
                if self.messagesNormaux.get(canal) and \
                        self.messagesNormaux[canal]:
                    data = self.messagesNormaux[canal].pop(0)[0]

                    if self.udp:  # on udp
                        self.channel.sendto(data, canal)
                    else:  # on snake_channel
                        self.send_channel(data, canal)
                        # print data

    def initialisation(self, canal):
        if not self.messagesNormaux.get(canal):
            self.messagesNormaux[canal] = []
        if not self.messagesSecures.get(canal):
            self.messagesSecures[canal] = []
        if not self.last_ack.get(canal):
            self.last_ack[canal] = None
        if not self.last_seq.get(canal):
            self.last_seq[canal] = []
        if not self.ackRecus.get(canal):
            self.ackRecus[canal] = None
        if not self.attenteSecureReseau.get(canal):
            self.attenteSecureReseau[canal] = None
