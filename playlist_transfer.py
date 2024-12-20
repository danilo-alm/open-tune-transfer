import logging
from typing import List, Optional

from thefuzz import fuzz

from music_services.music_service import MusicService, Playlist, Song
from music_services.spotify_service import SpotifyService


class PlaylistTransferer:
    def __init__(
        self,
        origin: MusicService,
        destination: MusicService,
        logger: Optional[logging.Logger] = None,
        dry_run: bool = False,
    ) -> None:
        self.origin = origin
        self.destination = destination
        self.logger = logger or PlaylistTransferer.__get_null_logger()
        self.dry_run = dry_run

    @staticmethod
    def __get_null_logger() -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.NullHandler())
        return logger

    @staticmethod
    def __check_match(str1: str, str2: str) -> bool:
        return fuzz.ratio(str1, str2) > 70

    def __transfer_playlist_all_at_once(
        self, playlist_id: str, songs: List[Song]
    ) -> List[Song]:
        not_match = []
        found_song_ids = []

        for song in songs:
            self.logger.info(
                f"Playlist {playlist_id}: searching for a match to {song.name}"
                + f" - {song.artist}"
                if song.artist
                else ""
            )

            match = self.destination.search_song(song.name, song.artist)
            if match and PlaylistTransferer.__check_match(song.name, match.name):
                self.logger.info(
                    f"Playlist {playlist_id}: found match: {match.name}. Song will be added to the playlist at the end"
                )
                found_song_ids += match.id
            else:
                self.logger.info(f'Playlist {playlist_id}: No match for "{song.name}"')
                not_match.append(song)

        self.logger.info(f"Adding found songs to playlist {playlist_id}")
        if not self.dry_run:
            self.destination.add_songs_to_playlist(playlist_id, found_song_ids)

        return not_match

    def __transfer_playlist_one_by_one(
        self,
        playlist_id: str,
        songs: List[Song],
    ) -> List[Song]:
        not_match = []

        for song in songs:
            self.logger.info(
                f"Playlist {playlist_id}: searching for a match to: {song.name}"
            )

            match = self.destination.search_song(song.name, song.artist)

            if match and PlaylistTransferer.__check_match(song.name, match.name):
                self.logger.info(
                    f'Playlist {playlist_id}: Adding "{match.name}" to the playlist '
                )
                if not self.dry_run:
                    self.destination.add_song_to_playlist(playlist_id, match.id)
            else:
                self.logger.warn(f'Playlist {playlist_id}: No match for "{song.name}"')
                not_match.append(song)

        return not_match

    def transfer_playlist(self, playlist: Playlist) -> List[Song]:
        songs = self.origin.get_playlist_songs(playlist.id)
        if songs is None:
            raise ValueError(f"Could not retrieve songs from playlist {playlist.name}")

        song_names = [song.name for song in songs]
        formatted_song_list = "\n".join(
            [f"{idx} - {name}" for idx, name in enumerate(song_names, start=1)]
        )
        self.logger.debug(f"Songs to transfer:\n{formatted_song_list}")

        to_playlist = (
            "DRY-RUN"
            if self.dry_run
            else self.destination.create_playlist(playlist.name, playlist.description)
        )

        self.logger.debug(f'Created playlist "{playlist.name}" with ID {to_playlist}')

        # Not all services have endpoints for adding all songs at once
        at_once = self.origin.__class__ in [SpotifyService]
        if at_once:
            self.logger.debug(
                f"Target is {type(self.destination).__name__}, calling add_to_playlist_all_at_once"
            )
            return self.__transfer_playlist_all_at_once(to_playlist, songs)

        self.logger.debug(
            f"Target is {type(self.destination).__name__}, calling add_to_playlist_one_by_one"
        )
        return self.__transfer_playlist_one_by_one(to_playlist, songs)
