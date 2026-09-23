import base64
import requests
from django.conf import settings


class SpotifyError(Exception):
    pass


class SpotifyClient:
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    API_URL = "https://api.spotify.com/v1"

    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET

    def get_access_token(self):
        if not self.client_id or not self.client_secret:
            raise SpotifyError(
                "Spotify credentials are not configured. "
                "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET."
            )

        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        response = requests.post(
            self.TOKEN_URL,
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
            timeout=15,
        )

        if response.status_code != 200:
            raise SpotifyError(
                f"Spotify token request failed: {response.text}"
            )

        return response.json()["access_token"]

    def search_tracks(self, query, limit=10):
        token = self.get_access_token()

        response = requests.get(
            f"{self.API_URL}/search",
            headers={
                "Authorization": f"Bearer {token}",
            },
            params={
                "q": query,
                "type": "track",
                "limit": limit,
            },
            timeout=15,
        )

        if response.status_code != 200:
            raise SpotifyError(
                f"Spotify search failed: {response.text}"
            )

        tracks = response.json().get("tracks", {}).get("items", [])

        return [
            {
                "id": track["id"],
                "name": track["name"],
                "artists": [
                    artist["name"]
                    for artist in track.get("artists", [])
                ],
                "album": track.get("album", {}).get("name"),
                "spotify_url": track.get("external_urls", {}).get(
                    "spotify"
                ),
                "preview_url": track.get("preview_url"),
                "duration_ms": track.get("duration_ms"),
            }
            for track in tracks
        ]

    def get_recommendations(
        self,
        genres=None,
        artists=None,
        moods=None,
        limit=20,
    ):
        genres = genres or []
        artists = artists or []
        moods = moods or []

        queries = []

        for genre in genres[:2]:
            queries.append(f"genre:{genre}")

        for artist in artists[:2]:
            queries.append(f'artist:"{artist}"')

        for mood in moods[:2]:
            queries.append(mood)

        if not queries:
            queries.append("popular music")

        recommendations = []
        seen_ids = set()

        for query in queries:
            tracks = self.search_tracks(query, limit=10)

            for track in tracks:
                if track["id"] not in seen_ids:
                    seen_ids.add(track["id"])
                    recommendations.append(track)

                if len(recommendations) >= limit:
                    return recommendations

        return recommendations
