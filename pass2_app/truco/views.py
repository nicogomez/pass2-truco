# -*- encoding: utf-8 -*-

from django.db import transaction
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.template.response import TemplateResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import time

from forms import GameForm
from truco.models import Game, Player, Card, Canto

TEAM_A = -1
TEAM_B = 1

def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.data['username']
            password = form.data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse('truco:index'))
    else:
        form = UserCreationForm()

    return TemplateResponse(
        request, "registration/sign_up.html", {'form': form})

@login_required
def index(request):
    games = Game.objects.all()

    if request.method == 'POST':
        new_game = Game()
        form = GameForm(request.POST, instance=new_game)
        if form.is_valid():
            try:
                form.save()
                new_game.add_player(request.user, True)
            except Exception:
                new_game.delete()
                messages.error(request, "Usted ya pertenece a otra partida")
                return render(request, "truco/index.html", {
                    'games': games, 
                    'form': form,
                })

            messages.success(request, "Partida creada exitosamente")
            return HttpResponseRedirect(
                reverse('truco:room', args=(new_game.id,)))
        else:
            messages.error(request, "Error al crear partida")
    else:
        form = GameForm()

    return render(request, "truco/index.html", {'games': games, 'form': form})

@login_required
def room(request, game_id):
    game = Game.objects.get(pk=game_id)
    other_players = []

    if game:
        users_ids = map(lambda player: player.user.id, game.player_set.all())
        if request.user.id in users_ids:
            my_player = Player.objects.get(user=request.user)
            uihelper = UIHelper(my_player)
            uinotifications = UINotifications(my_player)
            if game.is_ready() and game.game_started:

                for i in xrange(0,game.number_of_players - 1):
                    aux = (my_player.place_on_table+(i+1))%game.number_of_players
                    other_players.append(Player.objects.get(game=game, place_on_table=aux))
            else:
                other_players = game.player_set.exclude(id=my_player.id)

            return TemplateResponse(request, "truco/room.html", {
                'game': game,
                'my_player': my_player,
                'ui_helper' : uihelper,
                'other_players': other_players,
                'ui_notifications' : uinotifications,
            })
        elif len(users_ids) < game.number_of_players:
            try:
                with transaction.atomic():
                    my_player = game.add_player(request.user, False)
                uihelper = UIHelper(my_player)
                uinotifications = UINotifications(my_player)
                return TemplateResponse(request, "truco/room.html", {
                    'game': game,
                    'my_player': my_player,
                    'ui_helper' : uihelper,
                    'ui_notifications' : uinotifications,
                })
            except Exception:
                messages.error(request, "Usted ya pertenece a otra partida")
        else:
            messages.error(request, 'La cantidad de jugadores alcanzo el maximo')
    else:
        messages.error(request, 'La partida seleccionada no existe')

    return HttpResponseRedirect(reverse('truco:index'))

@login_required
def start_game(request, game_id):
    game = Game.objects.get(pk=game_id)

    if game.is_ready():
        game.init_game()
        messages.success(request, "La partida ha iniciado exitosamente")
    else:
        messages.error(request, "La partida aún no puede comenzar")

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))

@login_required
def put_card(request, game_id):
    game = Game.objects.get(pk=game_id)
    if request.method == 'POST':
        card_selected = request.POST.get('put_card')
        if card_selected != None :
            request.user.player.put_card(card_selected)
            game.round.next_turn()

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))


@login_required
def process_canto_declaration(request, game_id, tipo_de_canto):
    tipo_de_canto = int(tipo_de_canto)
    game = Game.objects.filter(pk=game_id)
    if not game.exists():
        messages.error(request, "La partida ya fue finalizada")
        return HttpResponseRedirect(reverse('truco:index'))

    my_player = request.user.player
    game = game.first()

    if game.round.player_can_declare(my_player, tipo_de_canto):
        my_player.declare_canto(tipo_de_canto)
        messages.success(request, Canto.get_name(tipo_de_canto) + " declarado")
    else:
        messages.warning(request, "No se puede cantar " + Canto.get_name(tipo_de_canto))

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))


@login_required
def process_aceptar_envido(request,game_id):
    game = Game.objects.filter(pk=game_id)
    if not game.exists():
        messages.error(request, "La partida ya fue finalizada")
        return HttpResponseRedirect(reverse('truco:index'))

    my_player = request.user.player
    game = game.first()

    game.round.accept_last_envido()

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))


@login_required
def process_rechazar_envido(request,game_id):
    game = Game.objects.filter(pk=game_id)
    if not game.exists():
        messages.error(request, "La partida ya fue finalizada")
        return HttpResponseRedirect(reverse('truco:index'))

    my_player = request.user.player
    game = game.first()

    game.round.reject_last_envido()

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))


@login_required
def process_aceptar_truco(request,game_id):
    game = Game.objects.filter(pk=game_id)
    if not game.exists():
        messages.error(request, "La partida ya fue finalizada")
        return HttpResponseRedirect(reverse('truco:index'))

    my_player = request.user.player
    game = game.first()

    game.round.accept_last_truco()

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))


@login_required
def process_rechazar_truco(request,game_id):
    game = Game.objects.filter(pk=game_id)
    if not game.exists():
        messages.error(request, "La partida ya fue finalizada")
        return HttpResponseRedirect(reverse('truco:index'))

    my_player = request.user.player
    game = game.first()

    game.round.reject_last_truco()
    game.round.finish(my_player.get_opponent_team())

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))


@login_required
def finish_game(request, game_id):
    game = Game.objects.filter(pk=game_id)
    if not game.exists():
        messages.error(request, "La partida ya fue finalizada")
        return HttpResponseRedirect(reverse('truco:index'))

    my_player = request.user.player
    game = game.first()

    # seria conveniente verificar que quien está haciendo el finish game es un player de esta partida,
    # sino cualquier gilastro le puede arruinar el juego a cualquiera.

    try:
        game.finish_game()
        return HttpResponseRedirect(reverse ('truco:index'))
    except:
        messages.success(request, "La partida ya fue finalizada")

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))


@login_required
def send_envido_points(request, game_id):
    game = Game.objects.filter(pk=game_id)
    if not game.exists():
        messages.error(request, "La partida ya fue finalizada")
        return HttpResponseRedirect(reverse('truco:index'))

    my_player = request.user.player
    game = game.first()

    if request.method == 'POST':
        envido_points = request.POST.get('points')
        if envido_points != '':
            request.user.player.declared_envido_points = envido_points
            request.user.player.save()
            # Agrego puntos de envido
            if game.round.all_players_sang_their_points():
                game.round.determine_and_assign_points_to_envido_winner()
        else:
            messages.success(request, 'Debe ingresar una cantidad de puntos') 

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))


@login_required
def finish_round(request, game_id):
    game = Game.objects.filter(pk=game_id)
    if not game.exists():
        messages.error(request, "La partida ya fue finalizada")
        return HttpResponseRedirect(reverse('truco:index'))

    my_player = request.user.player
    game = game.first()

    game.finish_round()

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))


@login_required
def show_cards(request,game_id):
    game = Game.objects.filter(pk=game_id)
    if not game.exists():
        messages.error(request, "La partida ya fue finalizada")
        return HttpResponseRedirect(reverse('truco:index'))

    my_player = request.user.player
    game = game.first()

    # Si el equipo contrario mintio en los puntos
    if game.round.determine_if_team_is_a_liar(my_player.get_opponent_team()):
        envido_mgr = game.round.get_envido_manager()
        # Le Resto esos puntos y se los asigno a mi equipo
        game.give_points_to_team(envido_mgr.get_envido_points_to_assign(), my_player.team)
        game.give_points_to_team(-envido_mgr.get_envido_points_to_assign(), my_player.get_opponent_team())
        messages.success(request,'El equipo contrario ha mentido:')
        messages.success(request,'Sus puntos de envido se han transferido a tu equipo')
    else:
        messages.success(request, 'El equipo contrario "No" ha mentido en sus puntos')

    return HttpResponseRedirect(reverse('truco:room', args=(game.id,)))

def giveup_game(request, game_id):
    game = Game.objects.get(pk=game_id)
    ## PROVISORIO , SOLO PARA QUE FUNCIONE ABANDONAR PARTIDA
    p = Player.objects.get(user=request.user)
    p.delete_cards()
    p.delete()

    if not game.player_set.exists():
        game.delete()

    return HttpResponseRedirect(reverse('truco:index'))


from django.template.defaulttags import register

#@register.filter
#def get_item(dictionary, key):
#    print 'asdjasdijasdoasj'
#    return dictionary.get(key)

@register.filter(name='lookup')
def lookup(dict, index):
    if index in dict:
        return dict[index]
    return ''


class UIHelper:
    def __init__(self, player):
        self.player = player
        self.canto_names = {}
        self.must_be_shown = {}
        self.pending_canto_name = 'Nadaroski'
        self.pending_canto_is_envido = False
        self.must_show_acceptation = False
        self.all_cantos = []
        self.ordered_players_list = []

        from truco.models import Canto, Round

        self.all_cantos = [
            Canto.TipoCanto.ENVIDO,
            Canto.TipoCanto.ENVIDO_ENVIDO,
            Canto.TipoCanto.REAL_ENVIDO,
            Canto.TipoCanto.FALTA_ENVIDO,
            Canto.TipoCanto.TRUCO,
            Canto.TipoCanto.RETRUCO,
            Canto.TipoCanto.VALE_CUATRO,
            Canto.TipoCanto.IR_AL_MAZO,
        ]

        self.ordered_players_list = sorted(player.game.player_set.all(), key= lambda x: x.place_on_table)

        self.actual_round = Round.objects.filter(game__id=player.game.id)
        if not self.actual_round.exists():
            return
        self.actual_round = self.actual_round.first()


        envido_mgr = self.actual_round.get_envido_manager()
        truco_mgr = self.actual_round.get_truco_manager()

        for canto in self.all_cantos:
            self.canto_names[canto] = Canto.get_name(canto)
            self.must_be_shown[canto] = self.actual_round.player_can_declare(self.player, canto)
            
            ultimo_envido_esta_en_espera = envido_mgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.EN_ESPERA
            ultimo_truco_esta_en_espera = truco_mgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.EN_ESPERA
            
            
            if ultimo_envido_esta_en_espera:
                self.pending_canto_is_envido = True
                self.pending_canto_name = Canto.get_name(envido_mgr.get_ultimo_canto())
                self.must_show_acceptation = envido_mgr.quien_canto_ultimo.team != self.player.team
            elif ultimo_truco_esta_en_espera:
                self.must_show_acceptation = truco_mgr.quien_canto_ultimo.team != self.player.team
                if envido_mgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.ACEPTADO:
                    self.must_show_acceptation = self.must_show_acceptation and self.actual_round.all_players_sang_their_points()
                self.pending_canto_name = Canto.get_name(truco_mgr.get_ultimo_canto())

            if ultimo_truco_esta_en_espera and not ultimo_envido_esta_en_espera and envido_mgr.get_estado_del_ultimo_canto() != None:
                self.must_show_acceptation = (self.must_show_acceptation and 
                    (self.actual_round.all_players_sang_their_points() or  
                    envido_mgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.RECHAZADO))

        self.must_show_envido_points_form = envido_mgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.ACEPTADO and self.player.declared_envido_points == 0


class UINotifications:
    def __init__(self, player):
        try:
            self.player = player
            self.round = player.game.round
            self.emgr = self.round.get_envido_manager()
            self.tmgr = self.round.get_truco_manager()
            self.todobien = 'bien'
        except Exception as e:
            self.todobien = e

    def status(self):
        result = ''
        if not self.player.game.game_started:
            return result

        ultimo_envido = self.emgr.get_ultimo_canto()
        ultimo_truco = self.tmgr.get_ultimo_canto()

        if ultimo_envido != Canto.TipoCanto.NADA:
            canto = Canto.get_name(ultimo_envido)
            if self.emgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.ACEPTADO:
                result = canto+" aceptado"
            elif self.emgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.RECHAZADO:
                result = canto+" rechazado"

        if ultimo_truco != Canto.TipoCanto.NADA:
            canto = Canto.get_name(ultimo_truco)
            if self.tmgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.ACEPTADO:
                result = canto+" aceptado"
            elif self.tmgr.get_estado_del_ultimo_canto() == Canto.EstadoCanto.RECHAZADO:
                result = canto+" rechazado"

        
        
        return result
