import os

import ytmusicapi
from ytmusicapi import YTMusic

from .music_service import MusicService, Playlist, Song


class YoutubeMusicService(MusicService):
    def __init__(self):
        oauth_file = "ytmusic_oauth.json"

        if os.path.exists(oauth_file):
            self.yt = YTMusic(auth=oauth_file)
        else:
            self.yt = ytmusicapi.setup_oauth(filepath=oauth_file)

    @property
    def has_auth(self) -> bool:
        return True

    @property
    def pretty_name(self) -> str:
        return "Youtube Music"

    @property
    def arg_name(self) -> str:
        return "ytmusic"

    def __extract_playlist_info(self, playlist):
        return Playlist(
            id=playlist.get("playlistId", ""),
            name=playlist.get("title", ""),
            description=playlist.get("description", ""),
        )

    def __extract_song_info(self, track):
        artist = track.get(["artists"], [])[:1]
        artist = artist["name"] if artist else ""
        return Song(
            id=track.get("videoId", ""),
            name=track.get("title", ""),
            artist=artist,
        )

    def get_user_id(self):
        return (self.yt.get_account_info()).get("channelHandle")

    def create_playlist(self, name, description=""):
        return self.yt.create_playlist(name, description)

    def add_songs_to_playlist(self, playlist_id, song_ids):
        return self.yt.add_playlist_items(playlist_id, song_ids)

    def add_song_to_playlist(self, playlist_id, song_id):
        return self.yt.add_playlist_items(playlist_id, [song_id])

    def get_playlist_songs(self, playlist_id):
        response = self.yt.get_playlist(playlist_id)
        return [self.__extract_song_info(item) for item in response]

    def get_liked_songs(self):
        response = self.yt.get_library_songs(limit=0)
        return [self.__extract_song_info(item) for item in response["tracks"]]

    def get_all_playlists(self):
        response = self.yt.get_library_playlists(limit=0)
        response = [i for i in response if i["playlistId"] not in ["LM", "RDPN", "SE"]]
        return [self.__extract_playlist_info(playlist) for playlist in response]

    def add_songs_to_liked_songs(self, song_ids):
        for song_id in song_ids:
            self.yt.rate_song(song_id, "LIKE")

    def add_song_to_liked_songs(self, song_id):
        return self.yt.rate_song(song_id, "LIKE")

    def search_song(self, query, artist):
        response = self.yt.search(f"{query} {artist}", filter="songs", limit=1)
        if response:
            return self.__extract_song_info(response[0])
