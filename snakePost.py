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
from timer import *
from select import *

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
        # dictionnaire de host,port qui contient message secure
        self.messagesSecures = {}
        self.messagesNormaux = {}

        self.last_ack = {}  # Last ack number
        self.seq_number = {}  # Last seq number
        self.ack_received = {}
        self.secure_in_network = {}

        pygame.init()
        pygame.time.set_timer(MESSAGE_SECURE, 30)
        self.numSeq = 0
        self.udp = False

    def gestionMessages(self, donnees, canal):
        if donnees is not None and len(donnees) >= 4:
            seq_number = struct.unpack('>H', donnees[:2])[0]
            ack_number = struct.unpack('>H', donnees[2:4])[0]

            print "SEQ_NUMBER : " + str(seq_number) + " - ACK_NUMBER " + str(ack_number)

            # SECURE - needs ack
            if seq_number != 0 and ack_number == 0:
                self.ack(seq_number, canal)

            # If we receive an ack
            if ack_number != 0 and len(self.last_seq_number[canal]) > 0:
                    # and (seq_number == 0 or seq_number == self.last_seq_number[canal][0]):
                # Compare the ack_number with the last seq_number
                if ack_number == self.last_seq_number[canal][0]:
                    # If the ack is correct, remove the secure message from the list
                    self.messagesSecures[canal].pop(0)
                    self.last_seq_number[canal].pop(0)
                    self.secure_in_network[canal] = False
                    self.ack_received[canal] = True
                    if seq_number != 0:
                        self.ack(seq_number, canal)
                else:
                    if self.udp:  # on udp
                        self.channel.sendto(self.messagesSecures[canal][0][0], canal)
                    else:  # on snake_channel
                        self.send_channel(self.messagesSecures[canal][0][0], canal)

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
        self.inistialisation(canal)
        if not secure:
            self.messagesNormaux[canal].append((struct.pack('>2H', 0, 0) + donnees, canal))
            # print "[send] Not secure : donnees = ", donnees, " - to : ", canal
        else:
            if len(self.messagesSecures[canal]) < MAX_CLIENT:
                self.last_seq_number[canal].append(random.randint(1, (1 << 16) - 1))
                self.messagesSecures[canal].append(
                    (struct.pack('>2H', self.last_seq_number[canal][-1], 0) + donnees, canal))
                print "SEQ_NUMBER : " + str(self.last_seq_number[canal][-1]) + " - ACK_NUMBER " + str(0)
            else:
                print "Buffer secure is full, try again later."

    def envoiNonSecure(self, s, donnees, host):
        # snakeChannel.envoi(s, donnees, host, sequence)
        self.envoi(s, donnees, host, 0)

    # def ackSecureMessage(self, host, sequence, donnees):
    #    if self.messagesSecures[host].get(0) == (donnees, sequence):
    #        self.messagesSecures[host].pop(0)

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
            if self.secure_in_network.get(canal) and \
                    self.secure_in_network[canal] and \
                    not self.ack_received[canal] and \
                    self.ack_timer.expired(self.current_time):
                # RE-send SECURE
                # If we didn't received ack for secure message, resend the message
                data = self.messagesSecures[canal][0][0]

                if self.udp:  # on udp
                    self.channel.sendto(data, canal)
                else:  # on snake_channel
                    self.send_channel(data, canal)

            elif self.messagesSecures.get(canal) and \
                    self.messagesSecures[canal] and \
                    not self.secure_in_network[canal]:
                # Send SECURE
                # Get the first secure packet to send
                # We don't pop it because we will wait for the ack
                data = self.messagesSecures[canal][0][0]
                if not self.secure_in_network[canal]:
                    # We are sending a secure message, we need to receive a ack and
                    # we can't have two secure message at the same time on the same channel
                    self.ack_received[canal] = False
                    self.secure_in_network[canal] = True

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
        if not self.last_seq_number.get(canal):
            self.last_seq_number[canal] = []
        if not self.ack_received.get(canal):
            self.ack_received[canal] = None
        if not self.secure_in_network.get(canal):
            self.secure_in_network[canal] = None
