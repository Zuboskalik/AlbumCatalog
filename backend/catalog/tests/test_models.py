from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from catalog.models import Album, AlbumSong, Artist, Song


class ArtistModelTest(TestCase):
    def test_create_artist_and_str(self):
        artist = Artist.objects.create(name="Queen")
        self.assertEqual(str(artist), "Queen")

    def test_name_is_required(self):
        artist = Artist(name="")
        with self.assertRaises(ValidationError):
            artist.full_clean()


class SongModelTest(TestCase):
    def test_create_song_and_str(self):
        song = Song.objects.create(title="Bohemian Rhapsody")
        self.assertEqual(str(song), "Bohemian Rhapsody")

    def test_title_is_required(self):
        song = Song(title="")
        with self.assertRaises(ValidationError):
            song.full_clean()


class AlbumModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name="Queen")

    def test_create_album_linked_to_artist(self):
        album = Album.objects.create(
            title="A Night at the Opera", artist=self.artist, release_year=1975
        )
        self.assertEqual(self.artist.albums.count(), 1)
        self.assertEqual(self.artist.albums.first(), album)

    def test_title_is_required(self):
        album = Album(artist=self.artist, release_year=1975, title="")
        with self.assertRaises(ValidationError):
            album.full_clean()

    def test_artist_is_required(self):
        album = Album(title="Untitled", release_year=1975)
        with self.assertRaises(ValidationError):
            album.full_clean()

    def test_release_year_is_required(self):
        album = Album(title="Untitled", artist=self.artist)
        with self.assertRaises(ValidationError):
            album.full_clean()

    def test_deleting_artist_cascades_to_albums(self):
        Album.objects.create(
            title="A Night at the Opera", artist=self.artist, release_year=1975
        )
        self.artist.delete()
        self.assertEqual(Album.objects.count(), 0)

    def test_release_year_too_far_in_future_is_invalid(self):
        album = Album(
            title="Future Album",
            artist=self.artist,
            release_year=timezone.now().year + 2,
        )
        with self.assertRaises(ValidationError):
            album.full_clean()

    def test_release_year_too_old_is_invalid(self):
        album = Album(title="Ancient Album", artist=self.artist, release_year=1800)
        with self.assertRaises(ValidationError):
            album.full_clean()

    def test_release_year_current_year_is_valid(self):
        album = Album(
            title="This Year Album",
            artist=self.artist,
            release_year=timezone.now().year,
        )
        album.full_clean()  # should not raise


class AlbumSongModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name="Queen")
        self.album = Album.objects.create(
            title="A Night at the Opera", artist=self.artist, release_year=1975
        )
        self.song_a = Song.objects.create(title="Death on Two Legs")
        self.song_b = Song.objects.create(title="Bohemian Rhapsody")

    def test_create_album_song(self):
        track = AlbumSong.objects.create(
            album=self.album, song=self.song_a, track_number=1
        )
        self.assertEqual(self.album.album_songs.count(), 1)
        self.assertIn(str(self.album), str(track))

    def test_duplicate_track_number_in_same_album_is_rejected(self):
        AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AlbumSong.objects.create(
                    album=self.album, song=self.song_b, track_number=1
                )

    def test_same_song_twice_in_same_album_is_rejected(self):
        AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AlbumSong.objects.create(
                    album=self.album, song=self.song_a, track_number=2
                )

    def test_track_number_zero_is_invalid(self):
        track = AlbumSong(album=self.album, song=self.song_a, track_number=0)
        with self.assertRaises(ValidationError):
            track.full_clean()

    def test_track_number_negative_is_invalid(self):
        track = AlbumSong(album=self.album, song=self.song_a, track_number=-1)
        with self.assertRaises(ValidationError):
            track.full_clean()

    def test_same_song_can_belong_to_different_albums_with_different_track_numbers(self):
        other_album = Album.objects.create(
            title="Greatest Hits", artist=self.artist, release_year=1981
        )
        AlbumSong.objects.create(album=self.album, song=self.song_b, track_number=11)
        AlbumSong.objects.create(album=other_album, song=self.song_b, track_number=2)

        self.assertEqual(self.song_b.album_songs.count(), 2)
        numbers = set(
            self.song_b.album_songs.values_list("track_number", flat=True)
        )
        self.assertEqual(numbers, {11, 2})

    def test_deleting_song_removes_album_song_but_keeps_album(self):
        AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)
        self.song_a.delete()
        self.assertEqual(AlbumSong.objects.count(), 0)
        self.assertTrue(Album.objects.filter(pk=self.album.pk).exists())

    def test_deleting_album_removes_album_song_but_keeps_song(self):
        AlbumSong.objects.create(album=self.album, song=self.song_a, track_number=1)
        self.album.delete()
        self.assertEqual(AlbumSong.objects.count(), 0)
        self.assertTrue(Song.objects.filter(pk=self.song_a.pk).exists())
