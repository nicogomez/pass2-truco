# -*- encoding: utf-8 -*-

from django.forms import ModelForm

from  truco.models import *

class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = [
            'name', 
            'number_of_players', 
            'score_limit',
        ]
