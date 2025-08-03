import httpx
import config
import time
from typing import Optional

class SpotifyClient:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0

    async def _get_access_token(self) -> str:
        # Return cached token if valid
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://accounts.spotify.com/api/token',
                    data={'grant_type': 'client_credentials'},
                    auth=(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET),
                    timeout=10.0
                )

            if response.status_code != 200:
                raise Exception(f"Spotify Auth Error: {response.text}")

            data = response.json()
            self._access_token = data['access_token']
            self._token_expiry = time.time() + data['expires_in'] - 60
            return self._access_token

        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    async def get_song_features(self, track_id: str) -> dict:
        token = await self._get_access_token()
        print(track_id)
        print(f"token: {token}")
        url = f"https://api.spotify.com/v1/audio-features/{track_id}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Spotify API Error: {response.status_code} - {response.text}")

        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
