import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from cloudcasts.models import Tag, Cloudcast

User = get_user_model()

GENRES = [
    # Main genres
    'Afrobeats', 'Ambient', 'Alternative', 'Bass & Club Music', 'Blues',
    'Chillout', 'Classical', 'Country', 'Dance', 'Dancehall', 'Disco',
    'Drum and Bass', 'Dub', 'Dubstep', 'EDM', 'Electronic', 'Electronica',
    'Experimental', 'Folk', 'Funk', 'Garage (UKG)', 'Hardcore', 'Hip Hop',
    'House', 'Industrial', 'Jazz', 'Jungle', 'Metal', 'Pop', 'Punk',
    'R&B', 'Rap', 'Reggae', 'Reggaeton', 'Rock', 'Soul', 'Techno', 'Trance',
    # House sub-genres
    'Acid House', 'Afro House', 'Bass House', 'Big Room House', 'Chicago House',
    'Classic House', 'Club House', 'Deep House', 'Disco House', 'Dutch House',
    'Electro House', 'Funky House', 'Latin House', 'Progressive House',
    'Soulful House', 'Tech House', 'Tribal House', 'Vocal House',
    # Techno sub-genres
    'Acid Techno', 'Ambient Techno', 'Bouncy Techno', 'Dark Techno',
    'Deep Techno', 'Detroit Techno', 'Dub Techno', 'Minimal Techno',
    # Drum and Bass sub-genres
    'Ambient Drum and Bass', 'Atmospheric Drum and Bass', 'Drumfunk',
    'Liquid Drum and Bass',
    # Trance sub-genres
    'Balearic Trance', 'Dark Psytrance', 'Dream Trance', 'Progressive EDM',
    'Euphoric Hardstyle',
    # Disco sub-genres
    'Disco Edits', 'Electro-disco', 'Hi-NRG', 'Nu-disco',
    # Breakbeat family
    'Big Beat', 'Breakbeat', 'Breakbeat Hardcore', 'Breakcore', 'Breaks',
    'Broken Beat',
    # Bass music
    'Bass Music', 'Bassline', 'Post-dubstep', 'Dubtronica',
    # Electro family
    'Electro', 'Electro Hop', 'Electro Swing', 'Electro-industrial',
    'Electroacoustic', 'Electronic Body Music',
    # Wave / synth
    'Cold Wave', 'Dark Electro', 'Dark Wave', 'Darksynth',
    # Other electronic
    'Balearic', 'Boogie', 'Chillstep', 'Chiptune', 'Dance-rock',
    'Deep Tech House', 'Dembow', 'Donk', 'Downtempo', 'Early Hardcore',
    'Future', 'Indie Dance', 'Lounge Music', 'Melodic House & Techno',
    'Progressive Electronic',
    # Other genres
    'Afrobeat', 'Blue-eyed Soul', 'Drill', 'DJ Edits / Bootlegs',
    'Indie', 'Nu Jazz', 'Progressive Rock', 'Remixes', 'Rock \'n\' Roll',
    'Rockabilly', 'UK Hip Hop', 'Underground', 'Urban', 'World', 'Worldbeat',
]

SHOW_TEMPLATES = [
    '{genre} Sessions Vol. {n}',
    'Late Night {genre}',
    '{genre} Mixtape #{n}',
    'The {genre} Show',
    '{genre} Underground',
    'Pure {genre} Vibes',
    'Essential {genre} Mix',
    '{genre} Selections',
    '{genre} After Dark',
    '{genre} Collective',
]

CREATORS = [
    'djmaria', 'househeaduk', 'technotemple', 'bassculture',
    'vinyldigger', 'nightowlmixes', 'groovemerchant', 'deepspace',
]


class Command(BaseCommand):
    help = 'Seed the database with sample genres, creators, and shows'

    def handle(self, *args, **options):
        genre_tags = []
        for genre_name in GENRES:
            tag, created = Tag.objects.get_or_create(
                slug=slugify(genre_name),
                defaults={'name': genre_name, 'tag_type': 'genre'},
            )
            genre_tags.append(tag)
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Genre: {tag.name} ({status})')

        creators = []
        for username in CREATORS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': username.replace('dj', 'DJ ').title()},
            )
            creators.append(user)

        now = timezone.now()
        created_count = 0

        for genre_tag in genre_tags:
            for i in range(3):
                template = random.choice(SHOW_TEMPLATES)
                name = template.format(genre=genre_tag.name, n=random.randint(1, 99))
                slug = slugify(name)
                creator = random.choice(creators)

                if Cloudcast.objects.filter(owner=creator, slug=slug).exists():
                    continue

                days_ago = random.randint(1, 300)
                show = Cloudcast.objects.create(
                    name=name,
                    slug=slug,
                    owner=creator,
                    quality_score=round(random.uniform(0.3, 1.0), 2),
                    publish_date=now - timedelta(days=days_ago),
                    play_count=random.randint(50, 5000),
                    is_public=True,
                    picture_url='',
                )
                show.tags.add(genre_tag)

                if random.random() < 0.3:
                    extra = random.choice([t for t in genre_tags if t != genre_tag])
                    show.tags.add(extra)

                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {created_count} shows across {len(genre_tags)} genres.'
        ))
