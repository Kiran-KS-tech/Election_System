from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required as django_staff_member_required
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

# Pass-through decorator to remove staff login restriction entirely
def staff_member_required(view_func=None, *args, **kwargs):
    if view_func is None:
        return lambda f: f
    return view_func



from .models import SchoolClass, Candidate, Vote, ElectionSetting
from .forms import VoteForm, CandidateForm

def student_vote(request):
    settings_obj = ElectionSetting.get_solo()
    
    # Security check: If voting is disabled or no class is active, show warning page
    if not settings_obj.voting_enabled or not settings_obj.current_class:
        return render(request, 'election/voting_disabled.html', {
            'settings': settings_obj
        })
    
    active_class = settings_obj.current_class
    male_candidates = Candidate.objects.filter(gender='Male')
    female_candidates = Candidate.objects.filter(gender='Female')
    
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            # standard and division come from the invigilator-selected active class, NOT from the student
            vote = Vote(
                male_candidate=form.cleaned_data['male_candidate'],
                female_candidate=form.cleaned_data['female_candidate'],
                standard=active_class.standard,
                division=active_class.division
            )
            vote.save()
            # Redirect to success screen
            return redirect('vote_success')
        else:
            # Add error messages if any validation fails
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = VoteForm()
        
    return render(request, 'election/vote.html', {
        'form': form,
        'active_class': active_class,
        'male_candidates': male_candidates,
        'female_candidates': female_candidates,
        'settings': settings_obj
    })



def vote_success(request):
    settings_obj = ElectionSetting.get_solo()
    active_class = settings_obj.current_class
    return render(request, 'election/success.html', {
        'active_class': active_class
    })


@staff_member_required
def control_panel(request):
    settings_obj = ElectionSetting.get_solo()
    
    # Define choice ranges for standard (1-12) and division (A-E)
    standards = list(range(1, 13))
    divisions = ['A', 'B', 'C', 'D', 'E']
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'set_class':
            standard = request.POST.get('standard')
            division = request.POST.get('division')
            
            if standard and division:
                # Retrieve or create the school class model
                school_class, created = SchoolClass.objects.get_or_create(
                    standard=int(standard),
                    division=division
                )
                settings_obj.current_class = school_class
                settings_obj.save()
                messages.success(request, f"Active Class successfully set to {school_class}")
            else:
                messages.error(request, "Please select both standard and division.")
                
        elif action == 'toggle_voting':
            settings_obj.voting_enabled = not settings_obj.voting_enabled
            settings_obj.save()
            state = "enabled" if settings_obj.voting_enabled else "disabled"
            messages.info(request, f"Voting has been {state}.")
            
        return redirect('control_panel')
        
    return render(request, 'election/control_panel.html', {
        'settings': settings_obj,
        'standards': standards,
        'divisions': divisions,
        'total_votes': Vote.objects.count()
    })


@staff_member_required
def reset_election(request):
    if request.method == 'POST':
        # Clear all votes safely
        Vote.objects.all().delete()
        messages.success(request, "Election has been successfully reset! All votes have been cleared.")
    return redirect('control_panel')


@staff_member_required
def election_results(request):
    # Total votes counts
    total_votes = Vote.objects.count()
    
    # Male candidates results
    # Aggregate votes by joining through the related_name='male_votes'
    male_results = Candidate.objects.filter(gender='Male').annotate(
        vote_count=Count('male_votes')
    ).order_by('-vote_count')
    
    # Female candidates results
    female_results = Candidate.objects.filter(gender='Female').annotate(
        vote_count=Count('female_votes')
    ).order_by('-vote_count')
    
    # Winners calculation
    male_winner = male_results.first() if male_results.exists() and male_results.first().vote_count > 0 else None
    female_winner = female_results.first() if female_results.exists() and female_results.first().vote_count > 0 else None
    
    # Vote breakdown by class
    # To display votes cast by Standard and Division
    class_breakdown = Vote.objects.values('standard', 'division').annotate(
        count=Count('id')
    ).order_by('standard', 'division')
    
    return render(request, 'election/results.html', {
        'total_votes': total_votes,
        'male_results': male_results,
        'female_results': female_results,
        'male_winner': male_winner,
        'female_winner': female_winner,
        'class_breakdown': class_breakdown,
    })


# CRUD Views for Candidate Management using Django Class-Based Views
@method_decorator(staff_member_required, name='dispatch')
class CandidateListView(ListView):
    model = Candidate
    template_name = 'election/candidate_manage.html'
    context_object_name = 'candidates'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['male_candidates'] = Candidate.objects.filter(gender='Male')
        context['female_candidates'] = Candidate.objects.filter(gender='Female')
        return context


@method_decorator(staff_member_required, name='dispatch')
class CandidateCreateView(CreateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'election/candidate_form.html'
    success_url = reverse_lazy('candidate_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Candidate {form.cleaned_data['name']} created successfully!")
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CandidateUpdateView(UpdateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'election/candidate_form.html'
    success_url = reverse_lazy('candidate_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Candidate {form.cleaned_data['name']} updated successfully!")
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CandidateDeleteView(DeleteView):
    model = Candidate
    template_name = 'election/candidate_confirm_delete.html'
    success_url = reverse_lazy('candidate_list')
    
    def delete(self, request, *args, **kwargs):
        candidate = self.get_object()
        messages.success(request, f"Candidate {candidate.name} deleted successfully!")
        return super().delete(request, *args, **kwargs)
