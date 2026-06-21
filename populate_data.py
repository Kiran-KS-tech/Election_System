import os
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_election.settings')
django.setup()

from django.contrib.auth.models import User
from election.models import SchoolClass, Candidate, ElectionSetting

def seed_database():
    print("--- Starting Database Seeding ---")
    
    # 1. Create Default Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@school.edu', 'admin123')
        print("[OK] Created Superuser: username='admin', password='admin123'")
    else:
        print("[INFO] Superuser 'admin' already exists.")

    # 2. Create Standards (1-12) and Divisions (A-E)
    classes_created = 0
    for std in range(1, 13):
        for div in ['A', 'B', 'C', 'D', 'E']:
            obj, created = SchoolClass.objects.get_or_create(standard=std, division=div)
            if created:
                classes_created += 1
    print(f"[OK] Seeded School Classes: Created {classes_created} classes (Standards 1-12, Divisions A-E).")

    # 3. Create Sample Candidates
    male_candidates_data = [
        {"name": "Arun", "manifesto": "Aiming to build a more collaborative school environment with better sports facilities and student representation."},
        {"name": "Rahul", "manifesto": "Promoting green initiatives, waste recycling programs, and academic peer tutoring sessions for junior classes."},
        {"name": "Akash", "manifesto": "Focusing on science fairs, technology clubs, coding bootcamps, and modern interactive classroom setups."}
    ]
    
    female_candidates_data = [
        {"name": "Anjana", "manifesto": "Committed to expanding cultural arts programs, drama events, music clubs, and school newsletter activities."},
        {"name": "Meera", "manifesto": "Advocating for better wellness spaces, student guidance programs, library books, and study corners."},
        {"name": "Gayathri", "manifesto": "Spearheading community service drives, charity runs, volunteer projects, and environmental cleanups."}
    ]

    for data in male_candidates_data:
        obj, created = Candidate.objects.get_or_create(
            name=data['name'],
            gender='Male',
            defaults={'manifesto': data['manifesto']}
        )
        if created:
            print(f"[OK] Registered Male Candidate: {obj.name}")

    for data in female_candidates_data:
        obj, created = Candidate.objects.get_or_create(
            name=data['name'],
            gender='Female',
            defaults={'manifesto': data['manifesto']}
        )
        if created:
            print(f"[OK] Registered Female Candidate: {obj.name}")

    # 4. Set Initial Election Settings
    class_8c = SchoolClass.objects.filter(standard=8, division='C').first()
    settings_obj = ElectionSetting.get_solo()
    settings_obj.current_class = class_8c
    settings_obj.voting_enabled = True
    settings_obj.save()
    print(f"[OK] Configured Initial Election State: Active Class set to '{class_8c}', Voting set to 'Enabled'.")
    
    print("--- Database Seeding Completed Successfully ---")

if __name__ == '__main__':
    seed_database()
