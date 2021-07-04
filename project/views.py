from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate

import json

from .forms import SignupForm, DetailsForm, AddForm, ApplyForm, EditForm, GameWinnerForm
from .models import Tournament, SponsorImage, Applicant, Game
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from django.db.models import Max
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
import copy
import pytz
import math

utc = pytz.UTC


def index(request):
    tournaments = [model_to_dict(instance) for instance in Tournament.objects.all()]
    for tournament in tournaments:
        tournament["time"] = tournament["time"].strftime("%d-%m-%Y %H:%M")
        tournament["deadline"] = tournament["deadline"].strftime("%d-%m-%Y %H:%M")
    json_tournaments = json.dumps(tournaments)
    return render(request, 'accounts/index.html', {'json_tournaments': json_tournaments, 'tournaments': tournaments})


def main(request):
    return render(request, 'registration/home.html')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your tournaments account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignupForm()
    return render(request, 'registration/sign_up.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


def tournament_round(no_of_teams, matchlist):
    new_matches = []
    for team_or_match in matchlist:
        if type(team_or_match) == type([]):
            new_matches += [tournament_round(no_of_teams, team_or_match)]
        else:
            new_matches += [[team_or_match, no_of_teams + 1 - team_or_match]]
    return new_matches


def flatten_list(matches):
    teamlist = []
    for team_or_match in matches:
        if type(team_or_match) == type([]):
            teamlist += flatten_list(team_or_match)
        else:
            teamlist += [team_or_match]
    return teamlist


def generate_tournament(num):
    num_rounds = math.log(num, 2)
    if num_rounds != math.trunc(num_rounds):
        raise ValueError("Number of teams must be a power of 2")
    teams = 1
    result = [1]
    while teams != num:
        teams *= 2
        result = tournament_round(teams, result)
    return flatten_list(result)


def create_ladder(tournament):
    ladder = []
    applicants = list(tournament.applicant_set.all())
    applicants.sort(key=lambda x: int(x.current_ranking))
    if len(applicants) == 0:
        return ladder
    while math.log(len(applicants), 2) - int(math.log(len(applicants), 2)) != 0:
        applicants.append(None)
    indexes = generate_tournament(len(applicants))
    indexes = [i - 1 for i in indexes]
    applicants_sorted = [applicants[i] for i in indexes]
    ladder.append(applicants_sorted)
    rounds = math.ceil(math.log(len(applicants)) / math.log(2))
    curr_count = len(applicants)
    for _ in range(rounds - 1):
        curr_count = math.ceil(curr_count / 2)
        curr_round = []
        for i in range(curr_count):
            curr_round.append(None)
        ladder.append(curr_round.copy())
    return ladder


def create_games(tournament):
    ladder = create_ladder(tournament)
    pairs = []
    for j in range(len(ladder)):
        for i in range(1, len(ladder[j]), 2):
            pairs.append((ladder[j][i - 1], ladder[j][i], j + 1))
    for pair in pairs:
        if pair[0] is not None and pair[1] is not None:
            game = Game.objects.create(tournament=tournament, round=pair[2], applicant1=pair[0], applicant2=pair[1])
        elif pair[0] is not None and pair[1] is None:
            game = Game.objects.create(tournament=tournament, round=pair[2], applicant1=pair[0], winner1=pair[0].user,
                                       winner2=pair[0].user)
        elif pair[0] is None and pair[1] is not None:
            game = Game.objects.create(tournament=tournament, round=pair[2], applicant2=pair[1], winner1=pair[1].user,
                                       winner2=pair[1].user)
        else:
            game = Game.objects.create(tournament=tournament, round=pair[2])
        game.save()


def find_game(tournament, game_round):
    games_of_round = tournament.game_set.filter(round=game_round + 1)
    for game in games_of_round:
        if game.applicant1 is None or game.applicant2 is None:
            return game


def update_games(tournament):
    games = tournament.game_set.order_by("round")
    for game in games:
        if game.winner is None and game.winner1 == game.winner2 and game.winner1 is not None:
            game.winner = game.winner1
            game.save()
            second_round = find_game(tournament, game.round)
            if second_round.applicant1 is None:
                second_round.applicant1 = get_object_or_404(Applicant, pk=game.winner1)
            else:
                second_round.applicant2 = get_object_or_404(Applicant, pk=game.winner1)
            second_round.save()


def find_active_player_game(tournament, player):
    games = tournament.game_set.all()
    for game in games:
        if game.applicant1 is None or game.applicant2 is None:
            continue
        if (game.applicant1.user == player and game.winner1 is None) or (
                game.applicant2.user == player and game.winner2 is None):
            return game
    return None


def details(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    games = []
    if tournament.deadline < utc.localize(datetime.now()):
        if not tournament.game_set.all().exists():
            create_games(tournament)
        update_games(tournament)
        games = tournament.game_set.order_by("round")

    is_playing = False
    active_game = find_active_player_game(tournament, request.user.get_username())
    if active_game is not None:
        is_playing = True
        winner_choices = [(active_game.applicant1.user, active_game.applicant1.user),
                          (active_game.applicant2.user, active_game.applicant2.user)]
    else:
        winner_choices = []

    game_winner_form = GameWinnerForm(winner_choices, request.POST)

    if game_winner_form.is_valid():
        is_playing = False
        winner = game_winner_form.cleaned_data['winner_radio']
        if active_game.applicant1.user == request.user.get_username():
            active_game.winner1 = winner
        else:
            active_game.winner2 = winner
            active_game.winner2 = winner

        if active_game.winner1 is not None and active_game.winner2 is not None:
            if active_game.winner1 == active_game.winner2:
                update_games(tournament)
            else:
                active_game.winner1 = None
                active_game.winner2 = None
        active_game.save()

    initial_values = {'name': tournament.name, 'discipline': tournament.discipline, 'organizer': tournament.organizer,
                      'time': tournament.time.strftime("%d.%m.%Y %H:%M"),
                      'max_participants': tournament.max_participants,
                      'application_deadline': tournament.deadline.strftime("%d.%m.%Y %H:%M"),
                      'number_of_ranked_players': tournament.number_of_ranked_players}

    form = DetailsForm(initial=initial_values)
    link = ""
    if tournament.lat != "" and tournament.lng != "":
        link = "https://www.google.com/maps/search/?api=1&query=" + tournament.lat + "," + tournament.lng

    sponsor_images = tournament.sponsorimage_set.all()
    images = []
    for img in sponsor_images:
        images.append(img.url)

    apply_available = True
    if request.user.get_username() == tournament.organizer or utc.localize(
            datetime.now()) > tournament.deadline or tournament.max_participants <= tournament.number_of_ranked_players:
        apply_available = False

    edit_available = True
    if request.user.get_username() != tournament.organizer or utc.localize(datetime.now()) > tournament.time:
        edit_available = False

    return render(request, 'accounts/details.html',
                  {'form': form, 'game_winner_form': game_winner_form, 'edit_available': edit_available,
                   'tournament_id': tournament_id, 'link': link,
                   'images': images, 'apply_available': apply_available, 'games': games, 'is_playing': is_playing})


@login_required
def add(request):
    form = AddForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data['name']
        discipline = form.cleaned_data['discipline']
        time = form.cleaned_data['time']
        lat = form.cleaned_data['lat']
        lng = form.cleaned_data['lng']
        max_participants = form.cleaned_data['max_participants']
        application_deadline = form.cleaned_data['application_deadline']
        url_field = form.cleaned_data['url']

        datetime_time = datetime.strptime(time, '%Y-%m-%dT%H:%M')
        datetime_deadline = datetime.strptime(application_deadline, '%Y-%m-%dT%H:%M')
        if datetime_time < datetime.now() or datetime_deadline < datetime.now():
            if datetime_time < datetime.now():
                error = "Time can't be earlier than now!"
            elif datetime_deadline < datetime.now():
                error = "Deadline can't be earlier than now!"
            return render(request, 'accounts/add.html',
                          {'form': form, 'error': error})

        if datetime_time < datetime_deadline:
            error = "Deadline can't be earlier than tournament time!"
            return render(request, 'accounts/add.html',
                          {'form': form, 'error': error})

        tournament = Tournament.objects.create(organizer=request.user.get_username(), name=name, discipline=discipline,
                                               lat=lat,
                                               lng=lng, time=datetime_time, deadline=datetime_deadline,
                                               max_participants=max_participants, number_of_ranked_players=0)

        tournament.save()

        urls = url_field.split(" ")
        for u in urls:
            url = SponsorImage(url=u)
            url.save()
            url.tournament.add(tournament)

        return redirect('/')

    return render(request, 'accounts/add.html',
                  {'form': form, 'error': ""})


@login_required
def edit(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    initial_values = {'name': tournament.name, 'discipline': tournament.discipline,
                      'time': tournament.time.strftime('%Y-%m-%dT%H:%M'), 'lat': tournament.lat, 'lng': tournament.lng,
                      'max_participants': tournament.max_participants,
                      'application_deadline': tournament.deadline.strftime('%Y-%m-%dT%H:%M')}

    if request.POST:
        form = EditForm(request.POST)
    else:
        form = EditForm(initial=initial_values)

    if form.is_valid():
        name = form.cleaned_data['name']
        discipline = form.cleaned_data['discipline']
        time = form.cleaned_data['time']
        lat = form.cleaned_data['lat']
        lng = form.cleaned_data['lng']

        datetime_time = datetime.strptime(time, '%Y-%m-%dT%H:%M')
        if datetime_time < datetime.now():
            error = "Time can't be earlier than now!"
            return render(request, 'accounts/edit.html',
                          {'form': form, 'error': error})

        tournament.name = name
        tournament.discipline = discipline
        tournament.time = time
        tournament.lat = lat
        tournament.lng = lng

        tournament.save(force_update=True)

        return redirect('/details/' + str(tournament_id))

    return render(request, 'accounts/edit.html',
                  {'form': form, 'error': ""})


@login_required
def apply(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    form = ApplyForm(request.POST)
    if form.is_valid():
        if tournament.number_of_ranked_players >= tournament.max_participants:
            error = "Tournament participant limits exceeded. You can no longer register for the event."
            return render(request, 'accounts/apply.html',
                          {'form': form, 'error': error, 'tournament_id': tournament_id})

        if tournament.deadline < utc.localize(datetime.now()):
            error = "Tournament deadline exceeded. You can no longer register for the event."
            return render(request, 'accounts/apply.html',
                          {'form': form, 'error': error, 'tournament_id': tournament_id})

        licence_number = form.cleaned_data['licence_number']
        current_ranking = form.cleaned_data['current_ranking']

        applicant = Applicant(user=request.user.get_username(), licence_number=licence_number,
                              current_ranking=current_ranking)
        try:
            applicant.save()
            applicant.tournament.add(tournament)
        except Exception as e:
            error = e.args
            if "UNIQUE" in e.args[0]:
                if "current_ranking" in e.args[0]:
                    error = "Current ranking has to be unique."
                elif "licence_number" in e.args[0]:
                    error = "License number has to be unique."
                else:
                    error = "You already are registered for this event!"
            return render(request, 'accounts/apply.html',
                          {'form': form, 'error': error, 'tournament_id': tournament_id})

        tournament.number_of_ranked_players += 1
        tournament.save()

        return redirect("/details/" + str(tournament_id))

    return render(request, 'accounts/apply.html',
                  {'form': form, 'error': "", 'tournament_id': tournament_id})


def my_events(request):
    try:
        applicant = get_object_or_404(Applicant, pk=request.user.get_username())
        tournaments = [model_to_dict(instance) for instance in applicant.tournament.all()]
    except:
        return render(request, 'accounts/my_events.html',
                      {'json_tournaments': "", 'tournaments': ""})
    for tournament in tournaments:
        tournament["time"] = tournament["time"].strftime("%d-%m-%Y %H:%M")
        tournament["deadline"] = tournament["deadline"].strftime("%d-%m-%Y %H:%M")
    json_tournaments = json.dumps(tournaments)
    return render(request, 'accounts/my_events.html',
                  {'json_tournaments': json_tournaments, 'tournaments': tournaments})
