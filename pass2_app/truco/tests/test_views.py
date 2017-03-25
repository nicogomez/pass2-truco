# -*- encoding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from truco.models import *


class LoggedUserTests(TestCase):

    fixtures = ['truco_1_fixture']

    def setUp(self):
        self.c = Client()
        self.c.post('/login/', {'username':'nicobella','password':'123'})

    def test_login(self):
        response = self.c.get(reverse('truco:index'))
        self.assertEqual(response.status_code, 200)

    def test_bad_login(self):
        c_bad_login = Client()
        response_bad_pass = c_bad_login.post(reverse('login'), {'username':'nano','password':'bad_pass'})
        self.assertEqual(response_bad_pass.status_code, 200)
        self.assertContains(response_bad_pass, "Please enter a correct username and password")

    def test_logout(self):
        response = self.c.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('login'), status_code=302, target_status_code=200)

        self.c.get(reverse('truco:index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('login'), status_code=302, target_status_code=200)    


class OnRoomContainsTest(TestCase):

    fixtures = ['truco_1_fixture']

    def setUp(self):
        self.c1 = Client()
        self.c1.post('/login/', {'username':'nicobella','password':'123'})

        self.c2 = Client()
        self.c2.post('/login/', {'username':'nano','password':'123'})

    def test_room_creation(self):
        response = self.c1.post(reverse('truco:index'), {'name':'altamesa', 'number_of_players':2, 'score_limit':15 }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Partida creada exitosamente')
        self.assertRedirects(response, reverse('truco:room', args=(1,)), status_code=302, target_status_code=200)

        self.assertEqual(Game.objects.filter(name='altamesa').exists(), True)

    def test_creating_and_leaving_room(self):
        self.c1.post(reverse('truco:index'), {'name':'altamesa', 'number_of_players':2, 'score_limit':15 }, follow=True)

        response = self.c1.get(reverse('truco:giveup-game', args=(1,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('truco:index'), status_code=302, target_status_code=200)

    def test_game_started_ok(self):
        response = self.c1.post(reverse('truco:index'),{'name':'mesacheck', 'number_of_players':2, 'score_limit':15 }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Partida creada exitosamente')

        response_c2 = self.c2.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response_c2.status_code, 200)
        self.assertEqual(len(Game.objects.get(name='mesacheck').player_set.all()), 2)

        #Jugador c1 inicia partida
        response_init_partida = self.c1.post(reverse('truco:start-game', args=(1,)), follow=True)
        self.assertEqual(response_init_partida.status_code, 200)
        self.assertContains(response_init_partida, "La partida ha iniciado exitosamente")

    def test_game_started_fail_for_insufficient_players(self):
        response = self.c1.post(reverse('truco:index'),{'name':'mesacheck', 'number_of_players':2, 'score_limit':15 }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Partida creada exitosamente')
        self.assertEqual(len(Game.objects.get(name='mesacheck').player_set.all()), 1)

        #Jugador c1 inicia partida
        response_init_partida = self.c1.post(reverse('truco:start-game', args=(1,)), follow=True)
        self.assertContains(response_init_partida, "La partida aún no puede comenzar")
        

class IntruderUserTests_two_players(TestCase):

    fixtures = ['truco_1_fixture']

    def setUp(self):
        self.normal_client = Client()
        self.normal_client.post('/login/', {'username':'nicobella','password':'123'})

        self.normal_client2 = Client()
        self.normal_client2.post('/login/', {'username':'nano','password':'123'})

        self.intruder_client = Client()
        self.intruder_client.post('/login/', {'username':'nicogomez','password':'123'})

    def test_intruder_trying_to_join_full_room(self):
        self.normal_client.post(reverse('truco:index'), {'name':'altamesa', 'number_of_players':2, 'score_limit':15 }, follow=True)

        self.assertEqual(len(Game.objects.get(name='altamesa').player_set.all()), 1)

        join_room_response = self.normal_client2.get(reverse('truco:room', args=(1,)), follow=True)
        self.assertEqual(join_room_response.status_code, 200)

        self.assertEqual(len(Game.objects.get(name='altamesa').player_set.all()), 2)

        intruder_join_response = self.intruder_client.get(reverse('truco:room', args=(1,)), follow=True)

        self.assertEqual(len(Game.objects.get(name='altamesa').player_set.all()), 2)
        self.assertRedirects(intruder_join_response, reverse('truco:index'), status_code=302, target_status_code=200)

        self.assertContains(intruder_join_response, 'La cantidad de jugadores alcanzo el maximo', count=None)

    def test_trying_to_join_room_when_already_have_one(self):
        self.normal_client.post(reverse('truco:index'), {'name':'altamesa', 'number_of_players':2, 'score_limit':15 }, follow=True)
        self.normal_client2.post(reverse('truco:index'), {'name':'otramesa', 'number_of_players':2, 'score_limit':15 }, follow=True)

        response = self.normal_client.get(reverse('truco:index'), follow=True)
        self.assertEqual(response.status_code, 200)

        second_response = self.normal_client.get(reverse('truco:room', args=(2,)), follow=True)
        self.assertEqual(second_response.status_code, 200)
        self.assertContains(second_response, 'Usted ya pertenece a otra partida')


class IntruderUserTests_more_than_two_players(TestCase):
    
    fixtures = ['truco_1_fixture']

    def setUp(self):
        self.c1 = Client()
        self.c1.post('/login/', {'username':'salome','password':'123'})

        self.c2 = Client()
        self.c2.post('/login/', {'username':'nicobella','password':'123'})

        self.c3 = Client()
        self.c3.post('/login/', {'username':'nicogomez','password':'123'})

        self.c4 = Client()
        self.c4.post('/login/', {'username':'nano','password':'123'})

        self.c5 = Client()
        self.c5.post('/login/', {'username':'agente007','password':'123'})

        self.c6 = Client()
        self.c6.post('/login/', {'username':'ironman','password':'123'})

        self.c_intruder = Client()
        self.c_intruder.post('/login/', {'username':'admin','password':'admin'})

    def test_intruder_trying_to_join_full_room_four_players(self):

        self.c1.post(reverse('truco:index'), {'name':'mesade4', 'number_of_players':4, 'score_limit':15 }, follow=True)
        mesade4 = Game.objects.get(name='mesade4')
        self.assertEqual(len(mesade4.player_set.all()), 1)

        response_c2 = self.c2.get(reverse('truco:room', args=(mesade4.pk,)), follow= True)
        self.assertEqual(response_c2.status_code, 200)
        self.assertEqual(len(mesade4.player_set.all()), 2)

        response_c3 = self.c3.get(reverse('truco:room', args=(mesade4.pk,)), follow= True)
        self.assertEqual(response_c3.status_code, 200)
        self.assertEqual(len(mesade4.player_set.all()), 3)

        response_c4 = self.c4.get(reverse('truco:room', args=(mesade4.pk,)), follow= True)
        self.assertEqual(response_c4.status_code, 200)
        self.assertEqual(len(mesade4.player_set.all()), 4)

        response_c_intruder = self.c_intruder.get(reverse('truco:room', args=(mesade4.pk,)), follow= True)
        self.assertContains(response_c_intruder, 'La cantidad de jugadores alcanzo el maximo')

    def test_intruder_trying_to_join_full_room_six_players(self):

        self.c1.post(reverse('truco:index'), {'name':'mesade6', 'number_of_players':6, 'score_limit':15 }, follow=True)
        mesade6 = Game.objects.get(name='mesade6')
        self.assertEqual(len(mesade6.player_set.all()), 1)

        response_c2 = self.c2.get(reverse('truco:room', args=(mesade6.pk,)), follow= True)
        self.assertEqual(response_c2.status_code, 200)
        self.assertEqual(len(mesade6.player_set.all()), 2)

        response_c3 = self.c3.get(reverse('truco:room', args=(mesade6.pk,)), follow= True)
        self.assertEqual(response_c3.status_code, 200)
        self.assertEqual(len(mesade6.player_set.all()), 3)

        response_c4 = self.c4.get(reverse('truco:room', args=(mesade6.pk,)), follow= True)
        self.assertEqual(response_c4.status_code, 200)
        self.assertEqual(len(mesade6.player_set.all()), 4)

        response_c5 = self.c5.get(reverse('truco:room', args=(mesade6.pk,)), follow= True)
        self.assertEqual(response_c5.status_code, 200)
        self.assertEqual(len(mesade6.player_set.all()), 5)

        response_c6 = self.c6.get(reverse('truco:room', args=(mesade6.pk,)), follow= True)
        self.assertEqual(response_c6.status_code, 200)
        self.assertEqual(len(mesade6.player_set.all()), 6)

        response_c_intruder = self.c_intruder.get(reverse('truco:room', args=(mesade6.pk,)), follow= True)
        self.assertContains(response_c_intruder, 'La cantidad de jugadores alcanzo el maximo')


class CantosDeclarationTest(TestCase):
    """
    Test de vista para el contenido del Room para verificar las 
    declaraciones posibles
    """
    fixtures = ['truco_1_fixture']

    def setUp(self):
        client = Client()
        client.post('/login/', {'username':'nicobella','password':'123'})

        client2 = Client()
        client2.post('/login/', {'username':'nano','password':'123'})

        client.post(reverse('truco:index'), {'name':'altamesa', 'number_of_players':2, 'score_limit':15 }, follow=True)
        client2.get(reverse('truco:room', args=(1,)), follow=True)

        client.post(reverse('truco:start-game', args=(1,)), follow=True)

        if Player.objects.get(pk=1).is_my_turn():
            self.mano_client = client
            self.dealer_client = client2
        else:
            self.mano_client = client2
            self.dealer_client = client

    def test_declaration_info_shown(self):
        response = self.mano_client.get(reverse('truco:room', args=(1,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cantar Envido')

        response = self.dealer_client.get(reverse('truco:room', args=(1,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Cantar Envido')
        
    def test_declare_envido(self):
        response = self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.ENVIDO, )), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Envido declarado')
        self.assertNotContains(response, 'Cantar Truco')
        
        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'El contrincante canto Envido')

    def test_envido_acepted(self):
        self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.ENVIDO, )), follow=True)

        response_dealer = self.dealer_client.post(reverse('truco:process-aceptar-envido', args=(1,)), follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'Cante sus Puntos')

        response = self.mano_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response.status_code, 200)
        #self.assertContains(response, 'Envido aceptado')
        self.assertContains(response, 'Cante sus Puntos')

    def test_declare_segundo_envido(self):
        #Previo al canto de envido por player mano
        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertNotContains(response_dealer, 'Cantar Segundo envido')

        response = self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.ENVIDO, )), follow=True)
        self.assertEqual(response.status_code, 200)

        #Posterior al canto de envido por jugador mano
        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'Cantar Segundo envido')

        #Canto de segundo envido por parte de dealer
        response_dealer = self.dealer_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.ENVIDO_ENVIDO, )), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response_dealer, 'Segundo envido declarado')

        response = self.mano_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'El contrincante canto Segundo envido')
        self.assertNotContains(response_dealer, 'Cantar Segundo envido')

    def test_segundo_envido_acepted(self):
        #Declaracion de envido
        self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.ENVIDO, )), follow=True)
        #Declaracion de segundo envido
        self.dealer_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.ENVIDO_ENVIDO, )), follow=True)

        #Aceptacion de segundo envido
        response = self.mano_client.post(reverse('truco:process-aceptar-envido', args=(1,)), follow=True)
        self.assertEqual(response.status_code, 200)
        
        #Post aceptacion de segundo envido
        self.assertContains(response, 'Cante sus Puntos')

        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1,)), follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'Cante sus Puntos')

    def test_declare_real_envido(self):
        response = self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.REAL_ENVIDO, )), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Real envido declarado')

        #Posterior al canto de real envido por jugador mano
        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'El contrincante canto Real envido')
        self.assertNotContains(response_dealer, 'Cantar Envido')
        self.assertNotContains(response_dealer, 'Cantar Segundo envido')
        self.assertNotContains(response_dealer, 'Cantar Real envido')
        self.assertNotContains(response_dealer, 'Cantar Truco')


    def test_real_envido_acepted(self):
        #Declaracion de real envido
        self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.REAL_ENVIDO, )), follow=True)
        
        #Aceptacion de real envido
        response_dealer = self.dealer_client.post(reverse('truco:process-aceptar-envido', args=(1,)), follow=True)
        self.assertEqual(response_dealer.status_code, 200)

        #Post aceptacion de real envido
        self.assertContains(response_dealer, 'Cante sus Puntos')

        response = self.mano_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cante sus Puntos')


    def test_declare_falta_envido(self):
        response = self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.FALTA_ENVIDO, )), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Falta envido declarado')

        #Posterior al canto de falta envido por jugador mano
        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'El contrincante canto Falta envido')
        self.assertNotContains(response_dealer, 'Cantar Envido')
        self.assertNotContains(response_dealer, 'Cantar Segundo envido')
        self.assertNotContains(response_dealer, 'Cantar Real envido')
        self.assertNotContains(response_dealer, 'Cantar Falta envido')
        self.assertNotContains(response_dealer, 'Cantar Truco')


    def test_falta_envido_acepted(self):
        #Declaracion de real envido
        self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.FALTA_ENVIDO, )), follow=True)
        
        #Aceptacion de real envido
        response_dealer = self.dealer_client.post(reverse('truco:process-aceptar-envido', args=(1,)), follow=True)
        self.assertEqual(response_dealer.status_code, 200)

        #Post aceptacion de real envido
        self.assertContains(response_dealer, 'Cante sus Puntos')

        response = self.mano_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cante sus Puntos')


    def test_truco(self):
        response = self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.TRUCO, )), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Truco declarado')

        #Posterior al canto del truco por jugador mano
        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'El contrincante canto Truco')
        self.assertNotContains(response_dealer, 'Cantar Truco')
        self.assertContains(response_dealer, 'Cantar Retruco')

        #Aceptacion de Retruco por dealer_client
        response_truco_acepted = self.dealer_client.post(reverse('truco:process-aceptar-truco', args=(1, )), follow=True)
        self.assertEqual(response_truco_acepted.status_code, 200)

    def test_retruco(self):
        self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.TRUCO, )), follow=True)
        response_dealer = self.dealer_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.RETRUCO, )), follow=True)

        #Posterior al canto del retruco por jugador dealer
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'Retruco declarado')

        response_mano = self.mano_client.get(reverse('truco:room', args=(1, )), follow=True)
        self.assertEqual(response_mano.status_code, 200)
        self.assertContains(response_mano, 'El contrincante canto Retruco')
        self.assertNotContains(response_mano, 'Cantar Truco')
        self.assertNotContains(response_mano, 'Cantar Retruco')
        self.assertContains(response_mano, 'Cantar Vale Cuatro')

        #Aceptacion de retruco
        response_retruco_acepted = self.mano_client.post(reverse('truco:process-aceptar-truco', args=(1, )), follow=True)
        self.assertEqual(response_retruco_acepted.status_code, 200)

    def test_vale_cuatro(self):
        self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.TRUCO, )), follow=True)
        self.dealer_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.RETRUCO, )), follow=True)

        #declaracion de vale_cuatro
        response_vale_cuatro_delared = self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.VALE_CUATRO, )), follow=True)
        self.assertEqual(response_vale_cuatro_delared.status_code, 200)
        self.assertContains(response_vale_cuatro_delared, 'Vale Cuatro declarado')

        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1,)), follow= True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'El contrincante canto Vale Cuatro')

        #Aceptacion de vale cuatro
        response_vale_cuatro_acepted = self.mano_client.post(reverse('truco:process-aceptar-truco', args=(1, )), follow=True)
        self.assertEqual(response_vale_cuatro_acepted.status_code, 200)


    def test_goto_mazo(self):
        response = self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.IR_AL_MAZO, )), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ir al mazo declarado')

        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1,)), follow= True)
        self.assertEqual(response_dealer.status_code, 200)

        self.assertContains(response_dealer, 'Info de Ronda')


    def test_declared_truco_and_envido(self):
        # Cliente mano declara Truco
        response_truco_declared = self.mano_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.TRUCO, )), follow=True)
        self.assertEqual(response_truco_declared.status_code, 200)
        self.assertContains(response_truco_declared, 'Truco declarado')

        response_dealer = self.dealer_client.get(reverse('truco:room', args=(1,)), follow= True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'El contrincante canto Truco')

        #Cliente dealer declara envido
        response_envido_declared = self.dealer_client.post(reverse('truco:process-canto-declaration', args=(1, Canto.TipoCanto.ENVIDO, )), follow=True)
        self.assertEqual(response_envido_declared.status_code, 200)
        self.assertContains(response_envido_declared, 'Envido declarado')      

        response_mano = self.mano_client.get(reverse('truco:room', args=(1,)), follow= True)
        self.assertEqual(response_mano.status_code, 200)
        self.assertContains(response_mano, 'El contrincante canto Envido')

        #Cliente mano acepta envido
        response_envido_acepted = self.mano_client.post(reverse('truco:process-aceptar-envido', args=(1,)), follow=True)
        self.assertEqual(response_envido_acepted.status_code, 200)
        self.assertContains(response_envido_acepted, 'Cante sus Puntos')

        #Cantan puntos
        response_dealer = self.dealer_client.post(reverse('truco:send-envido-points', args=(1,)), {'points':30}, follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'Puntos de envido: 30')
        
        response = self.mano_client.post(reverse('truco:send-envido-points', args=(1,)), {'points':33}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Puntos de envido: 33')

        #Luego le re aparece el cuadro de aceptacion de truco pendiente a cliente dealer
        response_dealer = self.dealer_client.post(reverse('truco:room', args=(1,)), follow=True)
        self.assertEqual(response_dealer.status_code, 200)
        self.assertContains(response_dealer, 'El contrincante canto Truco')

    def test_send_envido_points(self):
        response_dealer = self.dealer_client.post(reverse('truco:send-envido-points', args=(1,)), {'points':30}, follow=True)
        response = self.mano_client.post(reverse('truco:send-envido-points', args=(1,)), {'points':33}, follow=True)

        self.assertContains(response, 'Puntos de envido: 33')
        self.assertContains(response, 'Puntos de envido: 30')
        self.assertContains(response_dealer, 'Puntos de envido: 30')

    def test_send_empty_envido_points(self):
        response = self.mano_client.post(reverse('truco:send-envido-points', args=(1,)), {'points':''}, follow=True)
        self.assertContains(response, 'Debe ingresar una cantidad de puntos')
