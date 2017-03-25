# -*- encoding: utf-8 -*-

from django.db import models


class Canto(models.Model):
    canto_manager = models.ForeignKey('CantoManager')
    puntos = models.PositiveIntegerField(default=0) # puntos del canto
    tipo_de_canto = models.PositiveIntegerField(default=0)
    estado = models.PositiveIntegerField(default=1) # EN_ESPERA, ACEPTADO, RECHAZADO
    indice = models.PositiveIntegerField(default=0) # para saber el orden en que fueron llamados los cantos

    class TipoCanto():
        """
        Clase que se usa como enum.
        """
        NADA = 0
        ENVIDO = 1
        ENVIDO_ENVIDO = 2
        REAL_ENVIDO = 3
        FALTA_ENVIDO = 4
        TRUCO = 5
        RETRUCO = 6
        VALE_CUATRO = 7
        IR_AL_MAZO = 8

    class EstadoCanto():
        """
        Clase que se usa como enum.
        """
        EN_ESPERA = 1
        ACEPTADO = 2
        RECHAZADO = 3

    @staticmethod
    def get_name(tipo_de_canto):
        """
        Obtener el nombre del tipo de canto, como string. (sería una especie de to_string())
        """
        enum_to_string = {
            Canto.TipoCanto.NADA:'Nada',
            Canto.TipoCanto.ENVIDO:'Envido',
            Canto.TipoCanto.ENVIDO_ENVIDO:'Segundo envido',
            Canto.TipoCanto.REAL_ENVIDO:'Real envido',
            Canto.TipoCanto.FALTA_ENVIDO:'Falta envido',
            Canto.TipoCanto.TRUCO:'Truco',
            Canto.TipoCanto.RETRUCO:'Retruco',
            Canto.TipoCanto.VALE_CUATRO:'Vale Cuatro',
            Canto.TipoCanto.IR_AL_MAZO:'Ir al mazo',
        }
        if tipo_de_canto in enum_to_string.keys():
            return enum_to_string[tipo_de_canto]
        else:
            return 'Canto erróneo'

    def set_canto(self, tipo_de_canto):
        """
        Establece este canto al tipo tipo_de_canto, dandole el puntaje correspondiente.
        """

        self.tipo_de_canto = tipo_de_canto
        # se establece el indice, según la cantidad de cantos que ya tiene el CantoManager nuestro
        # dada esta implementacion, los indices (una vez establecidos) iran de 1 a n.
        todos_los_cantos = self.canto_manager.canto_set.all()
        self.indice = 1
        if todos_los_cantos.exists():
            self.indice += max(todos_los_cantos, key= lambda x: x.indice).indice

        if tipo_de_canto == Canto.TipoCanto.ENVIDO:
                self.puntos = 2
        elif tipo_de_canto == Canto.TipoCanto.ENVIDO_ENVIDO:
            self.puntos = 2
        elif tipo_de_canto == Canto.TipoCanto.REAL_ENVIDO:
            self.puntos = 3
        elif tipo_de_canto == Canto.TipoCanto.FALTA_ENVIDO:
            # calcular puntos falta envido TODO ver si se puede usar polimorfismo asi canto se usa como un objeto de tipo Envido
            self.puntos = self.canto_manager.get_falta_envido_points()
        elif tipo_de_canto == Canto.TipoCanto.TRUCO:
            self.puntos = 2
        elif tipo_de_canto == Canto.TipoCanto.RETRUCO:
            self.puntos = 3
        elif tipo_de_canto == Canto.TipoCanto.VALE_CUATRO:
            self.puntos = 4
        elif tipo_de_canto == Canto.TipoCanto.IR_AL_MAZO: #TODO: ahora siempre que se va al mazo, es un punto para el ganador, no dos o uno segun se va antes o despues de tirar cartas.
            self.puntos = 1
            self.estado = Canto.EstadoCanto.ACEPTADO

        self.save()

    def es_menor_que(self, tipo_de_canto):
        return self.tipo_de_canto < tipo_de_canto

    def es_mayor_que(self, tipo_de_canto):
        return self.tipo_de_canto > tipo_de_canto

    def es_el_anterior_de(self, tipo_de_canto):
        return self.tipo_de_canto + 1 == tipo_de_canto

    @staticmethod
    def es_algun_envido(tipo_de_canto):
        return tipo_de_canto <= Canto.TipoCanto.FALTA_ENVIDO and tipo_de_canto >= Canto.TipoCanto.ENVIDO


    @staticmethod
    def es_algun_truco(tipo_de_canto):
        return tipo_de_canto > Canto.TipoCanto.FALTA_ENVIDO and tipo_de_canto <= Canto.TipoCanto.IR_AL_MAZO

    def __unicode__(self):

        return Canto.get_name(self.tipo_de_canto)

    class Meta:
        app_label = 'truco'
