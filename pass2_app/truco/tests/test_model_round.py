from django.test import TestCase
from truco.models import *
from django.contrib.auth.models import User

class RoundTests(TestCase):

    def setUp(self):
        game_1 = Game.objects.create(name='1', team_a_score=6, team_b_score=10)
        self.round_1 = Round()
        game_1.round= self.round_1
        game_1.round.save()
        game_1.round.init_canto_managers()
        game_1.round.save()

        user_1 = User.objects.create_user(username='nano', password='nano')
        user_2 = User.objects.create_user(username='nico', password='nico')
        card_1 = Card.objects.create(number=12, palo='e', position=1, anchor=1)
        card_2 = Card.objects.create(number=7, palo='o', position=2, anchor=2)
        card_3 = Card.objects.create(number=1, palo='b', position=3, anchor=3)
        card_1_1 = Card.objects.create(number=1, palo='e', position=3, anchor=1)
        card_2_2 = Card.objects.create(number=11, palo='c', position=2, anchor=2)
        card_3_3 = Card.objects.create(number=3, palo='b', position=1, anchor=3)
        self.player_1 = Player.objects.create(
            user=user_1,
            game=game_1,
            card_1=card_1,
            card_2=card_2,
            card_3=card_3,
            team=-1
        )
        self.player_2 = Player.objects.create(
            user=user_2,
            game=game_1,
            card_1=card_1_1,
            card_2=card_2_2,
            card_3=card_3_3,
            team=1
        )
        self.emgr = EnvidoManager.objects.get(round=self.round_1)
        #Player 1 canta Envido
        self.canto_1= self.emgr.canto_set.create()
        self.canto_1.set_canto(Canto.TipoCanto.ENVIDO)
        self.emgr.quien_canto_ultimo = self.player_1
        self.emgr.save()

        self.tmgr = TrucoManager.objects.get(round=self.round_1)
        #Player 2 canta truco
        self.canto_2= self.tmgr.canto_set.create()
        self.canto_2.set_canto(Canto.TipoCanto.TRUCO)
        self.tmgr.quien_canto_ultimo = self.player_2
        self.tmgr.save()
 
    def test_init_canto_managers(self):
        self.assertEqual(len(self.round_1.envidomanager_set.all()), 1)
        self.assertEqual(len(self.round_1.trucomanager_set.all()), 1)

    def test_get_envido_manager(self):
        self.assertIsInstance(self.round_1.get_envido_manager(), EnvidoManager)

    def test_get_truco_manager(self):
        self.assertIsInstance(self.round_1.get_truco_manager(), TrucoManager)

    def test_player_can_declare(self):
        #Deben poder irse al mazo en cualquier momento
        self.assertTrue(self.round_1.player_can_declare(self.player_1, Canto.TipoCanto.IR_AL_MAZO))
        self.assertTrue(self.round_1.player_can_declare(self.player_2, Canto.TipoCanto.IR_AL_MAZO))
        #Verifico que Player 2 pueda recantar cualquier envido
        self.assertFalse(self.round_1.player_can_declare(self.player_1, Canto.TipoCanto.ENVIDO))
        self.assertTrue(self.round_1.player_can_declare(self.player_2, Canto.TipoCanto.ENVIDO_ENVIDO))
        self.assertTrue(self.round_1.player_can_declare(self.player_2, Canto.TipoCanto.REAL_ENVIDO))
        self.assertTrue(self.round_1.player_can_declare(self.player_2, Canto.TipoCanto.FALTA_ENVIDO))
        self.assertFalse(self.round_1.player_can_declare(self.player_2, Canto.TipoCanto.TRUCO))
        #Player 2 responde Real Envido
        self.emgr.recantar(Canto.TipoCanto.REAL_ENVIDO, self.player_2)
        self.assertFalse(self.round_1.player_can_declare(self.player_1, Canto.TipoCanto.ENVIDO_ENVIDO))
        self.assertTrue(self.round_1.player_can_declare(self.player_1, Canto.TipoCanto.FALTA_ENVIDO))
        self.assertFalse(self.round_1.player_can_declare(self.player_1, Canto.TipoCanto.TRUCO))
        #Player 1 responde Falta Envido
        self.emgr.recantar(Canto.TipoCanto.FALTA_ENVIDO, self.player_1)
        self.assertFalse(self.round_1.player_can_declare(self.player_2, Canto.TipoCanto.TRUCO))
        #Player 2 no acepta
        self.emgr.rechazar_ultimo_canto()

        #Player 1 declara Retruco
        self.tmgr.recantar(Canto.TipoCanto.RETRUCO, self.player_1)
        self.assertFalse(self.round_1.player_can_declare(self.player_1, Canto.TipoCanto.VALE_CUATRO))
        #Player 2 acepta
        self.tmgr.aceptar_ultimo_canto()
        self.assertFalse(self.round_1.player_can_declare(self.player_1, Canto.TipoCanto.VALE_CUATRO))
        

    def test_accept_last_envido(self):
        self.round_1.accept_last_envido()
        self.assertEqual(self.emgr.get_estado_del_ultimo_canto(), Canto.EstadoCanto.ACEPTADO)

    def test_accept_last_truco(self):
        self.round_1.accept_last_truco()
        self.assertEqual(self.tmgr.get_estado_del_ultimo_canto(), Canto.EstadoCanto.ACEPTADO)

    def test_reject_last_envido(self):
        self.round_1.reject_last_envido()
        self.assertEqual(self.emgr.get_estado_del_ultimo_canto(), Canto.EstadoCanto.RECHAZADO)

    def test_reject_last_truco(self):
        self.round_1.reject_last_truco()
        self.assertEqual(self.tmgr.get_estado_del_ultimo_canto(), Canto.EstadoCanto.RECHAZADO)

    def test_determine_and_assign_points_to_envido_winner(self):
        self.emgr.aceptar_ultimo_canto()
        self.emgr.save()
        self.player_1.declared_envido_points = 25
        self.player_1.save()
        self.player_2.declared_envido_points = 26
        self.player_2.save()
        self.round_1.determine_and_assign_points_to_envido_winner()
        self.assertEqual(self.round_1.team_a_round_score, 0)
        self.assertEqual(self.round_1.team_b_round_score, 2)

    # test test_determine_if_team_is_a_liar(self) y test de all_players_sang_their_points()
    def test_determine_if_team_is_a_liar(self):
        self.player_1.declared_envido_points = 12
        self.player_1.save()
        self.assertFalse(self.round_1.all_players_sang_their_points())
        self.player_2.declared_envido_points = 26
        self.player_2.save()
        self.assertTrue(self.round_1.all_players_sang_their_points())
        self.assertFalse(self.round_1.determine_if_team_is_a_liar(-1))
        self.assertTrue(self.round_1.determine_if_team_is_a_liar(1))

    def test_determine_round_winner(self):
        self.assertEqual(self.round_1.determine_round_winner(), self.player_2.team)
        self.player_1.card_1.set_from_tuple((10, 'b'))
        self.player_1.card_1.position = 1
        self.player_1.save()
        self.player_2.card_1.set_from_tuple((12, 'o'))
        self.player_2.card_1.position = 3
        self.player_2.save()
        self.assertEqual(self.round_1.determine_round_winner(), self.player_1.team)

    def test_get_max_score(self):
        # Funcion sirve para el caso de 4 o 6 jugadores para obtener la carta mas alta en mesa dentro del mismo equipo, mismo confromtamiento.... igual hago una simple pruebita
        self.assertEqual(self.round_1.get_max_score(self.round_1.game.player_set.all(), 1), self.player_2.card_3.get_score())
        self.assertEqual(self.round_1.get_max_score(self.round_1.game.player_set.all(), 2), self.player_1.card_2.get_score())
        self.assertEqual(self.round_1.get_max_score(self.round_1.game.player_set.all(), 3), self.player_2.card_1.get_score())

    def test_confront(self):
        self.assertEqual(self.round_1.confront(1), 1)
        self.assertEqual(self.round_1.confront(2), -1)
        self.assertEqual(self.round_1.confront(3), 1)

    def next_turn(self):
        pass      
    
    def try_finish(self):
        pass

    def finish(self):
        pass

    def test_increment_turn(self):
        self.round_1.increment_turn()
        self.assertEqual(self.round_1.current_turn, 1)

    def test_get_next_turn(self):
        self.round_1.get_next_turn()
        self.assertEqual(self.round_1.current_turn, 0)

    def is_finished(self):
        pass

    def test_entire_team_gone_to_mazo(self):
        self.player_1.gone_to_mazo = True
        self.player_1.save()
        self.assertTrue(self.round_1.entire_team_gone_to_mazo(-1))

    def test_assign_truco_points(self):
        self.tmgr.rechazar_ultimo_canto()    
        self.round_1.assign_truco_points(0)
        self.assertEqual(self.round_1.team_b_round_score, 1)
        self.assertEqual(self.round_1.team_a_round_score, 0)


class DetermineRoundWinnerFourPlayerTests(TestCase):
    def setUp(self):
        self.TEAM_A = -1
        self.TEAM_B = 1
        self.NO_TEAM = 0

        user_1 = User.objects.create_user(username='salo', password='123')
        user_2 = User.objects.create_user(username='nico', password='123')
        user_3 = User.objects.create_user(username='ngomez', password='123')
        user_4 = User.objects.create_user(username='nanom', password='123')
        
        card_1_p1 = Card.objects.create(anchor=1, number=1, palo='e')
        card_2_p1 = Card.objects.create(anchor=2, number=12, palo='c')
        card_3_p1 = Card.objects.create(anchor=3, number=3, palo='b')
        
        card_1_p2 = Card.objects.create(anchor=1, number=3, palo='e')
        card_2_p2 = Card.objects.create(anchor=2, number=10, palo='o')
        card_3_p2 = Card.objects.create(anchor=3, number=1, palo='o')
        
        card_1_p3 = Card.objects.create(anchor=1, number=5, palo='c')
        card_2_p3 = Card.objects.create(anchor=2, number=7, palo='e')
        card_3_p3 = Card.objects.create(anchor=3, number=2, palo='b')
        
        card_1_p4 = Card.objects.create(anchor=1, number=6, palo='c')
        card_2_p4 = Card.objects.create(anchor=2, number=7, palo='o')
        card_3_p4 = Card.objects.create(anchor=3, number=12, palo='b')
        
        
        game_1 = Game.objects.create(name='1', number_of_players=4)
        self.round_1= Round.objects.create(game=game_1)
        
        self.player_1= Player.objects.create(
            user=user_1,
            game=game_1,
            owner=True,
            card_1=card_1_p1,
            card_2=card_2_p1,
            card_3=card_3_p1,
            team=self.TEAM_A,
        )
        self.player_2= Player.objects.create(
            user=user_2,
            game=game_1,
            owner=False,
            card_1=card_1_p2,
            card_2=card_2_p2,
            card_3=card_3_p2,
            team=self.TEAM_B,
        )
        self.player_3= Player.objects.create(
            user=user_3,
            game=game_1,
            owner=False,
            card_1=card_1_p3,
            card_2=card_2_p3,
            card_3=card_3_p3,
            team=self.TEAM_A,
        )
        self.player_4= Player.objects.create(
            user=user_4,
            game=game_1,
            owner=False,
            card_1=card_1_p4,
            card_2=card_2_p4,
            card_3=card_3_p4,
            team=self.TEAM_B,
        )

    def test_c1a_c2b_c3a_wina(self):
        """
        Se testea quien es el ganadro de la ronda cuando:
        El equipo A gana el primer confrontamiento (c1a)
        El equipo B gana el segundo confrontamiento (c2b)
        El equipo A gana el Tercer confrontamiento (c3a)
        El equipo A gana la ronda (wina)
        """

        self.player_1.card_1.position = 1;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 3;self.player_1.card_3.save() 

        self.player_2.card_1.position = 2;self.player_2.card_1.save()
        self.player_2.card_2.position = 1;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 2;self.player_3.card_3.save() 

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 3;self.player_4.card_2.save()
        self.player_4.card_3.position = 2;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_A)
        self.assertEqual(self.round_1.confront(2), self.TEAM_B)
        self.assertEqual(self.round_1.confront(3), self.TEAM_A)

        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)

    def test_c1b_c2a_c3b_winb(self):

        self.player_1.card_1.position = 2;self.player_1.card_1.save()
        self.player_1.card_2.position = 1;self.player_1.card_2.save()
        self.player_1.card_3.position = 3;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 2;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 2;self.player_3.card_2.save()
        self.player_3.card_3.position = 3;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 3;self.player_4.card_2.save()
        self.player_4.card_3.position = 2;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_B)
        self.assertEqual(self.round_1.confront(2), self.TEAM_A)
        self.assertEqual(self.round_1.confront(3), self.TEAM_B)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_B)

    def test_c1b_c2b_winb(self):

        self.player_1.card_1.position = 3;self.player_1.card_1.save()
        self.player_1.card_2.position = 1;self.player_1.card_2.save()
        self.player_1.card_3.position = 2;self.player_1.card_3.save() 

        self.player_2.card_1.position = 2;self.player_2.card_1.save()
        self.player_2.card_2.position = 3;self.player_2.card_2.save()
        self.player_2.card_3.position = 1;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 2;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_B)
        self.assertEqual(self.round_1.confront(2), self.TEAM_B)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_B)

    def test_c1a_c2a_wina(self):

        self.player_1.card_1.position = 1;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 3;self.player_1.card_3.save() 

        self.player_2.card_1.position = 2;self.player_2.card_1.save()
        self.player_2.card_2.position = 1;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 2;self.player_3.card_2.save()
        self.player_3.card_3.position = 3;self.player_3.card_3.save()

        self.player_4.card_1.position = 3;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 1;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_A)
        self.assertEqual(self.round_1.confront(2), self.TEAM_A)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)

    def test_c1b_c2a_c3a_wina(self):

        self.player_1.card_1.position = 3;self.player_1.card_1.save()
        self.player_1.card_2.position = 1;self.player_1.card_2.save()
        self.player_1.card_3.position = 2;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 2;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 2;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 3;self.player_4.card_2.save()
        self.player_4.card_3.position = 2;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_B)
        self.assertEqual(self.round_1.confront(2), self.TEAM_A)
        self.assertEqual(self.round_1.confront(3), self.TEAM_A)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)
        
    def test_c1a_c2b_c3b_winb(self):

        self.player_1.card_1.position = 1;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 3;self.player_1.card_3.save() 

        self.player_2.card_1.position = 2;self.player_2.card_1.save()
        self.player_2.card_2.position = 1;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 3;self.player_3.card_1.save()
        self.player_3.card_2.position = 1;self.player_3.card_2.save()
        self.player_3.card_3.position = 2;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 3;self.player_4.card_2.save()
        self.player_4.card_3.position = 2;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_A)
        self.assertEqual(self.round_1.confront(2), self.TEAM_B)
        self.assertEqual(self.round_1.confront(3), self.TEAM_B)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_B)

    def test_c1noTeam_c2a_wina(self):

        self.player_1.card_1.position = 2;self.player_1.card_1.save()
        self.player_1.card_2.position = 3;self.player_1.card_2.save()
        self.player_1.card_3.position = 1;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 3;self.player_2.card_2.save()
        self.player_2.card_3.position = 2;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 2;self.player_3.card_2.save()
        self.player_3.card_3.position = 3;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(2), self.TEAM_A)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)

    def test_c1noTeam_c2b_winb(self):

        self.player_1.card_1.position = 3;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 1;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 2;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 2;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(2), self.TEAM_B)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_B)

    def test_c1noTeam_c2noTeam_c3a_wina(self):

        self.player_1.card_1.position = 3;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 1;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 2;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 2;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 1;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 3;self.player_4.card_2.save()
        self.player_4.card_3.position = 2;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(2), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(3), self.TEAM_A)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)

    def test_c1a_c2noTeam__wina(self):

        self.player_1.card_1.position = 1;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 3;self.player_1.card_3.save() 

        self.player_2.card_1.position = 3;self.player_2.card_1.save()
        self.player_2.card_2.position = 2;self.player_2.card_2.save()
        self.player_2.card_3.position = 1;self.player_2.card_3.save() 

        self.player_3.card_1.position = 2;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 1;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 3;self.player_4.card_2.save()
        self.player_4.card_3.position = 2;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_A)
        self.assertEqual(self.round_1.confront(2), self.NO_TEAM)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)

    def test_c1b_c2noTeam__winb(self):

        self.player_1.card_1.position = 3;self.player_1.card_1.save()
        self.player_1.card_2.position = 1;self.player_1.card_2.save()
        self.player_1.card_3.position = 2;self.player_1.card_3.save() 

        self.player_2.card_1.position = 2;self.player_2.card_1.save()
        self.player_2.card_2.position = 3;self.player_2.card_2.save()
        self.player_2.card_3.position = 1;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 2;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 3;self.player_4.card_2.save()
        self.player_4.card_3.position = 2;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_B)
        self.assertEqual(self.round_1.confront(2), self.NO_TEAM)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_B)

    def test_c1noTeam_c2noTeamb_c3noTeam_winmanoTeam(self):

        #Re-seteo valores de cartas para este caso especial
        self.player_1.card_1.set_from_tuple( (12,'c') )
        self.player_1.card_2.set_from_tuple( (1,'c') )
        self.player_1.card_3.set_from_tuple( (7,'b') )

        self.player_2.card_1.set_from_tuple( (4,'b') )
        self.player_2.card_2.set_from_tuple( (10,'e') )
        self.player_2.card_3.set_from_tuple( (5,'b') )

        self.player_3.card_1.set_from_tuple( (4,'o') )
        self.player_3.card_2.set_from_tuple( (11,'c') )
        self.player_3.card_3.set_from_tuple( (6,'o') )

        self.player_4.card_1.set_from_tuple( (12,'b') )
        self.player_4.card_2.set_from_tuple( (1,'o') )
        self.player_4.card_3.set_from_tuple( (7,'c') )

        # Mano de la ronda, Player1 , perteneciente a TEAM_A
        self.player_1.place_on_table = 0;self.player_1.save()
        self.player_2.place_on_table = 1;self.player_2.save()
        self.player_3.place_on_table = 2;self.player_3.save()    
        self.player_4.place_on_table = 3;self.player_4.save()

        #Asigno posiciones de cartas
        self.player_1.card_1.position = 1;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 3;self.player_1.card_3.save() 

        self.player_2.card_1.position = 2;self.player_2.card_1.save()
        self.player_2.card_2.position = 1;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 2;self.player_3.card_2.save()
        self.player_3.card_3.position = 3;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(2), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(3), self.NO_TEAM)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)    

class DetermineRoundWinnerSixPlayerTests(TestCase):
    def setUp(self):
        self.TEAM_A = -1
        self.TEAM_B = 1
        self.NO_TEAM = 0

        user_1 = User.objects.create_user(username='salo', password='123')
        user_2 = User.objects.create_user(username='nico', password='123')
        user_3 = User.objects.create_user(username='ngomez', password='123')
        user_4 = User.objects.create_user(username='nanom', password='123')
        user_5 = User.objects.create_user(username='invitado1', password='123')
        user_6 = User.objects.create_user(username='invitado2', password='123')
        
        card_1_p1 = Card.objects.create(anchor=1, number=7, palo='c')
        card_2_p1 = Card.objects.create(anchor=2, number=12, palo='c')
        card_3_p1 = Card.objects.create(anchor=3, number=3, palo='b')
        
        card_1_p2 = Card.objects.create(anchor=1, number=3, palo='e')
        card_2_p2 = Card.objects.create(anchor=2, number=10, palo='o')
        card_3_p2 = Card.objects.create(anchor=3, number=1, palo='o')
        
        card_1_p3 = Card.objects.create(anchor=1, number=5, palo='c')
        card_2_p3 = Card.objects.create(anchor=2, number=7, palo='o')
        card_3_p3 = Card.objects.create(anchor=3, number=2, palo='b')
        
        card_1_p4 = Card.objects.create(anchor=1, number=6, palo='c')
        card_2_p4 = Card.objects.create(anchor=2, number=7, palo='b')
        card_3_p4 = Card.objects.create(anchor=3, number=12, palo='b')

        card_1_p5 = Card.objects.create(anchor=1, number=12, palo='e')
        card_2_p5 = Card.objects.create(anchor=2, number=1, palo='c')
        card_3_p5 = Card.objects.create(anchor=3, number=6, palo='e')

        card_1_p6 = Card.objects.create(anchor=1, number=11, palo='o')
        card_2_p6 = Card.objects.create(anchor=2, number=5, palo='b')
        card_3_p6 = Card.objects.create(anchor=3, number=10, palo='b')
        
        
        game_1 = Game.objects.create(name='1', number_of_players=4)
        self.round_1= Round.objects.create(game=game_1)
        
        self.player_1= Player.objects.create(
            user=user_1,
            game=game_1,
            owner=True,
            card_1=card_1_p1,
            card_2=card_2_p1,
            card_3=card_3_p1,
            team=self.TEAM_A,
        )
        self.player_2= Player.objects.create(
            user=user_2,
            game=game_1,
            owner=False,
            card_1=card_1_p2,
            card_2=card_2_p2,
            card_3=card_3_p2,
            team=self.TEAM_B,
        )
        self.player_3= Player.objects.create(
            user=user_3,
            game=game_1,
            owner=False,
            card_1=card_1_p3,
            card_2=card_2_p3,
            card_3=card_3_p3,
            team=self.TEAM_A,
        )
        self.player_4= Player.objects.create(
            user=user_4,
            game=game_1,
            owner=False,
            card_1=card_1_p4,
            card_2=card_2_p4,
            card_3=card_3_p4,
            team=self.TEAM_B,
        )
        self.player_5= Player.objects.create(
            user=user_5,
            game=game_1,
            owner=False,
            card_1=card_1_p5,
            card_2=card_2_p5,
            card_3=card_3_p5,
            team=self.TEAM_A,
        )
        self.player_6= Player.objects.create(
            user=user_6,
            game=game_1,
            owner=False,
            card_1=card_1_p6,
            card_2=card_2_p6,
            card_3=card_3_p6,
            team=self.TEAM_B,
        )

    def test_c1a_c2b_c3a_wina(self):#aba
        self.player_1.card_1.position = 3;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 1;self.player_1.card_3.save() 

        self.player_2.card_1.position = 2;self.player_2.card_1.save()
        self.player_2.card_2.position = 1;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 2;self.player_3.card_3.save()

        self.player_4.card_1.position = 3;self.player_4.card_1.save()
        self.player_4.card_2.position = 1;self.player_4.card_2.save()
        self.player_4.card_3.position = 2;self.player_4.card_3.save() 

        self.player_5.card_1.position = 2;self.player_5.card_1.save()
        self.player_5.card_2.position = 3;self.player_5.card_2.save()
        self.player_5.card_3.position = 1;self.player_5.card_3.save() 

        self.player_6.card_1.position = 2;self.player_6.card_1.save()
        self.player_6.card_2.position = 1;self.player_6.card_2.save()
        self.player_6.card_3.position = 3;self.player_6.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_A)
        self.assertEqual(self.round_1.confront(2), self.TEAM_B)
        self.assertEqual(self.round_1.confront(3), self.TEAM_A)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)
    
    def test_c1b_c2a_c3b_winb(self):#bab
        self.player_1.card_1.position = 3;self.player_1.card_1.save()
        self.player_1.card_2.position = 1;self.player_1.card_2.save()
        self.player_1.card_3.position = 2;self.player_1.card_3.save() 

        self.player_2.card_1.position = 3;self.player_2.card_1.save()
        self.player_2.card_2.position = 2;self.player_2.card_2.save()
        self.player_2.card_3.position = 1;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 2;self.player_3.card_2.save()
        self.player_3.card_3.position = 3;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.player_5.card_1.position = 1;self.player_5.card_1.save()
        self.player_5.card_2.position = 2;self.player_5.card_2.save()
        self.player_5.card_3.position = 3;self.player_5.card_3.save() 

        self.player_6.card_1.position = 1;self.player_6.card_1.save()
        self.player_6.card_2.position = 2;self.player_6.card_2.save()
        self.player_6.card_3.position = 3;self.player_6.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_B)
        self.assertEqual(self.round_1.confront(2), self.TEAM_A)
        self.assertEqual(self.round_1.confront(3), self.TEAM_B)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_B)
    

    def test_c1a_c2b_c3b_winb(self):#abb
        self.player_1.card_1.position = 2;self.player_1.card_1.save()
        self.player_1.card_2.position = 3;self.player_1.card_2.save()
        self.player_1.card_3.position = 1;self.player_1.card_3.save() 

        self.player_2.card_1.position = 3;self.player_2.card_1.save()
        self.player_2.card_2.position = 1;self.player_2.card_2.save()
        self.player_2.card_3.position = 2;self.player_2.card_3.save() 

        self.player_3.card_1.position = 2;self.player_3.card_1.save()
        self.player_3.card_2.position = 1;self.player_3.card_2.save()
        self.player_3.card_3.position = 3;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.player_5.card_1.position = 3;self.player_5.card_1.save()
        self.player_5.card_2.position = 1;self.player_5.card_2.save()
        self.player_5.card_3.position = 2;self.player_5.card_3.save() 

        self.player_6.card_1.position = 1;self.player_6.card_1.save()
        self.player_6.card_2.position = 2;self.player_6.card_2.save()
        self.player_6.card_3.position = 3;self.player_6.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_A)
        self.assertEqual(self.round_1.confront(2), self.TEAM_B)
        self.assertEqual(self.round_1.confront(3), self.TEAM_B)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_B)

    def test_c1b_c2a_c3a_wina(self):#baa
        self.player_1.card_1.position = 3;self.player_1.card_1.save()
        self.player_1.card_2.position = 1;self.player_1.card_2.save()
        self.player_1.card_3.position = 2;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 3;self.player_2.card_2.save()
        self.player_2.card_3.position = 2;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 2;self.player_3.card_3.save()

        self.player_4.card_1.position = 3;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 1;self.player_4.card_3.save() 

        self.player_5.card_1.position = 3;self.player_5.card_1.save()
        self.player_5.card_2.position = 2;self.player_5.card_2.save()
        self.player_5.card_3.position = 1;self.player_5.card_3.save() 

        self.player_6.card_1.position = 1;self.player_6.card_1.save()
        self.player_6.card_2.position = 2;self.player_6.card_2.save()
        self.player_6.card_3.position = 3;self.player_6.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_B)
        self.assertEqual(self.round_1.confront(2), self.TEAM_A)
        self.assertEqual(self.round_1.confront(3), self.TEAM_A)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)


    def test_c1noTeam_c2a_wina(self):#_a
        self.player_1.card_1.position = 3;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 1;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 2;self.player_2.card_2.save()
        self.player_2.card_3.position = 3;self.player_2.card_3.save() 

        self.player_3.card_1.position = 1;self.player_3.card_1.save()
        self.player_3.card_2.position = 2;self.player_3.card_2.save()
        self.player_3.card_3.position = 3;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.player_5.card_1.position = 1;self.player_5.card_1.save()
        self.player_5.card_2.position = 2;self.player_5.card_2.save()
        self.player_5.card_3.position = 3;self.player_5.card_3.save() 

        self.player_6.card_1.position = 1;self.player_6.card_1.save()
        self.player_6.card_2.position = 2;self.player_6.card_2.save()
        self.player_6.card_3.position = 3;self.player_6.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(2), self.TEAM_A)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)

    def test_c1noTeam_c2b_winb(self):#_b
        self.player_1.card_1.position = 2;self.player_1.card_1.save()
        self.player_1.card_2.position = 3;self.player_1.card_2.save()
        self.player_1.card_3.position = 1;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 3;self.player_2.card_2.save()
        self.player_2.card_3.position = 2;self.player_2.card_3.save() 

        self.player_3.card_1.position = 2;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 1;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.player_5.card_1.position = 1;self.player_5.card_1.save()
        self.player_5.card_2.position = 3;self.player_5.card_2.save()
        self.player_5.card_3.position = 2;self.player_5.card_3.save() 

        self.player_6.card_1.position = 1;self.player_6.card_1.save()
        self.player_6.card_2.position = 2;self.player_6.card_2.save()
        self.player_6.card_3.position = 3;self.player_6.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(2), self.TEAM_B)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_B)

    def test_c1noTeam_c2noTeam_c3a_wina(self):#__a
        self.player_1.card_1.position = 2;self.player_1.card_1.save()
        self.player_1.card_2.position = 3;self.player_1.card_2.save()
        self.player_1.card_3.position = 1;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 3;self.player_2.card_2.save()
        self.player_2.card_3.position = 2;self.player_2.card_3.save() 

        self.player_3.card_1.position = 2;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 1;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.player_5.card_1.position = 1;self.player_5.card_1.save()
        self.player_5.card_2.position = 2;self.player_5.card_2.save()
        self.player_5.card_3.position = 3;self.player_5.card_3.save() 

        self.player_6.card_1.position = 1;self.player_6.card_1.save()
        self.player_6.card_2.position = 2;self.player_6.card_2.save()
        self.player_6.card_3.position = 3;self.player_6.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(2), self.NO_TEAM)
        self.assertEqual(self.round_1.confront(3), self.TEAM_A)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)

    def test_c1a_c2noTeam_wina(self):#a_
        self.player_1.card_1.position = 2;self.player_1.card_1.save()
        self.player_1.card_2.position = 3;self.player_1.card_2.save()
        self.player_1.card_3.position = 1;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 3;self.player_2.card_2.save()
        self.player_2.card_3.position = 2;self.player_2.card_3.save() 

        self.player_3.card_1.position = 2;self.player_3.card_1.save()
        self.player_3.card_2.position = 1;self.player_3.card_2.save()
        self.player_3.card_3.position = 3;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.player_5.card_1.position = 1;self.player_5.card_1.save()
        self.player_5.card_2.position = 2;self.player_5.card_2.save()
        self.player_5.card_3.position = 3;self.player_5.card_3.save() 

        self.player_6.card_1.position = 1;self.player_6.card_1.save()
        self.player_6.card_2.position = 2;self.player_6.card_2.save()
        self.player_6.card_3.position = 3;self.player_6.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_A)
        self.assertEqual(self.round_1.confront(2), self.NO_TEAM)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_A)

    def test_c1b_c2noTeam_winb(self):#b_
        self.player_1.card_1.position = 1;self.player_1.card_1.save()
        self.player_1.card_2.position = 2;self.player_1.card_2.save()
        self.player_1.card_3.position = 3;self.player_1.card_3.save() 

        self.player_2.card_1.position = 1;self.player_2.card_1.save()
        self.player_2.card_2.position = 3;self.player_2.card_2.save()
        self.player_2.card_3.position = 2;self.player_2.card_3.save() 

        self.player_3.card_1.position = 2;self.player_3.card_1.save()
        self.player_3.card_2.position = 3;self.player_3.card_2.save()
        self.player_3.card_3.position = 1;self.player_3.card_3.save()

        self.player_4.card_1.position = 1;self.player_4.card_1.save()
        self.player_4.card_2.position = 2;self.player_4.card_2.save()
        self.player_4.card_3.position = 3;self.player_4.card_3.save() 

        self.player_5.card_1.position = 1;self.player_5.card_1.save()
        self.player_5.card_2.position = 2;self.player_5.card_2.save()
        self.player_5.card_3.position = 3;self.player_5.card_3.save() 

        self.player_6.card_1.position = 1;self.player_6.card_1.save()
        self.player_6.card_2.position = 2;self.player_6.card_2.save()
        self.player_6.card_3.position = 3;self.player_6.card_3.save() 

        self.assertEqual(self.round_1.confront(1), self.TEAM_B)
        self.assertEqual(self.round_1.confront(2), self.NO_TEAM)
        self.assertEqual(self.round_1.determine_round_winner(), self.TEAM_B)