import argparse
import logging
import sys
from typing import Iterable, List, Sequence, Set, Tuple, Type

from music_services.deezer_service import DeezerService
from music_services.music_service import MusicService
from music_services.spotify_service import SpotifyService
from music_services.ytmusic_service import YoutubeMusicService
from playlist_transfer import PlaylistTransferer


def main():
    global LOGGER

    services = [
        SpotifyService,
        YoutubeMusicService,
        DeezerService,
    ]

    args = parse_args(
        from_opts=[s.arg_name() for s in services],
        to_opts=[s.arg_name() for s in services if s.has_auth()],
    )
    validate_args(args)

    LOGGER = get_logger(args)

    if args.dry:
        LOGGER.info(
            "--> dry-run enabled. don't mind the logs, no action is being taken"
        )

    origin, destination = get_services_from_args(args, services)

    if not origin:
        print("Where do you want to import FROM?")
        origin = choose_service(services)
    LOGGER.info(f"Chosen origin: {origin.pretty_name()}")

    if not destination:
        available_destinations = [
            s
            for s in get_services_with_auth(services)
            if s.pretty_name() != origin.pretty_name()
        ]

        print("Where do you want to import TO?")
        destination = choose_service(available_destinations)
    LOGGER.info(f"Chosen destination: {destination.pretty_name()}")

    LOGGER.debug("Initializing music services")
    origin, destination = initialize_services(origin, destination)

    origin_playlists = choose_playlists(origin)

    playlist_transferer = PlaylistTransferer(origin, destination, LOGGER, args.dry)
    for playlist in origin_playlists:
        LOGGER.info(
            f"--- Importing PLAYLIST {playlist.name} FROM {origin.pretty_name()} TO {destination.pretty_name()} ---"
        )

        not_match = playlist_transferer.transfer_playlist(playlist)
        if not_match:
            enumerated_not_match = get_enumerated_elements([s.name for s in not_match])
            LOGGER.info(
                f"These songs were not found and were not added to {playlist.name}:\n{enumerated_not_match}"
            )

        LOGGER.info(f"Finished importing {playlist.name}")


def get_enumerated_elements(elements: Iterable[str]) -> str:
    return "\n".join(
        [f"{idx} - {element}" for idx, element in enumerate(elements, start=1)]
    )


def print_enumerated_elements(elements: Iterable[str]) -> None:
    enumerated = get_enumerated_elements(elements)
    print(enumerated)


def log_enumerated_elements(elements: Iterable[str]) -> None:
    string = ""
    for idx, element in enumerate(elements, start=1):
        string += f"{idx} - {element}\n"
    LOGGER.info(string)


def choose_option(options: Sequence[str]):
    print_enumerated_elements(options)

    while True:
        chosen = input(f"Choose (1-{len(options)}): ").strip()
        if chosen.isnumeric() and 0 < int(chosen) < len(options) + 1:
            break
        print(f"{chosen} is not a valid option.\n")

    return int(chosen) - 1


def choose_service(services: List[Type[MusicService]]) -> Type[MusicService]:
    service_options = [s.pretty_name() for s in services]
    chosen_idx = choose_option(service_options)
    return services[chosen_idx]


def get_services_with_auth(
    services: List[Type[MusicService]],
) -> List[Type[MusicService]]:
    return [s for s in services if s.has_auth()]


def initialize_services(*services: Type[MusicService]) -> List[MusicService]:
    initialized = []
    for service in services:
        print(
            f"\nInitializing {service.__name__}..." + " Please, authenticate"
            if service.has_auth()
            else ""
        )
        try:
            initialized.append(service())
        except Exception as e:
            LOGGER.critical(f"Error initializing {service.__name__}: {e}")
            sys.exit(1)
    return initialized


def parse_numbers(input_string) -> Set[int]:
    result_set = set()
    elements = input_string.split()

    for element in elements:
        if "-" in element:
            start, end = map(int, element.split("-"))
            result_set.update(range(start, end + 1))
        else:
            result_set.add(int(element))

    return result_set


def choose_playlists(origin: MusicService):
    origin_playlists = origin.get_all_playlists()
    LOGGER.info(f"Found {len(origin_playlists)} playlists in {origin.pretty_name()}")

    print("\nPlaylists found:")
    print_enumerated_elements([p.name for p in origin_playlists])

    not_import = parse_numbers(
        input(
            "\nWhich playlists do you NOT want to import (e.g. 1 3 5-7)? \
            Leave empty to import ALL playlists.\n-> "
        )
    )

    return [
        playlist
        for idx, playlist in enumerate(origin_playlists)
        if idx + 1 not in not_import
    ]


def get_logger(args: argparse.Namespace) -> logging.Logger:
    logging_level = logging.DEBUG if args.debug else logging.INFO
    file_handler = logging.FileHandler("open_tune_transfer.log")
    file_handler.setLevel(logging_level)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    stdout_handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)
    logger.addHandler(file_handler)
    if args.logs:
        logger.addHandler(stdout_handler)

    return logger


def validate_args(args: argparse.Namespace) -> None:
    if args.origin and args.origin == args.to:
        raise ValueError("Origin and destination services cannot be the same")


def get_services_from_args(
    args: argparse.Namespace, services: List[Type[MusicService]]
) -> Tuple[Type[MusicService], Type[MusicService]]:
    origin = next(s for s in services if s.arg_name() == args.origin)
    destination = next(s for s in services if s.arg_name() == args.to)
    return origin, destination


def parse_args(from_opts: List[str], to_opts: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Open Tune Transfer",
        description="Transfer playlists across different music platforms",
    )

    parser.add_argument(
        "--from", choices=from_opts, help="music service to import from", dest="origin"
    )
    parser.add_argument("--to", choices=to_opts, help="music service to import to")
    parser.add_argument("--debug", action="store_true", help="set log level to debug")
    parser.add_argument("--logs", action="store_true", help="redirect logs to stdout")
    parser.add_argument(
        "--dry",
        action="store_true",
        help="do not actually transfer the playlists. logs are still shown",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
