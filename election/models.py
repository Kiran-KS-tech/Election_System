from django.db import models
from django.core.exceptions import ValidationError

class SchoolClass(models.Model):
    STANDARD_CHOICES = [(i, str(i)) for i in range(1, 13)]
    DIVISION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]

    standard = models.IntegerField(choices=STANDARD_CHOICES)
    division = models.CharField(max_length=1, choices=DIVISION_CHOICES)

    class Meta:
        unique_together = ('standard', 'division')
        ordering = ['standard', 'division']
        verbose_name = 'School Class'
        verbose_name_plural = 'School Classes'

    def __str__(self):
        return f"{self.standard}-{self.division}"


class Candidate(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    manifesto = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.gender})"

    class Meta:
        ordering = ['gender', 'name']


class Vote(models.Model):
    male_candidate = models.ForeignKey(
        Candidate, 
        related_name='male_votes', 
        on_delete=models.PROTECT,
        limit_choices_to={'gender': 'Male'}
    )
    female_candidate = models.ForeignKey(
        Candidate, 
        related_name='female_votes', 
        on_delete=models.PROTECT,
        limit_choices_to={'gender': 'Female'}
    )
    # Storing standard and division as basic fields to preserve vote records if classes change
    standard = models.IntegerField()
    division = models.CharField(max_length=1)
    voted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vote in {self.standard}-{self.division} at {self.voted_at.strftime('%Y-%m-%d %H:%M')}"


class ElectionSetting(models.Model):
    current_class = models.ForeignKey(
        SchoolClass, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    voting_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Election Setting'
        verbose_name_plural = 'Election Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        kwargs.pop('force_insert', None)
        super().save(*args, **kwargs)


    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        active_class = self.current_class if self.current_class else "None"
        return f"Active Class: {active_class} | Voting: {'Enabled' if self.voting_enabled else 'Disabled'}"

