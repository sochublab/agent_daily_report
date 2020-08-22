from django import forms


class CreateNewList(forms.Form):
    name = forms.CharField(label="Your Name", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    uploadfile = forms.FileField(label="File (.zip)", widget=forms.FileInput(attrs={'accept': '.zip, .jpg'}))
    datefield = forms.DateField(label="Report Date", widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD e.g 2020-01-01'}))
