# -*- encoding: utf-8 -*-

from django.db import models
from truco.models import Player, Canto, CantoManager, Round


class TrucoManager(CantoManager):
    round = models.ForeignKey(Round)

    def recantar(self, tipo_de_truco, cantor):
        """
        Se evalúa si el tipo de truco que se quiere cantar es factible, y si lo es
        se actualiza el tipo de truco actual.
        """
        se_puede_cantar = self.se_puede_cantar(tipo_de_truco)
        if se_puede_cantar:
            self.quien_canto_ultimo = cantor

            #aceptar ultimo canto como consecuencia de recantar algo
            self.aceptar_ultimo_canto()

            # crear nuevo canto
            nuevo_canto = self.canto_set.create()
            nuevo_canto.set_canto(tipo_de_truco)
            self.save()

        return se_puede_cantar

    def se_puede_cantar(self, tipo_de_truco):
        """
        Es posible cantar el truco tipo_de_truco?
        """

        result = False
        if Canto.es_algun_truco(tipo_de_truco):
            if tipo_de_truco == Canto.TipoCanto.IR_AL_MAZO:
                return True

            cantos_actuales = self.canto_set.all()
            if not cantos_actuales.exists():
                if tipo_de_truco == Canto.TipoCanto.TRUCO:
                    result = True
            else:
                mayor_canto_actual = max(cantos_actuales, key= lambda x: x.tipo_de_canto)
                result = mayor_canto_actual.es_el_anterior_de(tipo_de_truco)
                result = result and mayor_canto_actual.estado != Canto.EstadoCanto.RECHAZADO

        return result

    def get_truco_points_to_assign(self):
        puntos = 1
        cantos_actuales_aceptados = self.canto_set.filter(estado= Canto.EstadoCanto.ACEPTADO)
        if cantos_actuales_aceptados.exists():
            mayor_canto_actual = max(cantos_actuales_aceptados, key= lambda x: x.tipo_de_canto)
            puntos = mayor_canto_actual.puntos

        # for canto in self.canto_set.all():
        #     if canto.estado == Canto.EstadoCanto.ACEPTADO:
        #         puntos += canto.puntos
        #     elif canto.estado == Canto.EstadoCanto.RECHAZADO:
        #         puntos += 1

        return puntos

    class Meta:
        app_label = 'truco'
