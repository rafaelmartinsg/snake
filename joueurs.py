# !/usr/bin/python2.7
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
#   Nom fichier     :   joueurs.py
# ##############################################################################
from constants import *

class Joueurs:
    def __init__(self, nom, couleur, score, etat, positions):
        self.nom = nom
        self.couleur = couleur
        self.score = score
        self.etat = etat
        self.positions = positions
        self.derniereMAJ = 0

    def ActualisationEtat(self, tempsCourant):
        self.derniereMAJ = tempsCourant

    def timeout(self, tempsCourant):
        return abs(tempsCourant - self.derniereMAJ) > MAX_ATTENTE_JOUEUR * 1000
