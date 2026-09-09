from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Album, AlbumSong, Artist, Song


class ArtistApiTest(APITestCase):
    def test_list_artists_empty(self):
        response = self.client.get("/api/artists/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_create_artist(self):
        response = self.client.post("/api/artists/", {"name": "Queen"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Artist.objects.count(), 1)
        self.assertEqual(Artist.objects.get().name, "Queen")

    def test_create_artist_with_blank_name_is_rejected(self):
        response = self.client.post("/api/artists/", {"name": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_retrieve_artist_includes_nested_albums(self):
        artist = Artist.objects.create(name="Queen")
        Album.objects.create(title="A Night at the Opera", artist=artist, release_year=1975)
        response = self.client.get(f"/api/artists/{artist.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Queen")
        self.assertEqual(len(response.data["albums"]), 1)
        self.assertEqual(response.data["albums"][0]["title"], "A Night at the Opera")

    def test_update_artist_name(self):
        artist = Artist.objects.create(name="Queen")
        response = self.client.patch(f"/api/artists/{artist.id}/", {"name": "Queen (Band)"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        artist.refresh_from_db()
        self.assertEqual(artist.name, "Queen (Band)")

    def test_delete_artist(self):
        artist = Artist.objects.create(name="Queen")
        response = self.client.delete(f"/api/artists/{artist.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Artist.objects.count(), 0)

    def test_delete_artist_cascades_to_albums_and_tracks(self):
        artist = Artist.objects.create(name="Queen")
        album = Album.objects.create(title="A Night at the Opera", artist=artist, release_year=1975)
        song = Song.objects.create(title="Bohemian Rhapsody")
        AlbumSong.objects.create(album=album, song=song, track_number=11)

        response = self.client.delete(f"/api/artists/{artist.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Album.objects.count(), 0)
        self.assertEqual(AlbumSong.objects.count(), 0)
        # The song itself is not an Artist/Album descendant, so it must survive.
        self.assertTrue(Song.objects.filter(pk=song.pk).exists())


class SongApiTest(APITestCase):
    def test_list_songs_empty(self):
        response = self.client.get("/api/songs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_create_song(self):
        response = self.client.post("/api/songs/", {"title": "Bohemian Rhapsody"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Song.objects.count(), 1)

    def test_create_song_with_blank_title_is_rejected(self):
        response = self.client.post("/api/songs/", {"title": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_update_song_title(self):
        song = Song.objects.create(title="Bohemian Rapsody")
        response = self.client.patch(f"/api/songs/{song.id}/", {"title": "Bohemian Rhapsody"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        song.refresh_from_db()
        self.assertEqual(song.title, "Bohemian Rhapsody")

    def test_delete_song(self):
        song = Song.objects.create(title="Bohemian Rhapsody")
        response = self.client.delete(f"/api/songs/{song.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Song.objects.count(), 0)

    def test_delete_song_removes_album_song_but_keeps_album(self):
        artist = Artist.objects.create(name="Queen")
        album = Album.objects.create(title="A Night at the Opera", artist=artist, release_year=1975)
        song = Song.objects.create(title="Bohemian Rhapsody")
        AlbumSong.objects.create(album=album, song=song, track_number=11)

        response = self.client.delete(f"/api/songs/{song.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AlbumSong.objects.count(), 0)
        self.assertTrue(Album.objects.filter(pk=album.pk).exists())

    def test_search_songs_by_title_case_insensitive(self):
        Song.objects.create(title="Bohemian Rhapsody")
        Song.objects.create(title="Death on Two Legs")
        response = self.client.get("/api/songs/", {"search": "bohe"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Bohemian Rhapsody")

    def test_song_detail_lists_every_album_it_belongs_to_with_track_numbers(self):
        """Key business rule (docs/01_SPEC.md, rule 1): the same Song can belong to
        several Albums, each with its own track_number."""
        artist = Artist.objects.create(name="Queen")
        night_at_opera = Album.objects.create(
            title="A Night at the Opera", artist=artist, release_year=1975
        )
        greatest_hits = Album.objects.create(
            title="Greatest Hits", artist=artist, release_year=1981
        )
        song = Song.objects.create(title="Bohemian Rhapsody")
        AlbumSong.objects.create(album=night_at_opera, song=song, track_number=11)
        AlbumSong.objects.create(album=greatest_hits, song=song, track_number=2)

        response = self.client.get(f"/api/songs/{song.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        albums = response.data["albums"]
        self.assertEqual(len(albums), 2)

        by_title = {entry["album"]["title"]: entry["track_number"] for entry in albums}
        self.assertEqual(by_title["A Night at the Opera"], 11)
        self.assertEqual(by_title["Greatest Hits"], 2)

    def test_song_detail_with_no_albums_returns_empty_list(self):
        song = Song.objects.create(title="Unreleased Demo")
        response = self.client.get(f"/api/songs/{song.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["albums"], [])

    def test_song_detail_query_count_does_not_grow_with_album_count(self):
        artist = Artist.objects.create(name="Queen")
        song = Song.objects.create(title="Bohemian Rhapsody")
        for i in range(5):
            album = Album.objects.create(title=f"Compilation {i}", artist=artist, release_year=1980)
            AlbumSong.objects.create(album=album, song=song, track_number=1)

        with self.assertNumQueries(2):  # 1 for the Song, 1 for its album_songs (select_related)
            response = self.client.get(f"/api/songs/{song.id}/")
        self.assertEqual(len(response.data["albums"]), 5)


class AlbumApiTest(APITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name="Queen")

    def test_create_album_without_tracks(self):
        response = self.client.post(
            "/api/albums/",
            {"title": "A Night at the Opera", "artist_id": self.artist.id, "release_year": 1975},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Album.objects.count(), 1)
        self.assertEqual(response.data["artist"]["name"], "Queen")
        self.assertEqual(response.data["tracks"], [])

    def test_create_album_with_nonexistent_artist_is_rejected(self):
        response = self.client.post(
            "/api/albums/",
            {"title": "A Night at the Opera", "artist_id": 999, "release_year": 1975},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_album_with_release_year_out_of_range_is_rejected(self):
        response = self.client.post(
            "/api/albums/",
            {
                "title": "Future Album",
                "artist_id": self.artist.id,
                "release_year": timezone.now().year + 5,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("release_year", response.data)

    def test_retrieve_album_includes_tracks(self):
        album = Album.objects.create(title="A Night at the Opera", artist=self.artist, release_year=1975)
        response = self.client.get(f"/api/albums/{album.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tracks"], [])

    def test_list_albums_uses_short_representation(self):
        Album.objects.create(title="A Night at the Opera", artist=self.artist, release_year=1975)
        response = self.client.get("/api/albums/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tracks_count", response.data[0])
        self.assertNotIn("tracks", response.data[0])

    def test_create_album_with_tracks_using_existing_songs(self):
        song_a = Song.objects.create(title="Death on Two Legs")
        song_b = Song.objects.create(title="Bohemian Rhapsody")

        response = self.client.post(
            "/api/albums/",
            {
                "title": "A Night at the Opera",
                "artist_id": self.artist.id,
                "release_year": 1975,
                "tracks": [
                    {"song_id": song_a.id, "track_number": 1},
                    {"song_id": song_b.id, "track_number": 11},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        album = Album.objects.get()
        self.assertEqual(album.album_songs.count(), 2)
        self.assertEqual(
            set(album.album_songs.values_list("song__title", "track_number")),
            {("Death on Two Legs", 1), ("Bohemian Rhapsody", 11)},
        )

    def test_create_album_with_new_song_created_on_the_fly(self):
        response = self.client.post(
            "/api/albums/",
            {
                "title": "A Night at the Opera",
                "artist_id": self.artist.id,
                "release_year": 1975,
                "tracks": [{"new_song_title": "Bohemian Rhapsody", "track_number": 11}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Song.objects.count(), 1)
        self.assertEqual(Song.objects.get().title, "Bohemian Rhapsody")
        self.assertEqual(AlbumSong.objects.get().track_number, 11)

    def test_create_album_with_duplicate_track_numbers_creates_nothing(self):
        song_a = Song.objects.create(title="Death on Two Legs")
        song_b = Song.objects.create(title="Bohemian Rhapsody")

        response = self.client.post(
            "/api/albums/",
            {
                "title": "A Night at the Opera",
                "artist_id": self.artist.id,
                "release_year": 1975,
                "tracks": [
                    {"song_id": song_a.id, "track_number": 1},
                    {"song_id": song_b.id, "track_number": 1},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Album.objects.count(), 0)
        self.assertEqual(AlbumSong.objects.count(), 0)

    def test_delete_album_removes_tracks_but_keeps_songs(self):
        album = Album.objects.create(title="A Night at the Opera", artist=self.artist, release_year=1975)
        song = Song.objects.create(title="Bohemian Rhapsody")
        AlbumSong.objects.create(album=album, song=song, track_number=11)

        response = self.client.delete(f"/api/albums/{album.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AlbumSong.objects.count(), 0)
        self.assertTrue(Song.objects.filter(pk=song.pk).exists())


class SongAcrossTwoAlbumsWithDifferentTrackNumbersApiTest(APITestCase):
    """Dedicated end-to-end test for the core catalog requirement: the same Song
    can be attached to two different Albums, each under its own track_number,
    entirely through the public REST API (docs/01_SPEC.md, business rule 1)."""

    def test_same_song_attached_to_two_albums_with_different_track_numbers(self):
        artist = Artist.objects.create(name="Queen")
        song = Song.objects.create(title="Bohemian Rhapsody")

        album_1_response = self.client.post(
            "/api/albums/",
            {
                "title": "A Night at the Opera",
                "artist_id": artist.id,
                "release_year": 1975,
                "tracks": [{"song_id": song.id, "track_number": 11}],
            },
            format="json",
        )
        album_2_response = self.client.post(
            "/api/albums/",
            {
                "title": "Greatest Hits",
                "artist_id": artist.id,
                "release_year": 1981,
                "tracks": [{"song_id": song.id, "track_number": 2}],
            },
            format="json",
        )

        self.assertEqual(album_1_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(album_2_response.status_code, status.HTTP_201_CREATED)

        # The AlbumSong through-table has one row per album for the same song,
        # each with its own track_number — this is the whole point of `through`.
        self.assertEqual(song.album_songs.count(), 2)
        numbers = set(song.album_songs.values_list("track_number", flat=True))
        self.assertEqual(numbers, {11, 2})

        song_response = self.client.get(f"/api/songs/{song.id}/")
        self.assertEqual(song_response.status_code, status.HTTP_200_OK)
        albums = song_response.data["albums"]
        self.assertEqual(len(albums), 2)
        by_title = {entry["album"]["title"]: entry["track_number"] for entry in albums}
        self.assertEqual(by_title, {"A Night at the Opera": 11, "Greatest Hits": 2})


class AlbumTrackApiTest(APITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name="Queen")
        self.album = Album.objects.create(
            title="A Night at the Opera", artist=self.artist, release_year=1975
        )
        self.song_a = Song.objects.create(title="Death on Two Legs")
        self.song_b = Song.objects.create(title="Bohemian Rhapsody")

    def test_list_tracks_sorted_by_track_number(self):
        AlbumSong.objects.create(album=self.album, song=self.song_b, track_number=11)
        AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)

        response = self.client.get(f"/api/albums/{self.album.id}/tracks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([t["track_number"] for t in response.data], [1, 11])

    def test_add_track_to_album(self):
        response = self.client.post(
            f"/api/albums/{self.album.id}/tracks/",
            {"song_id": self.song_a.id, "track_number": 1},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.album.album_songs.count(), 1)

    def test_add_track_with_duplicate_track_number_is_rejected(self):
        AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)

        response = self.client.post(
            f"/api/albums/{self.album.id}/tracks/",
            {"song_id": self.song_b.id, "track_number": 1},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("track_number", response.data)
        self.assertEqual(self.album.album_songs.count(), 1)

    def test_add_track_with_song_already_in_album_is_rejected(self):
        AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)

        response = self.client.post(
            f"/api/albums/{self.album.id}/tracks/",
            {"song_id": self.song_a.id, "track_number": 2},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("song_id", response.data)

    def test_patch_track_number_to_free_slot(self):
        track = AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)

        response = self.client.patch(
            f"/api/albums/{self.album.id}/tracks/{track.id}/", {"track_number": 5}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        track.refresh_from_db()
        self.assertEqual(track.track_number, 5)

    def test_patch_track_number_to_taken_slot_is_rejected(self):
        AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)
        track_2 = AlbumSong.objects.create(album=self.album, song=self.song_b, track_number=2)

        response = self.client.patch(
            f"/api/albums/{self.album.id}/tracks/{track_2.id}/", {"track_number": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        track_2.refresh_from_db()
        self.assertEqual(track_2.track_number, 2)

    def test_delete_track_keeps_song(self):
        track = AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)

        response = self.client.delete(f"/api/albums/{self.album.id}/tracks/{track.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AlbumSong.objects.count(), 0)
        self.assertTrue(Song.objects.filter(pk=self.song_a.pk).exists())

    def test_track_belonging_to_another_album_returns_404(self):
        other_album = Album.objects.create(title="Greatest Hits", artist=self.artist, release_year=1981)
        track = AlbumSong.objects.create(album=other_album, song=self.song_a, track_number=1)

        response = self.client.get(f"/api/albums/{self.album.id}/tracks/{track.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
