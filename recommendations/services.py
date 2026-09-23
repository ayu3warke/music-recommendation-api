from django.core.cache import cache
from django.conf import settings

from recommendations.models import Recommendation
from spotify.client import SpotifyClient, SpotifyError


DEMO_TRACKS = [
    {
        "id": "demo-001",
        "name": "Adventure of a Lifetime",
        "artists": ["Coldplay"],
        "album": "A Head Full of Dreams",
        "spotify_url": None,
        "preview_url": None,
        "duration_ms": 263000,
    },
    {
        "id": "demo-002",
        "name": "Paradise",
        "artists": ["Coldplay"],
        "album": "Mylo Xyloto",
        "spotify_url": None,
        "preview_url": None,
        "duration_ms": 278000,
    },
    {
        "id": "demo-003",
        "name": "Viva La Vida",
        "artists": ["Coldplay"],
        "album": "Viva La Vida or Death and All His Friends",
        "spotify_url": None,
        "preview_url": None,
        "duration_ms": 242000,
    },
    {
        "id": "demo-004",
        "name": "Yellow",
        "artists": ["Coldplay"],
        "album": "Parachutes",
        "spotify_url": None,
        "preview_url": None,
        "duration_ms": 266000,
    },
    {
        "id": "demo-005",
        "name": "Blinding Lights",
        "artists": ["The Weeknd"],
        "album": "After Hours",
        "spotify_url": None,
        "preview_url": None,
        "duration_ms": 200000,
    },
]


def refresh_user_recommendations(user):
    client = SpotifyClient()

    source = "spotify"

    try:
        tracks = client.get_recommendations(
            genres=user.favorite_genres,
            artists=user.favorite_artists,
            moods=user.moods,
            limit=20,
        )
    except SpotifyError:
        tracks = DEMO_TRACKS.copy()
        source = "demo"

    recommendation = Recommendation.objects.create(
        user=user,
        tracks=tracks,
        source=source,
    )

    cache_key = f"recommendations:user:{user.id}"

    cache.set(
        cache_key,
        {
            "user_id": user.id,
            "source": source,
            "tracks": tracks,
            "recommendation_id": recommendation.id,
        },
        settings.RECOMMENDATION_CACHE_TTL,
    )

    return recommendation
