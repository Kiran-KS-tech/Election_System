from django import forms
from .models import Candidate, SchoolClass, ElectionSetting

class VoteForm(forms.Form):
    # standard and division are NOT collected from the student.
    # They are read from the invigilator's active class (ElectionSetting.current_class).
    male_candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.filter(gender='Male'),
        widget=forms.RadioSelect,
        required=True,
        error_messages={'required': 'Please select one Male Candidate.'}
    )
    female_candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.filter(gender='Female'),
        widget=forms.RadioSelect,
        required=True,
        error_messages={'required': 'Please select one Female Candidate.'}
    )



class ElectionControlForm(forms.ModelForm):
    class_select = forms.ModelChoiceField(
        queryset=SchoolClass.objects.all(),
        label="Select Active Class",
        empty_label="-- Select Class --",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )

    class Meta:
        model = ElectionSetting
        fields = ['voting_enabled']
        widgets = {
            'voting_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.current_class:
            self.fields['class_select'].initial = self.instance.current_class


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'photo', 'gender', 'manifesto']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'manifesto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe candidate goals...'})
        }
