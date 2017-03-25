from django.contrib import admin

from truco.models import *


class gameAdmin(admin.ModelAdmin):
  list_display = ('name', 'game_started', 'number_of_players')

class playerAdmin(admin.ModelAdmin):
    list_display = ('user','owner','place_on_table')

class cardAdmin(admin.ModelAdmin):
  list_display = ('number', 'palo', 'en_mano')


admin.site.register(Game, gameAdmin)
admin.site.register(Card, cardAdmin)
admin.site.register(Player, playerAdmin)
admin.site.register(Round)
