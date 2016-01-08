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
import socket
import random
import struct
from constants import *


class snakeChannel(object):
    def __init__(self, canal, ip, port, couleur, nickname):
        """

        :param canal: continent le canal de communication
        :param ip: contient l'adresse ip du serveur
        :param port: contient le port du serveur
        :param couleur: contient la couleur du joueur
        :param nickname:
        :return: correspond au nom du joueur
        """
        self.canal = canal
        self.addIP = ip
        self.nPort = port
        self.canal.setblocking(False)
        self.canal.settimeout(0.1)
        self.couleur = couleur
        self.nickname = nickname
        self.a = 0

        self.connexions = {}
        self.connexionsNonEtablies = {}

    def clientConnexion(self):
        """

        Methode qui permettra au client de se connecter au serveur
        Cette methode suit une machine d'etat definie par le cahier des charges de la maniere suivante :
            TX  :   0xFFFFFFFF (numero de sequence pour initier la connexion)
            TX  :   GetToken A Snake (envoi a interval regulier tant que le serveur ne repond pas)
            RX  :   Token B A ProtocoleNumber
            TX  :   Connect /nom_cles/valeur_cles/.../...
            RX  :   Connected B

        :return True: client connecte au serveur
        :return False: probleme pendant la phase de connexion
        """
        etat = 0
        a = random.randint(0, (1 << 32) - 1)
        b = 0

        while etat < 3:
            if etat == 0:
                self.envoiSnakeChann("GetToken " + str(a) + " Snake", (self.addIP, self.nPort),
                                     SEQUENCE_OUTBAND)
                print "Client envoi : GetToken", a, "Snake"
                etat += 1
            elif etat == 1:
                controlToken, client = self.receptionSnakeChann()
                print "Client recoit : ", controlToken
                if controlToken is None:
                    etat -= 1
                else:
                    token = controlToken.split()
                    # Controle du A recu
                    if token[2] == str(a):
                        b = token[1]
                        pNum = token[3]
                        self.envoiSnakeChann("Connect \\challenge\\" + str(b) + "\\protocol\\" + str(pNum) +
                                             "\\color\\" + str(self.couleur) + "\\nickname\\" + str(self.nickname),
                                             (self.addIP, self.nPort), SEQUENCE_OUTBAND)
                        print "Client envoi : Connect \challenge\\", b, \
                            "\\protocol\\", pNum, "\\color\\", str(self.couleur), "\\nickname\\", str(self.nickname)
                        etat += 1
                    else:
                        etat = 0
                        print "Erreur token, retour etat initial (0)"
            # Si etat 3
            elif etat == 2:
                controlConnexion, client = self.receptionSnakeChann()
                print "Client recoit : ", controlConnexion
                if controlConnexion is None:
                    # Si connexion pas acquitee, on revient a l'etat precedent
                    etat -= 1
                else:
                    token = controlConnexion.split()
                    print b
                    if b == token[1]:
                        etat += 1
                        return True
            else:
                print "Une erreur est survenue pendant la connexion du client."
                return False

    def receptionSnakeChann(self):
        """

        Methode qui receptionne les donnees et on les traite en fonction du n° de sequence.
            On taites les cas suivants :
                - Donnes recues valides --> on les traite. Sinon, on retourne None, None
                - Si n°sequence = 0xFFFFFFFF et que c'est la premiere connexion du client :
                    On cree une entree pour ce client dans le dictionnaire du serveur.
                - Si n°sequence != 0xFFFFFFFF et que l'on a pas depasse la valeur maximale :
                    On stock le numero de sequence du client dans le dictionnaire
                    On retourne le payload des donnees
        :return None, None: erreur dans les donnes ou sur le canal
        :return payload, canal: renvoi des donnees a transmettre sur le canal
        """
        try:
            donnees, host = self.canal.recvfrom(BUFFER_SIZE)
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
            return None, host
        except:
            return None, None
        
    def envoiSnakeChann(self, donnees, host, sequence=None):
        """

        :param donnees: continent les donnes a envoyer
        :param host: tuple avec adresse IP et n°port
        :param sequence: contient le numero de sequence
        :return:
        """
        if self.connexionsNonEtablies.get(host) is None:
            self.connexionsNonEtablies[host] = SEQUENCE_OUTBAND

        if sequence is None:
            # Incrementation du numero de sequence par modulo
            self.connexionsNonEtablies[host] = (self.connexionsNonEtablies[host] + 1) % (0x1 << 32)
        else:
            # Si n°sequence = 0xFFFFFFFF -> phase de connexion
            self.connexionsNonEtablies[host] = sequence

        # Pack le numero de sequence
        pack = struct.pack('>I', self.connexionsNonEtablies[host])
        pack += donnees

        self.canal.sendto(pack, host)

    def serveurConnexion(self):
        """

        Methode qui s'occupe de la phase de connexion entre un client et un serveur
        Les messages sont definit par le cahier des charges, de la manière suivante :
           RX  :   0xFFFFFFFF (numero de sequence OUTBAND pour initier la connexion)
           RX  :   GetToken A Snake
           TX  :   Token B A ProtocoleNumber
           RX  :   Connect /nom_cles/valeur_cles/.../...
           TX  :   Connected B

        :return:
        """
        try:
            donnees, client = self.receptionSnakeChann()

            if donnees is None:
                return None, None
            if not self.connexions[client][C_STATUS]:
                token = donnees.split()
                print "Serveur recoit : ", donnees

                if token[0] == "GetToken":
                    self.connexions[client][C_SEQNUM] = 0
                    # Generation de B de la meme sorte que A
                    self.a = random.randint(0, (1 << 32) - 1)
                    b = token[1]

                    self.envoiSnakeChann("Token " + str(self.a) + " " + str(b) + " " + str(PNUM), client,
                                         SEQUENCE_OUTBAND)
                    print "Serveur envoi : Token ", self.a, " ", b, " ", PNUM

                elif token[0] == "Connect":
                    separateur = token[1].split("\\")
                    couleur = separateur[6]
                    nickname = separateur[8]

                    # Control de la valeur de B
                    if (len(separateur) < 3) or (int(self.a) != int(separateur[2])):
                        print "Suivant... !"
                        return None, None

                    self.envoiSnakeChann("Connected " + str(self.a), client, SEQUENCE_OUTBAND)
                    self.connexions[client][C_STATUS] = True
                    self.connexions[client][C_COULEUR] = couleur
                    self.connexions[client][C_NICKNAME] = nickname
                    print "Serveur envoi : Connected ", self.a
                print "En attente de clients ..."
            else:
                # Client connecte
                return donnees, client
        except socket.timeout:
            pass
        return None, None
