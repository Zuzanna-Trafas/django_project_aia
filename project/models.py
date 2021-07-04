from django.db import models


class Tournament(models.Model):
    organizer = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    discipline = models.CharField(max_length=100)
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)
    time = models.DateTimeField()
    deadline = models.DateTimeField()
    max_participants = models.PositiveIntegerField()
    number_of_ranked_players = models.PositiveIntegerField()


class SponsorImage(models.Model):
    url = models.CharField(max_length=200)
    tournament = models.ManyToManyField(Tournament)


class Applicant(models.Model):
    user = models.CharField(max_length=100, primary_key=True)
    licence_number = models.CharField(max_length=100, unique=True)
    current_ranking = models.CharField(max_length=100, unique=True)
    tournament = models.ManyToManyField(Tournament)


class Game(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    round = models.PositiveIntegerField()
    applicant1 = models.ForeignKey(Applicant, related_name='applicant1', null=True, on_delete=models.CASCADE)
    applicant2 = models.ForeignKey(Applicant, related_name='applicant2', null=True, on_delete=models.CASCADE)
    winner1 = models.CharField(max_length=100, null=True)
    winner2 = models.CharField(max_length=100, null=True)
    winner = models.CharField(max_length=100, null=True)


