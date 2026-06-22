import os
import cloudinary
import cloudinary.uploader
from django.core.management.base import BaseCommand
from django.conf import settings
from election.models import Candidate


class Command(BaseCommand):
    help = 'Migrate existing local candidate photos to Cloudinary storage'

    def handle(self, *args, **options):
        candidates_with_photos = Candidate.objects.exclude(photo='').exclude(photo__isnull=True)
        total = candidates_with_photos.count()

        if total == 0:
            self.stdout.write(self.style.WARNING('No candidates with photos found.'))
            return

        self.stdout.write(f'Found {total} candidate(s) with photos. Starting migration...\n')

        success = 0
        skipped = 0
        failed = 0

        for candidate in candidates_with_photos:
            photo_field_value = str(candidate.photo)

            # Already a Cloudinary URL — skip
            if photo_field_value.startswith('http') or 'cloudinary' in photo_field_value:
                self.stdout.write(self.style.SUCCESS(
                    f'  ✅ SKIP  {candidate.name} — already on Cloudinary'
                ))
                skipped += 1
                continue

            # Try local disk path
            local_path = os.path.join(settings.MEDIA_ROOT, photo_field_value)

            if not os.path.exists(local_path):
                self.stdout.write(self.style.WARNING(
                    f'  ⚠️  MISS  {candidate.name} — file not found at {local_path}'
                ))
                failed += 1
                continue

            try:
                # Upload directly to Cloudinary
                result = cloudinary.uploader.upload(
                    local_path,
                    folder='candidates',
                    public_id=f'candidate_{candidate.pk}',
                    overwrite=True,
                    resource_type='image',
                )

                # Save the Cloudinary public_id as the new photo path
                # django-cloudinary-storage uses public_id as the stored value
                new_path = f"candidates/candidate_{candidate.pk}.{result['format']}"
                candidate.photo = new_path
                candidate.save(update_fields=['photo'])

                self.stdout.write(self.style.SUCCESS(
                    f'  ✅ OK    {candidate.name} → {result["secure_url"]}'
                ))
                success += 1

            except Exception as exc:
                self.stdout.write(self.style.ERROR(
                    f'  ❌ FAIL  {candidate.name} — {exc}'
                ))
                failed += 1

        self.stdout.write('\n─────────────────────────────────')
        self.stdout.write(f'Done. Uploaded: {success}  |  Skipped: {skipped}  |  Failed: {failed}')
        if failed:
            self.stdout.write(self.style.WARNING(
                'Failed candidates need their photos re-uploaded manually via the Edit page.'
            ))
