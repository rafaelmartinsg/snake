# !/usr/bin/python2.7
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
#   Nom fichier     :   joueurs.py
# ##############################################################################
from constants import *

class Joueurs:
    def __init__(self, nom="Guest", couleur="yellow", score=0, etat=False, positions=[]):
        """

        Methode permettant de créer et d'initier les parametre d'un nouveau joueur
        :param nom: contient le nickname du joueur
        :param couleur: contient la couleur choisir par le joueur
        :param score: contient le score du joueur
        :param etat: contient l'etat du joueur (ready/non ready)
        :param positions: contient une liste avec les coordonnees du snake
        :return:
        """
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
