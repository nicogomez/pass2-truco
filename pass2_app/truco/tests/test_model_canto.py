from django.test import TestCase
from truco.models import *
from django.contrib.auth.models import User

class CantoTests(TestCase):
    def setUp(self):

        game_1 = Game.objects.create(name='1', team_a_score=6, team_b_score=10)
        game_1.round= Round()
        game_1.round.save()
        game_1.round.init_canto_managers()
        game_1.round.save()
        emgr = EnvidoManager.objects.get(round=game_1.round)
        tmgr = TrucoManager.objects.get(round=game_1.round)
        
        self.envido_canto = emgr.canto_set.create()
        self.envido_envido = emgr.canto_set.create()
        self.real_envido = emgr.canto_set.create()
        self.falta_envido = emgr.canto_set.create()
        self.truco = tmgr.canto_set.create()
        self.retruco = tmgr.canto_set.create()
        self.vale_cuatro = tmgr.canto_set.create()

    def test_set_canto(self):
        # import ipdb; ipdb.set_trace()

        self.envido_canto.set_canto(1)
        self.assertEqual(self.envido_canto.puntos, 2)
        self.assertEqual(self.envido_canto.tipo_de_canto, Canto.TipoCanto.ENVIDO)
        self.assertEqual(self.envido_canto.estado, 1)
        self.assertEqual(self.envido_canto.indice, 1)
        self.assertIsInstance(self.envido_canto.canto_manager, EnvidoManager)

        self.envido_envido.set_canto(2)
        self.assertEqual(self.envido_envido.puntos, 2)
        self.assertEqual(self.envido_envido.tipo_de_canto, Canto.TipoCanto.ENVIDO_ENVIDO)
        self.assertEqual(self.envido_envido.estado, 1)
        self.assertEqual(self.envido_envido.indice, 2)
        self.assertIsInstance(self.envido_envido.canto_manager, EnvidoManager)

        self.real_envido.set_canto(3)
        self.assertEqual(self.real_envido.puntos, 3)
        self.assertEqual(self.real_envido.tipo_de_canto, Canto.TipoCanto.REAL_ENVIDO)
        self.assertEqual(self.real_envido.estado, 1)
        self.assertEqual(self.real_envido.indice, 3)
        self.assertIsInstance(self.real_envido.canto_manager, EnvidoManager)

        self.falta_envido.set_canto(4)
        self.assertEqual(self.falta_envido.puntos, 5)
        self.assertEqual(self.falta_envido.tipo_de_canto, Canto.TipoCanto.FALTA_ENVIDO)
        self.assertEqual(self.falta_envido.estado, 1)
        self.assertEqual(self.falta_envido.indice, 4)
        self.assertIsInstance(self.falta_envido.canto_manager, EnvidoManager)

        self.truco.set_canto(5)
        self.assertEqual(self.truco.puntos, 2)
        self.assertEqual(self.truco.tipo_de_canto, Canto.TipoCanto.TRUCO)
        self.assertEqual(self.truco.estado, 1)
        self.assertEqual(self.truco.indice, 1)
        self.assertIsInstance(self.truco.canto_manager, TrucoManager)

        self.retruco.set_canto(6)
        self.assertEqual(self.retruco.puntos, 3)
        self.assertEqual(self.retruco.tipo_de_canto, Canto.TipoCanto.RETRUCO)
        self.assertEqual(self.retruco.estado, 1)
        self.assertEqual(self.retruco.indice, 2)
        self.assertIsInstance(self.retruco.canto_manager, TrucoManager)

        self.vale_cuatro.set_canto(7)
        self.assertEqual(self.vale_cuatro.puntos, 4)
        self.assertEqual(self.vale_cuatro.tipo_de_canto, Canto.TipoCanto.VALE_CUATRO)
        self.assertEqual(self.vale_cuatro.estado, 1)
        self.assertEqual(self.vale_cuatro.indice, 3)
        self.assertIsInstance(self.vale_cuatro.canto_manager, TrucoManager)

    
    	self.assertEqual(self.real_envido.es_menor_que(Canto.TipoCanto.FALTA_ENVIDO), True)
    	self.assertEqual(self.real_envido.es_mayor_que(Canto.TipoCanto.ENVIDO), True)
    	self.assertEqual(self.truco.es_menor_que(Canto.TipoCanto.RETRUCO), True)
    	self.assertEqual(self.retruco.es_menor_que(Canto.TipoCanto.VALE_CUATRO), True)
    	self.assertEqual(self.vale_cuatro.es_mayor_que(Canto.TipoCanto.RETRUCO), True)
    	self.assertEqual(self.envido_canto.es_menor_que(Canto.TipoCanto.FALTA_ENVIDO), True)