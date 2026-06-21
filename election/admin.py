from django.contrib import admin
from .models import SchoolClass, Candidate, Vote, ElectionSetting

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('standard', 'division')
    list_filter = ('standard', 'division')
    ordering = ('standard', 'division')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'manifesto_short')
    list_filter = ('gender',)
    search_fields = ('name',)

    def manifesto_short(self, obj):
        if obj.manifesto:
            return obj.manifesto[:50] + "..." if len(obj.manifesto) > 50 else obj.manifesto
        return "-"
    manifesto_short.short_description = 'Manifesto'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voted_at', 'standard', 'division', 'male_candidate', 'female_candidate')
    list_filter = ('standard', 'division', 'male_candidate', 'female_candidate')
    date_hierarchy = 'voted_at'
    
    # Read-only fields to prevent editing of cast votes in admin panel
    readonly_fields = ('male_candidate', 'female_candidate', 'standard', 'division', 'voted_at')
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(ElectionSetting)
class ElectionSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'current_class', 'voting_enabled')
    list_editable = ('current_class', 'voting_enabled')

