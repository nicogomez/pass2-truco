from django.conf.urls import patterns, url

from truco import views

urlpatterns = patterns('',
	url(r'^$', views.index , name='index'),

	url(r'^room/(?P<game_id>\d+)/$', views.room, name='room'),
	url(r'^room/(?P<game_id>\d+)/cantar/(?P<tipo_de_canto>\d+)$', views.process_canto_declaration, name='process-canto-declaration'),
	url(r'^room/(?P<game_id>\d+)/aceptar_truco/$', views.process_aceptar_truco, name='process-aceptar-truco'),
	url(r'^room/(?P<game_id>\d+)/rechazar_truco/$', views.process_rechazar_truco, name='process-rechazar-truco'),
	url(r'^room/(?P<game_id>\d+)/aceptar_envido/$', views.process_aceptar_envido, name='process-aceptar-envido'),
	url(r'^room/(?P<game_id>\d+)/rechazar_envido/$', views.process_rechazar_envido, name='process-rechazar-envido'),

	url(r'^room/(?P<game_id>\d+)/finish_game/$', views.finish_game, name='finish-game'),
	url(r'^room/(?P<game_id>\d+)/finish_round/$', views.finish_round, name='finish-round'),

	url(r'^room/(?P<game_id>\d+)/send_envido_points/$', views.send_envido_points, name='send-envido-points'),

	url(r'^room/(?P<game_id>\d+)/show_cards/$', views.show_cards, name='show-cards'),

	url(r'^start_game/(?P<game_id>\d+)/$', views.start_game, name='start-game'),

	url(r'^giveup_game/(?P<game_id>\d+)/$', views.giveup_game, name='giveup-game'),

	url(r'^put_card/(?P<game_id>\d+)/$', views.put_card, name='put-card'),
)