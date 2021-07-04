from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import date

from django.forms import DateTimeInput


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class AddForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "name",
                                                         'maxlength': "100", "required": "true"}))

    discipline = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "discipline",
                                      'maxlength': '100', "required": "true"}))

    time = forms.CharField(widget=forms.TextInput(attrs={"type": "datetime-local", "class": "form-control",
                                                         "id": "time", "required": "true"}))

    lat = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "lat",
                                      'maxlength': '50'}), required=False)

    lng = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "lat",
                                      'maxlength': '50'}), required=False)

    max_participants = forms.CharField(
        widget=forms.TextInput(attrs={'type': "number", 'class': "form-control", 'id': "max_participants",
                                      'maxlength': '20', "min": "0", "required": "true"}))

    application_deadline = forms.CharField(
        widget=forms.TextInput(attrs={"type": "datetime-local", "class": "form-control",
                                      "id": "application_deadline", "required": "true"}))

    url = forms.CharField(widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "url",
                                                        'maxlength': "1000", "required": "true"}))


class EditForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "name",
                                                         'maxlength': "100", "required": "true"}))

    discipline = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "discipline",
                                      'maxlength': '100', "required": "true"}))

    time = forms.CharField(widget=forms.TextInput(attrs={"type": "datetime-local", "class": "form-control",
                                                         "id": "time", "required": "true"}))

    lat = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "lat",
                                      'maxlength': '50'}), required=False)

    lng = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "lat",
                                      'maxlength': '50'}), required=False)


class DetailsForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "name",
                                                         'maxlength': "100"}))

    discipline = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "discipline",
                                      'maxlength': '100'}))

    organizer = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "organizer",
                                      'maxlength': '100'}))

    time = forms.CharField(widget=forms.TextInput(attrs={"type": "text", "class": "form-control",
                                                         "id": "time"}))

    max_participants = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "max_participants",
                                      'maxlength': '20'}))

    application_deadline = forms.CharField(
        widget=forms.TextInput(attrs={"type": "text", "class": "form-control",
                                      "id": "application_deadline"}))

    number_of_ranked_players = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "number_of_ranked_players",
                                      'maxlength': '20'}))


class ApplyForm(forms.Form):
    licence_number = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "licence_number",
                                      'maxlength': "100", "required": "true"}))

    current_ranking = forms.CharField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "current_rankin",
                                      'maxlength': "100", "required": "true"}))


class GameWinnerForm(forms.Form):
    def __init__(self, winner_choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['winner_radio'] = forms.ChoiceField(label="Select winner: ", widget=forms.RadioSelect(attrs={'id': "winner_radio"}),
                                                        choices=winner_choices)
    winner_radio = forms.ChoiceField()


