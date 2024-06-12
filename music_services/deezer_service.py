import deezer

from .music_service import MusicService, Playlist, Song


class DeezerService(MusicService):
    def __init__(self):
        self.client = deezer.Client()
        self.__user_id = input("Deezer User ID: ")

    @classmethod
    def has_auth(cls):
        return False

    @classmethod
    def pretty_name(cls):
        return "Deezer"

    @classmethod
    def arg_name(cls):
        return "deezer"

    def __extract_playlist_info(self, playlist):
        return Playlist(
            id=playlist.id,
            name=playlist.title,
            description=(
                playlist.description if hasattr(playlist, "description") else ""
            ),
        )

    def __extract_song_info(self, track):
        return Song(
            id=track.id,
            name=track.title,
            artist=track.artist.name,
        )

    def __get_all_playlists(self):
        user = self.client.get_user(user_id=self.__user_id)
        return user.get_playlists()

    def get_user_id(self):
        return self.__user_id

    def create_playlist(self, name, description=""):
        raise NotImplementedError("Creating playlists is not supported.")

    def add_songs_to_playlist(self, playlist_id, song_ids):
        raise NotImplementedError("Adding songs to playlists is not supported.")

    def add_song_to_playlist(self, playlist_id, song_id):
        raise NotImplementedError("Adding a song to a playlist is not supported.")

    def get_all_playlists(self):
        playlists = [i for i in self.__get_all_playlists() if i.title != "Loved Tracks"]
        return [self.__extract_playlist_info(playlist) for playlist in playlists]

    def get_playlist_songs(self, playlist_id):
        playlist = self.client.get_playlist(playlist_id)
        return [self.__extract_song_info(track) for track in playlist.tracks]

    def get_liked_songs(self):
        for playlist in self.__get_all_playlists():
            if playlist.title == "Loved Tracks":
                return [self.__extract_song_info(track) for track in playlist.tracks]
        return []

    def add_song_to_liked_songs(self, song_id):
        raise NotImplementedError("Adding a song to liked songs is not supported.")

    def add_songs_to_liked_songs(self, song_ids):
        raise NotImplementedError("Adding songs to liked songs is not supported.")

    def search_song(self, query, artist):
        results = self.client.search(query, artist=artist)
        if results:
            return self.__extract_song_info(results[0])

        results = self.client.search(f"{query} {artist}")
        if results:
            return self.__extract_song_info(results[0])
