# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
import random

TEAM_A = -1
TEAM_B = 1
NO_TEAM = 0


class Game(models.Model):
    name = models.CharField(max_length=100)
    game_started = models.BooleanField(default=False)
    number_of_players = models.PositiveIntegerField(default=2)
    score_limit = models.PositiveIntegerField(default=15)
    team_a_score = models.PositiveIntegerField(default=0)
    team_b_score = models.PositiveIntegerField(default=0)

    def add_player(self, user, owner):
        from truco.models import Player, Card
        card_1 = Card.objects.create(anchor=1)
        card_2 = Card.objects.create(anchor=2)
        card_3 = Card.objects.create(anchor=3)
        new_player = Player.objects.create(
            user=user,
            game=self,
            owner=owner,
            card_1=card_1,
            card_2=card_2,
            card_3=card_3,
        )

        return new_player

    def is_ready(self):
        return self.player_set.count() == self.number_of_players

    def init_game(self):
        players = list(self.player_set.all())
        random.shuffle(players)
        position = 0
        team_selector = 1
        
        for player in players:
            player.place_on_table = position
            position += 1
            player.team = team_selector
            team_selector *= -1
            player.save()

        self.next_round()
        self.game_started = True
        self.save()

    def finish_round(self):
        self.next_round()

    def is_finished(self):
        return self.team_a_score >= self.score_limit or self.team_b_score >= self.score_limit

    def next_round(self):
        from truco.models import Round
        # Al iniciar la sig ronda, borro la anterior
        players = list(self.player_set.all())

        try:
            self.round.delete()
        except Exception:
            pass 

        ronda = Round(game=self)
        ronda.save()
        ronda.init_canto_managers()
        ronda.save()

        # Re asigno las posiciones en la mesa, por cada nueva ronda, para el cambio de mano
        # Y reseteo de algunas variables
        for player in players:
            player.place_on_table = (player.place_on_table + 1) % self.number_of_players
            player.declared_envido_points = 0
            player.gone_to_mazo = False
            player.save()

        ronda.deal_cards(players)
        ronda.save()

    def get_team_a_players(self, only_active_players=False):
        """
        Devuelve una lista de todos los jugadores del equipo A si only_active_players = False.
        si es diferente, devuelve solo los jugadores que no se fueron al mazo
        """
        result = self.player_set.filter(team= TEAM_A)
        if only_active_players:
            result = result.filter(gone_to_mazo=False)

        return result

    def get_team_b_players(self, only_active_players=False):
        """
        Devuelve una lista de todos los jugadores del equipo B si only_active_players = False.
        si es diferente, devuelve solo los jugadores que no se fueron al mazo
        """
        result = self.player_set.filter(team= TEAM_B)
        if only_active_players:
            #lista de solo los jugadores que no se fueron al mazo
            result = result.filter(gone_to_mazo=False)

        return result


    def give_points_to_team(self, points, team):
        if team == TEAM_A:
            self.team_a_score += points
            self.round.team_a_round_score += points
        elif team == TEAM_B:
            self.team_b_score += points
            self.round.team_b_round_score += points
        
        self.round.game.save()
        self.round.save()

    def finish_game(self):
        players = list(self.player_set.all())
        self.round.delete()

        for player in players:
            player.delete_cards()
            player.delete()

        self.delete()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'truco'
