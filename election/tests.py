from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SchoolClass, Candidate, Vote, ElectionSetting
from .forms import VoteForm

class ElectionModelTests(TestCase):
    def setUp(self):
        self.school_class = SchoolClass.objects.create(standard=8, division='C')
        self.candidate_m = Candidate.objects.create(name="Arun", gender="Male", manifesto="Male Leader")
        self.candidate_f = Candidate.objects.create(name="Anjana", gender="Female", manifesto="Female Leader")

    def test_school_class_str(self):
        self.assertEqual(str(self.school_class), "8-C")

    def test_candidate_str(self):
        self.assertEqual(str(self.candidate_m), "Arun (Male)")

    def test_election_setting_singleton(self):
        # Create two setting objects and assert only one exists in DB
        setting1 = ElectionSetting.objects.create(current_class=self.school_class, voting_enabled=True)
        setting2 = ElectionSetting.objects.create(current_class=None, voting_enabled=False)
        
        # Singleton forces pk=1, so setting2 updates setting1
        self.assertEqual(ElectionSetting.objects.count(), 1)
        active_setting = ElectionSetting.get_solo()
        self.assertEqual(active_setting.voting_enabled, False)
        self.assertNil = self.assertEqual(active_setting.current_class, None)


class StudentVotingViewTests(TestCase):
    def setUp(self):
        self.school_class = SchoolClass.objects.create(standard=8, division='C')
        self.candidate_m = Candidate.objects.create(name="Arun", gender="Male")
        self.candidate_f = Candidate.objects.create(name="Anjana", gender="Female")
        
        self.settings = ElectionSetting.get_solo()
        self.settings.current_class = self.school_class
        self.settings.voting_enabled = True
        self.settings.save()

    def test_voting_page_accessible_when_enabled(self):
        response = self.client.get(reverse('student_vote'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'election/vote.html')
        self.assertContains(response, 'value="8" selected')
        self.assertContains(response, 'value="C" selected')


    def test_voting_page_disabled_when_flag_false(self):
        self.settings.voting_enabled = False
        self.settings.save()
        
        response = self.client.get(reverse('student_vote'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'election/voting_disabled.html')

    def test_vote_form_validation(self):
        # Form requires both a male and female selection
        form_data = {
            'standard': 8,
            'division': 'C',
            'male_candidate': self.candidate_m.id,
            # female_candidate is missing
        }
        form = VoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        form_data = {
            'standard': 8,
            'division': 'C',
            'male_candidate': self.candidate_m.id,
            'female_candidate': self.candidate_f.id,
        }
        form = VoteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_successful_vote_submission(self):
        # Post a valid vote
        form_data = {
            'standard': 10,
            'division': 'B',
            'male_candidate': self.candidate_m.id,
            'female_candidate': self.candidate_f.id,
        }
        response = self.client.post(reverse('student_vote'), data=form_data)
        
        # Check redirection to success screen
        self.assertRedirects(response, reverse('vote_success'))
        
        # Verify vote is written to database matching the user's selection
        self.assertEqual(Vote.objects.count(), 1)
        vote = Vote.objects.first()
        self.assertEqual(vote.male_candidate, self.candidate_m)
        self.assertEqual(vote.female_candidate, self.candidate_f)
        self.assertEqual(vote.standard, 10)
        self.assertEqual(vote.division, 'B')



class StaffAccessControlTests(TestCase):
    def test_control_panel_accessible_anonymously(self):
        response = self.client.get(reverse('control_panel'))
        self.assertEqual(response.status_code, 200)


