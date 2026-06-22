import os
from django.core.management.base import BaseCommand
from django.conf import settings
from election.models import Candidate


class Command(BaseCommand):
    help = 'Clear stale photo references from candidates whose files no longer exist on disk'

    def handle(self, *args, **options):
        candidates_with_photos = Candidate.objects.exclude(photo='').exclude(photo__isnull=True)
        total = candidates_with_photos.count()

        if total == 0:
            self.stdout.write(self.style.WARNING('No candidates with photo references found.'))
            return

        self.stdout.write(f'Checking {total} candidate(s) with photo references...\n')
        cleared = 0

        for candidate in candidates_with_photos:
            photo_val = str(candidate.photo)

            # If it's already a Cloudinary URL, skip it — it's valid
            if photo_val.startswith('http') or 'cloudinary' in photo_val.lower() or 'res.cloudinary' in photo_val.lower():
                self.stdout.write(f'  ✅ KEEP  {candidate.name} — Cloudinary URL')
                continue

            # Check if local file exists
            local_path = os.path.join(settings.MEDIA_ROOT, photo_val)
            if not os.path.exists(local_path):
                candidate.photo = None
                candidate.save(update_fields=['photo'])
                self.stdout.write(self.style.WARNING(
                    f'  🗑️  CLEAR {candidate.name} — stale path removed: {photo_val}'
                ))
                cleared += 1
            else:
                self.stdout.write(f'  ✅ KEEP  {candidate.name} — file exists locally')

        self.stdout.write(f'\nDone. Cleared {cleared} stale photo reference(s).')
        if cleared:
            self.stdout.write('Candidates can now re-upload photos via the Edit page.')
