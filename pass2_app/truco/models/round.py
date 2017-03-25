# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
import random

from truco.models import Game

TEAM_A = -1
TEAM_B = 1
NO_TEAM = 0
CONFRONT_UNFINISHED = 2


class Round(models.Model):
    game = models.OneToOneField(Game)

    current_turn = models.PositiveIntegerField(default=0)
    confront_number = models.PositiveIntegerField(default=1)

    team_a_round_score = models.PositiveIntegerField(default=0)
    team_b_round_score = models.PositiveIntegerField(default=0)

    team_a_envido_points = models.CharField(default="", max_length=200)
    team_b_envido_points = models.CharField(default="", max_length=200)

    players_must_put_envido_points = models.BooleanField(default=False) # esto no se usa, se puede borrar
    envido_points_already_assigned = models.BooleanField(default=False)


    def init_canto_managers(self):
        """
        Inicializa los managers para los cantos.
        """
        self.envidomanager_set.create()
        self.trucomanager_set.create()

    def deal_cards(self, jugadores): 
        from truco.models import Card 
        mazo = Card.generate_mazo()

        for player in jugadores:
            carta = random.choice(mazo)
            player.card_1.set_from_tuple(carta)
            ubi = mazo.index(carta)
            del mazo[ubi]

            carta = random.choice(mazo)
            player.card_2.set_from_tuple(carta)
            ubi = mazo.index(carta)
            del mazo[ubi]

            carta = random.choice(mazo)
            player.card_3.set_from_tuple(carta)
            ubi = mazo.index(carta)
            del mazo[ubi]

            player.save()

    # Region: Metodos utiles sobre los diferentes cantos
    #---------------------------------------------------------------------
    def get_envido_manager(self):
        return self.envidomanager_set.first()

    def get_truco_manager(self):
        return self.trucomanager_set.first()


    def player_can_declare(self, player, tipo_de_canto):
        """
        Determina si un player puede cantar tipo_de_canto en este momento.
        """
        from truco.models import Canto

        truco_mgr = self.get_truco_manager()
        envido_mgr = self.get_envido_manager()
        result = True
        if player.gone_to_mazo:
            return False

        if tipo_de_canto == Canto.TipoCanto.IR_AL_MAZO and player.is_my_turn():
            return True

        if Canto.es_algun_envido(tipo_de_canto):
            result = self.confront_number == 1
            result = envido_mgr.se_puede_cantar(tipo_de_canto) and result
            if envido_mgr.get_ultimo_canto() != Canto.TipoCanto.NADA:
                result = envido_mgr.quien_canto_ultimo.team != player.team and result

            if truco_mgr.hay_algun_canto_aceptado():
                return False

            ultimo_truco_cantado = truco_mgr.get_ultimo_canto()
            if player.is_my_turn():
                #result = ultimo_truco_cantado == Canto.TipoCanto.NADA and result
                if ultimo_truco_cantado != Canto.TipoCanto.NADA and truco_mgr.quien_canto_ultimo.team == player.team: # yo cante truco
                    if envido_mgr.get_ultimo_canto() == Canto.TipoCanto.NADA:  # y no se canto ningun envido: no se puede cantar envidos
                        result = False
            else:
                if ultimo_truco_cantado == Canto.TipoCanto.TRUCO:
                    if truco_mgr.quien_canto_ultimo.team == player.team:
                        result = False

                if envido_mgr.get_ultimo_canto() != Canto.TipoCanto.NADA:
                    if envido_mgr.get_estado_del_ultimo_canto() != Canto.EstadoCanto.EN_ESPERA:
                        result = False

                if ultimo_truco_cantado == Canto.TipoCanto.NADA and envido_mgr.get_ultimo_canto() == Canto.TipoCanto.NADA:
                    result = False

        elif Canto.es_algun_truco(tipo_de_canto):
            result = truco_mgr.se_puede_cantar(tipo_de_canto)

            if truco_mgr.get_ultimo_canto() != Canto.TipoCanto.NADA:
                result = truco_mgr.quien_canto_ultimo.team != player.team and result

            if envido_mgr.get_ultimo_canto() != Canto.TipoCanto.NADA:
                result = (self.all_players_sang_their_points() or 
                    envido_mgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.RECHAZADO) and result


            if truco_mgr.get_ultimo_canto() == Canto.TipoCanto.NADA:
                result = player.is_my_turn() and result
            else:
                result = truco_mgr.quien_canto_ultimo.team != player.team and result
                result = (player.is_my_turn() or
                        truco_mgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.EN_ESPERA) and result

        else:
            result = False

        return result


    def accept_last_envido(self):
        self.get_envido_manager().aceptar_ultimo_canto()

    def accept_last_truco(self):
        self.get_truco_manager().aceptar_ultimo_canto()

    def reject_last_envido(self):
        self.get_envido_manager().rechazar_ultimo_canto()

    def reject_last_truco(self):
        self.get_truco_manager().rechazar_ultimo_canto()


    def determine_and_assign_points_to_envido_winner(self):
        """
        similar a lo que hace el metodo del EnvidoManager TODO: ver por que el duplicado.
        """
        if self.envido_points_already_assigned:
            return
        self.envido_points_already_assigned = True
        team_a = self.game.get_team_a_players(False)
        team_b = self.game.get_team_b_players(False)
        team_a_points = map(lambda x: x.declared_envido_points, team_a)
        team_b_points = map(lambda x: x.declared_envido_points, team_b)

        points = self.get_envido_manager().get_envido_points_to_assign()
        if max(team_a_points) > max(team_b_points):
            self.game.give_points_to_team(points, TEAM_A)
        elif max(team_a_points) < max(team_b_points):
            self.game.give_points_to_team(points, TEAM_B)
        else:
            lead_team = self.game.player_set.get(place_on_table = 0).team
            self.game.give_points_to_team(points, lead_team)
        self.save()

    def determine_if_team_is_a_liar(self, team):
        """
        Determina si algun jugador de un equipo dado ha mentido en su envido. 
        """
        if team == TEAM_A:
            team = self.game.get_team_a_players(False)
        else:
            team = self.game.get_team_b_players(False)

        result = False

        for player in team:
            if player.declared_envido_points > 0:
                result = (player.declared_envido_points != player.get_envido_points()) or result 

        return result

    def all_players_sang_their_points(self):
        """
        Determina si todos los jugadores han cantado sus puntos o aceptado 
        como buenos los puntos de su contrincante.
        """
        players = self.game.player_set.exclude(gone_to_mazo=True)
        result = all(map(lambda x: x.declared_envido_points != 0, players))

        return result 

    def determine_round_winner(self):
        first_confrontment = self.confront(1)
        second_confrontment = self.confront(2)
        third_confrontment = self.confront(3)


        if first_confrontment == TEAM_A:
            if second_confrontment == TEAM_A:
                return TEAM_A

            if second_confrontment == TEAM_B:
                if third_confrontment == TEAM_A:
                    return TEAM_A

                if third_confrontment == TEAM_B:
                    return TEAM_B

                if third_confrontment == NO_TEAM:
                    return TEAM_A

            if second_confrontment == NO_TEAM:
                    return TEAM_A

        elif first_confrontment == TEAM_B:
            if second_confrontment == TEAM_B:
                return TEAM_B

            if second_confrontment == TEAM_A:
                if third_confrontment == TEAM_A:
                    return TEAM_A

                if third_confrontment == TEAM_B:
                    return TEAM_B

                if third_confrontment == NO_TEAM:
                    return TEAM_B

            if second_confrontment == NO_TEAM:
                    return TEAM_B
        else:
            if second_confrontment == TEAM_B:
                return TEAM_B

            if second_confrontment == TEAM_A:
                return TEAM_A

            if second_confrontment == NO_TEAM:
                if third_confrontment == TEAM_A:
                    return TEAM_A
                if third_confrontment == TEAM_B:
                    return TEAM_B
                if third_confrontment == NO_TEAM:
                    lead_team = self.game.player_set.get(place_on_table = 0).team
                    return lead_team

        return NO_TEAM

    def get_max_score(self, list_players, card_position):
        """
        Devuelve la carta de máximo valor de entre las jugadas por los jugadores en list_players, en la
        posición card_position, si no todas las cartas han sido jugadas, se retorna 0.
        """
        result = 0
        if len(list_players) > 0:
            #players_who_didnt_gone_to_mazo = list(list_players.exclude(gone_to_mazo=True))
            all_cards_thrown = all(map(lambda x: x.get_card_by_position(card_position) != None,list_players))
                
            if all_cards_thrown:
                    result = max(map(lambda x: x.get_card_by_position(card_position).get_score(), list_players))
        
        return result

    def confront(self, confrontment_number):
        """
        Se confrontan las cartas de los jugadores, y se devuelve qué equipo ganó el actual confrontamiento,
        si aún no se han puesto en mesa todas las cartas de este confrontamiento, se retorna el valor
        CONFRONT_UNFINISHED.
        """
        players_team_a = self.game.get_team_a_players(True)
        players_team_b = self.game.get_team_b_players(True)

        players_x_card_team_a = self.get_max_score(players_team_a, confrontment_number)
        players_x_card_team_b = self.get_max_score(players_team_b, confrontment_number)

        if players_x_card_team_b != 0 and players_x_card_team_a != 0:
            if players_x_card_team_a < players_x_card_team_b:
                return TEAM_B
            elif players_x_card_team_a > players_x_card_team_b:
                return TEAM_A
            else:
                return NO_TEAM
        else:
            return CONFRONT_UNFINISHED

    def next_turn(self):
        from truco.models import Player

        confrontment_result = self.confront(self.confront_number) 
        if  confrontment_result == CONFRONT_UNFINISHED: #Por confrontment_result == NO_TEAM
            self.increment_turn()
            
        else:
            # obtengo lista de playesr ganadores del confrontamiento
            if confrontment_result == TEAM_A:
                winner_players = self.game.get_team_a_players(True)
            elif confrontment_result == TEAM_B:
                winner_players = self.game.get_team_b_players(True)

            if confrontment_result != NO_TEAM: 
                # Obtengo el valor jerarquico mas alto de la carta entre los ganadores 
                max_score = self.get_max_score(winner_players, self.confront_number)
                # Filtramos paa que solo queden en la lista, los que tienen este maximo valor
                winner_players = filter(lambda y:
                                 y.get_card_by_position(self.confront_number).get_score() == max_score, winner_players)

                # Le damos el sigueinte turno al jugador de place_on_table menor
                self.current_turn = min(map(lambda x: x.place_on_table, winner_players))
            else:
                self.increment_turn()

            self.confront_number += 1
            self.save()

            # Al terminar cada confrontamiento, veo si alguien puede haber ganado la ronda
            winner_team = self.determine_round_winner()
            
            if self.is_finished():

                # self.determine_envido_winner()
                self.finish(winner_team)

    def try_finish(self):
        """
        Función que intenta asignar puntos si la ronda finalizó, existe sobre todo
        porque sino la unica forma de que se asignen los puntos cuando finaliza una partida,
        es cuando se chequea is_finished cuando se pone alguna carta, si todos los
        jugadores de un equipo se van al mazo, el juego termina, pero no se asignan puntos
        ya que nunca se hace el chequeo de is_finished.
        """
        if self.is_finished():
            self.determine_and_assign_points_to_envido_winner()
            if self.entire_team_gone_to_mazo(TEAM_A):
                winner_team = TEAM_B
            else:
                winner_team = TEAM_A
            self.assign_truco_points(winner_team)

    def finish(self, winner_team):
        self.determine_and_assign_points_to_envido_winner()
        self.assign_truco_points(winner_team)

    def increment_turn(self):
    
        # me fijo si el turno le toca a algun player que se fue al mazo
        siguiente_turno = (self.current_turn +1) % self.game.number_of_players
        actual_player = self.game.player_set.filter(place_on_table = siguiente_turno, gone_to_mazo=True)
        # mientras 
        while(actual_player.exists()):
                siguiente_turno = (siguiente_turno +1) % self.game.number_of_players
                actual_player = self.game.player_set.filter(place_on_table = siguiente_turno, gone_to_mazo=True)

        self.current_turn = siguiente_turno        
        self.save()

    def get_next_turn(self):
        return (self.current_turn +1) % self.game.number_of_players

    def is_finished(self):
        from truco.models import Canto
        first_cond = self.determine_round_winner() != NO_TEAM
        truco_mgr = self.get_truco_manager()
        second_cond = self.entire_team_gone_to_mazo(TEAM_A) or self.entire_team_gone_to_mazo(TEAM_B)

        third_cond = False
        if truco_mgr.get_ultimo_canto() != Canto.TipoCanto.NADA:
            third_cond = truco_mgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.RECHAZADO

        return (first_cond or second_cond or third_cond)

    def entire_team_gone_to_mazo(self, team):
        if team == TEAM_A:
            players = self.game.get_team_a_players(True)
        else:
            players = self.game.get_team_b_players(True)

        if players != None:
            return all(map(lambda x: x.gone_to_mazo, players))
        else:
            return True


    def assign_truco_points(self, winner_team=NO_TEAM):
        """
        Metodo que se encarga de asignar los puntos obtenidos por el truco,
        retruco y/o vale cuatro, al equipo ganador de cada ronda.
        """        
        if winner_team == NO_TEAM:
            winner_team = self.determine_round_winner()
        
        truco_points = self.get_truco_manager().get_truco_points_to_assign()

        self.game.give_points_to_team(truco_points, winner_team)

    def __unicode__(self):
        return self.game.name

    class Meta:
        app_label = 'truco'
