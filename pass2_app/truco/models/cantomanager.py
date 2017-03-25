# -*- encoding: utf-8 -*-

from django.db import models
from truco.models import Player, Round, Canto


class CantoManager(models.Model):
    """
    Esta clase puede verse más bien como una interfaz, delimita dos métodos principales que tendrán en común
    los dos CantoManagers de la aplicación, y algunos atributos básicos.

    quien_canto_ultimo: Player que cantó el último canto relacionado con este CantoManager.
    round: ronda a la que pertenece este CantoManager.
    """
    #round = models.ForeignKey(Round) esto no se puede asi de simple, el choto de django no genera los sets envidomanager_set trucomanager_Set en round si no tienen ellos mismos el foreign key.
    quien_canto_ultimo = models.ForeignKey(Player, null = True, default = None)


    def recantar():
        pass

    def se_puede_cantar():
        pass

    def get_ultimo_canto(self):
        """
        obtener el tipo de canto del ultimo canto declarado.
        """
        ultimo_canto = Canto.TipoCanto.NADA
        cantos = self.canto_set.all()
        if cantos.exists():
            ultimo_canto = max(cantos, key= lambda x: x.indice).tipo_de_canto
        return ultimo_canto

    def get_estado_del_ultimo_canto(self):
        result = None
        cantos = self.canto_set.all()
        if cantos.exists():
            ultimo_canto = max(cantos, key= lambda x: x.tipo_de_canto)
            result = ultimo_canto.estado
        return result


    def hay_algun_canto_aceptado(self):
        cantos = self.canto_set.filter(estado = Canto.EstadoCanto.ACEPTADO)
        return cantos.exists()

    def aceptar_ultimo_canto(self):
        """
        Se acepta el ultimo canto declarado, si es que estaba en espera.
        """
        cantos = self.canto_set.all()
        if cantos.exists():
            ultimo_canto = max(cantos, key= lambda x: x.tipo_de_canto)
            if ultimo_canto.estado == Canto.EstadoCanto.EN_ESPERA:
                ultimo_canto.estado = Canto.EstadoCanto.ACEPTADO
                ultimo_canto.save()

    def rechazar_ultimo_canto(self):
        """
        Se rechaza el ultimo canto declarado, si es que estaba en espera.
        """
        cantos = self.canto_set.all()
        if cantos.exists():
            ultimo_canto = max(cantos, key= lambda x: x.tipo_de_canto)
            if ultimo_canto.estado == Canto.EstadoCanto.EN_ESPERA:
                ultimo_canto.estado = Canto.EstadoCanto.RECHAZADO
                ultimo_canto.save()

    class Meta:
        app_label = 'truco'
