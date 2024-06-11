from spotipy import Spotify, SpotifyPKCE

from .music_service import MusicService, Playlist, Song


class SpotifyService(MusicService):
    def __init__(self):
        sp_oauth = SpotifyPKCE(
            client_id="96d2d77892cc4384aff4a7328e68b41f",
            redirect_uri="http://localhost:8888/callback",
            scope="user-library-read",
        )
        self.sp = Spotify(auth=sp_oauth.get_access_token(check_cache=True))

    @property
    def has_auth(self):
        return True

    @property
    def pretty_name(self):
        return "Spotify"

    @property
    def arg_name(self):
        return "spotify"

    def __extract_playlist_info(self, playlist):
        return Playlist(
            id=playlist.get("id", ""),
            name=playlist.get("name", ""),
            description=playlist.get("description", ""),
        )

    def __extract_song_info(self, track):
        artist = track.get("artists", [])[:1]
        artist = artist["name"] if artist else ""
        return Song(
            id=track.get("uri", ""),
            name=track.get("name", ""),
            artist=artist,
        )

    def get_user_id(self):
        return self.sp.current_user()["id"]

    def create_playlist(self, name, description=""):
        user_id = self.get_user_id()
        return self.sp.user_playlist_create(
            user_id, name, public=False, description=description
        )["id"]

    def add_songs_to_playlist(self, playlist_id, song_ids):
        return self.sp.playlist_add_items(playlist_id, song_ids)

    def add_song_to_playlist(self, playlist_id, song_id):
        return self.sp.playlist_add_items(playlist_id, [song_id])

    def get_all_playlists(self):
        data = []
        while True:
            response = self.sp.current_user_playlists(offset=len(data))
            data.extend(
                [self.__extract_playlist_info(item) for item in response["items"]]
            )
            if not response["next"]:
                break
        return data

    def get_playlist_songs(self, playlist_id):
        response = self.sp.playlist(playlist_id)
        return [
            self.__extract_song_info(item["track"])
            for item in response["tracks"]["items"]
        ]

    def get_liked_songs(self):
        response = self.sp.current_user_saved_tracks()
        return [self.__extract_song_info(item["track"]) for item in response["items"]]

    def add_song_to_liked_songs(self, song_id):
        return self.sp.current_user_saved_tracks_add([song_id])

    def add_songs_to_liked_songs(self, song_ids):
        return self.sp.current_user_saved_tracks_add(song_ids)

    def search_song(self, query, artist):
        response = self.sp.search(f"{query} {artist}", limit=1)["tracks"]["items"]
        if response:
            return self.__extract_song_info(response[0])
