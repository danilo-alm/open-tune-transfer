# Open Tune Transfer

Transfer your playlists and liked songs across different music services. Supported services:

| Service       | FROM | TO  |
| ------------- | ---- | --- |
| Spotify       | ✅   | ✅  |
| Youtube Music | ✅   | ✅  |
| Deezer        | ✅   | ❌  |

## Features

- Transfer playlists;
- Transfer liked songs;
- Script-friendly through CLI args;
- Skip playlists you don't want to import.

## Preparation

Install the required packages with:

```python
pip install -r requirements.txt
```

## Usage

You can run the script interactively with `python main.py`. For more information such as available flags and command-line arguments, see help with `python main.py --help`.

## For developers

To add support for more music services, write a class that implements [MusicService](./music_services/music_service.py) for your desired service and add it to the services list in [main](./main.py).

## Thanks to

- [spotipy](https://github.com/spotipy-dev/spotipy)
- [ytmusicapi](https://github.com/sigma67/ytmusicapi)
- [deezer-python](https://github.com/browniebroke/deezer-python)
