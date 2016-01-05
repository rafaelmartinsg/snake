#!\usr\bin\python2.7
# -*- coding: utf-8 -*-

#  ##############################################################################
#   Auteurs         :   Gerber Cedric
#                       Martins Gomes Rafael
#   Date de debut   :   28 septembre 2015
#   Date de fin     :   08 janvier 2016
#   Etablissement   :   hepia
#   Filiere         :   3eme ITI
#   Cours           :   Reseau I
#
#   Nom fichier     :   snakeChannel.py
# ##############################################################################
import socket  # Import socket module
import random
import struct
from constants import *

C_SEQNUM = 0    # Numero de sequence
C_STATUS = 1    # Statut du client (connectee / deconnecte)
C_LASTP = 2     # Dernier ping
C_COULEUR = 3   # Couleur du joueur
C_NICKNAME = 4  # Nickname du joueur


class snakeChannel(object):
    def __init__(self, canal, ip, port, couleur, nickname):
        self.canal = canal
        self.addIP = ip
        self.nPort = port
        self.canal.setblocking(False)
        self.canal.settimeout(0.1)
        self.couleur = couleur
        self.nickname = nickname
        self.A = 0

        self.connexions = {}
        self.connexionsNonEtablies = {}

    def clientConnexion(self):
        etat = 0
        A = random.randint(0, (1 << 32) - 1)
        B = 0
        # couleur = pygame.color.THECOLORS
        while (etat < 3):
            # Si etat 0
            if etat == 0:
                self.envoiSnakeChann("GetToken " + str(A) + " Snake", (self.addIP, self.nPort),
                                     SEQUENCE_OUTBAND)
                print "Client envoi : GetToken", A, "Snake"
                etat += 1
            # Si etat 1
            elif etat == 1:
                controlToken, client = self.receptionSnakeChann
                print "Client recoit : ", controlToken
                if controlToken is None:
                    etat -= 1
                else:
                    token = controlToken.split()
                    # Controle du A recu
                    if token[2] == str(A):
                        B = token[1]
                        pNum = token[3]
                        self.envoiSnakeChann("Connect \\challenge\\" + str(B) + "\\protocol\\" + str(pNum) +
                                             "\\color\\" + str(self.couleur) + "\\nickname\\" + str(self.nickname),
                                             (self.addIP, self.nPort), SEQUENCE_OUTBAND)
                        print "Client envoi : Connect \challenge\\", B, \
                            "\\protocol\\", pNum, "\\color\\", str(self.couleur), "\\nickname\\", str(self.nickname)
                        etat += 1
                    else:
                        etat = 0
                        print "Erreur token, retour etat initial (0)"
            # Si etat 3
            elif etat == 2:
                controlConnexion, client = self.receptionSnakeChann
                print "Client recoit : ", controlConnexion
                if controlConnexion is None:
                    # Si connexion pas acquitee, on revient a l'etat precedent
                    etat -= 1
                else:
                    token = controlConnexion.split()
                    print B
                    if B == token[1]:
                        etat += 1
                        return True
            else:
                print "Une erreur est survenue pendant la connexion du client."
                return False

    def receptionSnakeChann(self):
        """Receive data with sequence number

        Verification of sequence message.
        If this is the first time we manage this connection, we add his sequence number
        as 0xffffffff for the connection phase (out of band messages).
        :return:
        """
        try:
            donnees, host = self.canal.recvfrom(BUFFER_SIZE)
            # print data
        except socket.error:
            return None, None

        try:
            numSquence = struct.unpack('>I', donnees[:4])[0]
            payload = donnees[4:]

            if self.connexions.get(host) is None:
                self.connexions[host] = [SEQUENCE_OUTBAND, False, 0, '', '']

            if ((numSquence == SEQUENCE_OUTBAND) or
                    (self.connexions[host][C_SEQNUM] < numSquence) or
                    (numSquence < self.connexions[host][C_SEQNUM] and
                        (self.connexions[host][C_SEQNUM] - numSquence) > (1 << 31))):
                self.connexions[host][C_SEQNUM] = numSquence
                return payload, host
            return None, None

        except:
            # If we receive garbage, return None
            return None, None

    #   envoi
    #
    #   Parametres  :   - donnees   : continent les donnes a envoyer
    #                   - client    : tuple avec adresse IP et n°port
    #                   - sequence  : utile uniquement pour l'envoi de sequence hors bande
    #
    def envoiSnakeChann(self, donnees, host, sequence):
        if self.connexionsNonEtablies.get(host) is None:
            self.connexionsNonEtablies[host] = SEQUENCE_OUTBAND

        if sequence is None:  # Incrementation of sequence number (modulo)
            self.connexionsNonEtablies[host] = (self.connexionsNonEtablies[host] + 1) % (0x1 << 32)
        else:  # Sequence number is 0xFFFFFFFF -> connection packet
            self.connexionsNonEtablies[host] = sequence

        # Pack the sequence number
        pack = struct.pack('>I', self.connexionsNonEtablies[host])
        # Concatenation of data
        pack += donnees

        # Send the message
        # print str(pack)
        self.canal.sendto(pack, host)

    def serveurConnexion(self):
        print 'Serveur ecoute sur le port : ', self.nPort, '...'
        print "En attente de clients ..."
        try:
            donnees, client = self.receptionSnakeChann

            if donnees is None:
                return None, None
            if not self.connexions[client][C_STATUS]:
                token = donnees.split()
                print "Serveur recoit : ", donnees

                if token[0] == "GetToken":
                    self.connexions[client][C_SEQNUM] = 0
                    # Generation de B de la meme sorte que A
                    self.A = random.randint(0, (1 << 32) - 1)
                    B = token[1]

                    self.envoiSnakeChann("Token " + str(self.A) + " " + str(B) + " " + str(PNUM), client,
                                         SEQUENCE_OUTBAND)
                    print "Serveur envoi : Token ", self.A, " ", B, " ", PNUM

                elif token[0] == "Connect":
                    separateur = token[1].split("\\")
                    couleur = separateur[6]
                    nickname = separateur[8]
                    print "separateur == ", separateur
                    print "couleur == ", couleur
                    print "nickname == ", nickname

                    # Control de la valeur de B
                    if (len(separateur) < 3) or (int(self.A) != int(separateur[2])):
                        print "Suivant...!"
                        return None, None

                    self.envoiSnakeChann("Connected " + str(self.A), client, SEQUENCE_OUTBAND)
                    self.connexions[client][C_STATUS] = True
                    self.connexions[client][C_COULEUR] = couleur
                    self.connexions[client][C_NICKNAME] = nickname
                    print "Serveur envoi : Connected ", self.A
                print "En attente de clients ..."
            else:
                # Client connecte
                return donnees, client
        except socket.timeout:
            # print 'Error timeout'
            pass
        return None, None
