# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
import random

from truco.models import Game, Card

TEAM_A = -1
TEAM_B = 1
NO_TEAM = 0

class Player(models.Model):
    game = models.ForeignKey(Game)
    user = models.OneToOneField(User)
    team = models.IntegerField(default=0)
    owner = models.BooleanField(default=False)
    card_1 = models.ForeignKey(Card, related_name='card_1', on_delete=models.DO_NOTHING)
    card_2 = models.ForeignKey(Card, related_name='card_2', on_delete=models.DO_NOTHING)
    card_3 = models.ForeignKey(Card, related_name='card_3', on_delete=models.DO_NOTHING)
    declared_envido_points = models.IntegerField(default=0)
    place_on_table = models.PositiveIntegerField(default=0)
    gone_to_mazo = models.BooleanField(default=False)

    def put_card(self, card_selected):
        card = self.get_card_by_number(card_selected)
        card.position = self.game.round.confront_number
        card.save()

    def get_envido_points(self):
        list_of_cards = self.get_current_cards()
        points = 0
        palos_list = []
        # Cada elemento de esta lista representa las cartas con este palo
        for i in xrange(0,4):
            palos_list.append([])

        # En cada lista se guardan las cartas correspondientes a su palo
        for card in list_of_cards:
            if card.palo == "o":
                palos_list[0].append(card.number)
            elif card.palo == "b":
                palos_list[1].append(card.number)
            elif card.palo == "c":
                palos_list[2].append(card.number)
            else: 
                palos_list[3].append(card.number)

        # Filtramos quedandonos con el palo con mas de una carta
        bigger = filter(lambda x: len(x) > 1, palos_list)

        # Si hay al menos 2 cartas del mismo palo
        if bigger:
            bigger = filter(lambda x: x<10, bigger[0])
            points = sum(bigger) + 20
            # si quedaron cartas diferentes de 10 11 y 12
            if bigger:
                if len(bigger) == 3:
                    points -= min(bigger)
        else:
            # Obtengo la carta con mayor puntaje
            points = max(map(lambda y: y.number, list_of_cards))

        return points

    def get_current_cards(self):
        """
        Este metodo devuelve una lista de las cartas del jugador
        """
        list_of_cards = []
        list_of_cards.append(self.card_1)
        list_of_cards.append(self.card_2)
        list_of_cards.append(self.card_3)

        return list_of_cards

    def is_my_turn(self):
        result = True
        result = result and self.game.round
        result = result and self.place_on_table == self.game.round.current_turn

        return result

    def next_turn_is_mine(self):
        result = True
        result = result and self.game.round
        result = result and self.place_on_table == self.game.round.get_next_turn()

        return result

    def get_my_team_score(self):
        if self.team == TEAM_A:
            return self.game.team_a_score

        return self.game.team_b_score

    def get_opponent_team_score(self):
        if self.team == TEAM_A:
            return self.game.team_b_score

        return self.game.team_a_score

    def get_my_team_round_score(self):
        if self.team == TEAM_A:
            return self.game.round.team_a_round_score

        return self.game.round.team_b_round_score

    def get_opponent_team_round_score(self):
        if self.team == TEAM_A:
            return self.game.round.team_b_round_score

        return self.game.round.team_a_round_score

    def declare_canto(self, tipo_de_canto):
        from truco.models import Canto
        truco_mgr = self.game.round.get_truco_manager()
        envido_mgr = self.game.round.get_envido_manager()

        if tipo_de_canto == Canto.TipoCanto.IR_AL_MAZO:
            self.gone_to_mazo = True
            self.save()
            self.game.round.try_finish()
            self.game.round.next_turn()
        else:

            if Canto.es_algun_envido(tipo_de_canto):
                envido_mgr.recantar(tipo_de_canto, self)
            elif Canto.es_algun_truco(tipo_de_canto):
                truco_mgr.recantar(tipo_de_canto,self)        

    def leave_game(self):
        self.delete()

    def get_opponent_team(self):
        return self.team * (-1)

    def get_card_by_number(self, card_number):
        if card_number == '1':
            result = self.card_1
        elif card_number == '2':
            result = self.card_2
        elif card_number == '3':
            result = self.card_3
        else:
            result = None

        return result

    def get_card_by_position(self, card_position):
        cards = self.get_current_cards()
        result = filter(lambda x: x.position == card_position, cards)
        if len(result) > 0:
            return result[0]

        return None
        

    def delete_cards(self):
        self.card_1.delete()
        self.card_2.delete()
        self.card_3.delete()

    def __unicode__(self):
        return self.user.username + " " + "Player"

    class Meta:
        app_label = 'truco'
