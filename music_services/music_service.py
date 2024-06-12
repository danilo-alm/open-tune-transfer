from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Song:
    id: str
    name: str
    artist: str


@dataclass
class Playlist:
    id: str
    name: str
    description: str


class MusicService(ABC):

    # Attributes will be defined as methods, since I did not find a clean way
    # of making attributes static when implementing the class (@property and
    # @staticmethod cannot be combined). @classmethod is being used for
    # static methods.

    @classmethod
    @abstractmethod
    def has_auth(cls) -> bool:
        """
        Indicates whether there is support for authentication.

        Returns:
            bool: True if supported, False otherwise.
        """
        pass

    @classmethod
    @abstractmethod
    def pretty_name(cls) -> str:
        """
        Provides a user-friendly name for the music service.

        Returns:
            str: The user-friendly name of the music service.
        """
        pass

    @classmethod
    @abstractmethod
    def arg_name(cls) -> str:
        """
        Provides a short argument name for the music service.

        Returns:
            str: The short argument name of the music service.
        """
        pass

    @abstractmethod
    def create_playlist(self, name: str, description: str) -> str:
        """
        Creates a new playlist with the given name and description.

        Args:
            name (str): The name of the playlist.
            description (str): The description of the playlist.

        Returns:
            str: The ID of the created playlist.
        """
        pass

    @abstractmethod
    def get_user_id(self) -> str:
        """
        Retrieves the user ID of the authenticated user.

        Returns:
            str: The user ID of the authenticated user.
        """
        pass

    @abstractmethod
    def add_song_to_playlist(self, playlist_id: str, song_id: str) -> None:
        """
        Adds a single song to a specified playlist.

        Args:
            playlist_id (str): The ID of the playlist.
            song_id (str): The ID of the song to add to the playlist.

        Returns:
            None
        """
        pass

    @abstractmethod
    def add_songs_to_playlist(self, playlist_id: str, song_ids: List[str]) -> None:
        """
        Adds multiple songs to a specified playlist.

        This method will either call an API endpoint that accepts multiple songs,
        or call add_song_to_playlist() multiple times.

        Args:
            playlist_id (str): The ID of the playlist.
            song_ids (List[str]): The list of song IDs to add to the playlist.

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_all_playlists(self) -> List[Playlist]:
        """
        Retrieves all playlists of the authenticated user.

        Returns:
            List[Playlist]: A list of all playlists.
        """
        pass

    @abstractmethod
    def get_playlist_songs(self, playlist_id: str) -> Optional[List[Song]]:
        """
        Retrieves songs in a specified playlist.

        Args:
            playlist_id (str): The ID of the playlist.

        Returns:
            Optional[Playlist]: The songs in the specified playlist.
        """
        pass

    @abstractmethod
    def get_liked_songs(self) -> List[Song]:
        """
        Retrieves all songs liked by the authenticated user.

        Returns:
            List[Song]: A list of liked songs.
        """
        pass

    @abstractmethod
    def add_song_to_liked_songs(self, song_id: str) -> None:
        """
        Adds a single song to the user's liked songs.

        Args:
            song_id (str): The ID of the song to add to liked songs.

        Returns:
            None
        """
        pass

    @abstractmethod
    def add_songs_to_liked_songs(self, song_ids: List[str]) -> None:
        """
        Adds multiple songs to the user's liked songs.

        This method will either call an API endpoint that accepts multiple songs,
        or call add_song_to_liked_songs() multiple times.

        Args:
            song_ids (List[str]): The list of song IDs to add to liked songs.

        Returns:
            None
        """
        pass

    @abstractmethod
    def search_song(self, query: str, artist: str) -> Optional[Song]:
        """
        Searches for a song by its title and artist.

        Args:
            query (str): The title of the song.
            artist (str): The artist of the song.

        Returns:
            Optional[Song]: The details of the found song.
        """
        pass
