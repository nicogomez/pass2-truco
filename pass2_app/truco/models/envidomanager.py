# -*- encoding: utf-8 -*-

from django.db import models
from truco.models import Player, Canto, CantoManager, Round

TEAM_A = -1
TEAM_B = 1
NO_TEAM = 0

class EnvidoManager(CantoManager):
    round = models.ForeignKey(Round)

    def determine_envido_winner(self):
        """
        Determina qué equipo gana el envido, y le asigna los puntos correspondientes.
        """
        team_a = self.round.game.get_team_a_players(False)
        team_b = self.round.game.get_team_b_players(False)

        team_a_points = map(lambda x: x.declared_envido_points, team_a)
        team_b_points = map(lambda x: x.declared_envido_points, team_b)

        points = self.get_envido_points_to_assign()

        if max(team_a_points) > max(team_b_points):
            self.round.game.give_points_to_team(points, TEAM_A)
        elif max(team_a_points) < max(team_b_points):
            self.round.game.give_points_to_team(points, TEAM_B)    
        else:
            lead_team = self.round.game.player_set.get(place_on_table = 0).team
            self.round.game.give_points_to_team(points, lead_team)

    def recantar(self, tipo_de_envido, cantor):
        """
        Se evalúa si el tipo de envido que se quiere cantar es factible, y si lo es
        se actualiza el tipo de envido actual.
        """
        se_puede_cantar = self.se_puede_cantar(tipo_de_envido)
        if se_puede_cantar:
            self.quien_canto_ultimo = cantor

            #aceptar ultimo canto como consecuencia de recantar algo
            self.aceptar_ultimo_canto()
            # crear nuevo canto
            nuevo_canto = self.canto_set.create()
            nuevo_canto.set_canto(tipo_de_envido)
            self.save()

        return se_puede_cantar

    def se_puede_cantar(self, tipo_de_envido):
        """
        Es posible cantar el envido tipo_de_envido?
        """

        result = False
        if Canto.es_algun_envido(tipo_de_envido):

            cantos_actuales = self.canto_set.all()
            if not cantos_actuales.exists():
                if tipo_de_envido != Canto.TipoCanto.ENVIDO_ENVIDO:
                    result = True
            else:
                mayor_canto_actual = max(cantos_actuales, key= lambda x: x.tipo_de_canto)
                result = mayor_canto_actual.es_menor_que(tipo_de_envido)
                result = result and mayor_canto_actual.estado == Canto.EstadoCanto.EN_ESPERA

        return result

    def get_falta_envido_points(self):
        return min(self.round.game.score_limit - self.round.game.team_a_score, 
                self.round.game.score_limit - self.round.game.team_b_score)

    def get_envido_points_to_assign(self):
        puntos = 0
        for canto in self.canto_set.all():
            if canto.estado == Canto.EstadoCanto.ACEPTADO:
                puntos += canto.puntos
            elif canto.estado == Canto.EstadoCanto.RECHAZADO:
                puntos += 1

        return puntos

    class Meta:
        app_label = 'truco'
