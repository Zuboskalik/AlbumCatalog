from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def current_year_plus_one():
    return timezone.now().year + 1


class Artist(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="albums"
    )
    release_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1860),
            MaxValueValidator(current_year_plus_one),
        ]
    )
    songs = models.ManyToManyField(
        "Song", through="AlbumSong", related_name="albums"
    )

    class Meta:
        ordering = ["artist__name", "release_year", "title"]

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class Song(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class AlbumSong(models.Model):
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name="album_songs"
    )
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE, related_name="album_songs"
    )
    track_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ["album", "track_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["album", "track_number"],
                name="uniq_album_track_number",
            ),
            models.UniqueConstraint(
                fields=["album", "song"],
                name="uniq_album_song",
            ),
        ]

    def __str__(self):
        return f"{self.album} — #{self.track_number} {self.song}"
