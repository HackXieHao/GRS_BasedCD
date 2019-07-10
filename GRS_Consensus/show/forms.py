from django import forms

class MovieNumberForm(forms.Form):
    userIds = forms.CharField(max_length=200)
    number = forms.IntegerField()