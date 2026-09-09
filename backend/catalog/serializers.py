from django.db import transaction
from rest_framework import serializers

from .models import Album, AlbumSong, Artist, Song


# ---------------------------------------------------------------------------
# Artist
# ---------------------------------------------------------------------------


class ArtistAlbumSerializer(serializers.ModelSerializer):
    """Short album representation nested under an artist's detail payload."""

    class Meta:
        model = Album
        fields = ["id", "title", "release_year"]


class ArtistSerializer(serializers.ModelSerializer):
    albums_count = serializers.IntegerField(read_only=True, source="albums.count")
    albums = ArtistAlbumSerializer(many=True, read_only=True)

    class Meta:
        model = Artist
        fields = ["id", "name", "albums_count", "albums"]


class ArtistListSerializer(serializers.ModelSerializer):
    albums_count = serializers.IntegerField(read_only=True, source="albums.count")

    class Meta:
        model = Artist
        fields = ["id", "name", "albums_count"]


# ---------------------------------------------------------------------------
# Song
# ---------------------------------------------------------------------------


class SongListSerializer(serializers.ModelSerializer):
    albums_count = serializers.IntegerField(read_only=True, source="albums.count")

    class Meta:
        model = Song
        fields = ["id", "title", "albums_count"]


class SongAlbumMembershipSerializer(serializers.ModelSerializer):
    """One row of the "which albums is this song in" list on a song's detail view."""

    album = serializers.SerializerMethodField()

    class Meta:
        model = AlbumSong
        fields = ["album", "track_number"]

    def get_album(self, obj: AlbumSong):
        return {
            "id": obj.album_id,
            "title": obj.album.title,
            "release_year": obj.album.release_year,
            "artist": obj.album.artist.name,
        }


class SongSerializer(serializers.ModelSerializer):
    """Song detail serializer: includes every album the song appears in.

    This is the "watched field" for Song → Albums: `albums` is computed from
    `song.album_songs` (select_related to avoid N+1 queries) rather than stored,
    since a Song has no direct FK to Album (see docs/01_SPEC.md, business rule 1).
    """

    albums = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ["id", "title", "albums"]

    def get_albums(self, obj: Song):
        album_songs = obj.album_songs.select_related("album", "album__artist").order_by(
            "album__title", "track_number"
        )
        return SongAlbumMembershipSerializer(album_songs, many=True).data


# ---------------------------------------------------------------------------
# Album / AlbumSong (tracks)
# ---------------------------------------------------------------------------


class ArtistRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ["id", "name"]


class TrackSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ["id", "title"]


class AlbumTrackSerializer(serializers.ModelSerializer):
    """Read/write representation of a single track (AlbumSong).

    Accepts either `song_id` (an existing Song) or `new_song_title` to create a
    new Song on the fly, matching docs/02_PLAN.md section 3.2. Validates both the
    mutual exclusivity of song_id/new_song_title and the album-scoped uniqueness
    of track_number / song (mirroring the model's UniqueConstraints) so that
    conflicts surface as 400 validation errors instead of IntegrityError/500.
    """

    song = TrackSongSerializer(read_only=True)
    song_id = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(), source="song", write_only=True, required=False
    )
    new_song_title = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = AlbumSong
        fields = ["id", "song", "song_id", "new_song_title", "track_number"]

    def validate(self, attrs):
        has_song_id = "song" in attrs
        has_new_song_title = bool(attrs.get("new_song_title"))
        if has_song_id and has_new_song_title:
            raise serializers.ValidationError(
                "Укажите либо song_id, либо new_song_title, но не оба одновременно."
            )
        if not has_song_id and not has_new_song_title and self.instance is None:
            raise serializers.ValidationError(
                "Необходимо указать song_id (существующая песня) или new_song_title (новая песня)."
            )

        album = self.context.get("album") or getattr(self.instance, "album", None)
        track_number = attrs.get(
            "track_number", getattr(self.instance, "track_number", None)
        )
        song = attrs.get("song")

        if album is not None and track_number is not None:
            qs = AlbumSong.objects.filter(album=album, track_number=track_number)
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {
                        "track_number": [
                            f"Трек с номером {track_number} уже существует в этом альбоме."
                        ]
                    }
                )

        if album is not None and song is not None:
            qs = AlbumSong.objects.filter(album=album, song=song)
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"song_id": ["Эта песня уже добавлена в этот альбом."]}
                )

        return attrs

    def create(self, validated_data):
        new_song_title = validated_data.pop("new_song_title", None)
        if new_song_title:
            validated_data["song"] = Song.objects.create(title=new_song_title)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_song_title = validated_data.pop("new_song_title", None)
        if new_song_title:
            validated_data["song"] = Song.objects.create(title=new_song_title)
        return super().update(instance, validated_data)


class AlbumSerializer(serializers.ModelSerializer):
    """Album detail serializer, read/write, with a nested `tracks` list.

    On create, `tracks` accepts nested-write payloads: each item is either
    `{"song_id": <id>, "track_number": N}` or `{"new_song_title": "...", "track_number": N}`.
    The whole album + its tracks are created inside one transaction (see `create()`),
    so a duplicate track_number in the payload leaves no partially-created Album behind.
    """

    artist = ArtistRefSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(), source="artist", write_only=True
    )
    tracks = serializers.SerializerMethodField()
    tracks_input = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "artist",
            "artist_id",
            "release_year",
            "tracks",
            "tracks_input",
        ]

    def get_tracks(self, obj: Album):
        album_songs = obj.album_songs.select_related("song").order_by("track_number")
        return AlbumTrackSerializer(album_songs, many=True).data

    def to_internal_value(self, data):
        # The wire format (docs/02_PLAN.md) uses "tracks" for both request and
        # response bodies; internally we route write payloads through the
        # write-only "tracks_input" field to keep it separate from the
        # SerializerMethodField "tracks" used for output.
        if "tracks" in data and "tracks_input" not in data:
            data = {**data, "tracks_input": data["tracks"]}
        return super().to_internal_value(data)

    def validate_tracks_input(self, tracks):
        seen_numbers = set()
        for item in tracks:
            track_number = item.get("track_number")
            if track_number in seen_numbers:
                raise serializers.ValidationError(
                    f"Трек с номером {track_number} указан более одного раза."
                )
            seen_numbers.add(track_number)
        return tracks

    @transaction.atomic
    def create(self, validated_data):
        tracks_data = validated_data.pop("tracks_input", [])
        album = Album.objects.create(**validated_data)
        for track_data in tracks_data:
            track_serializer = AlbumTrackSerializer(data=track_data)
            track_serializer.is_valid(raise_exception=True)
            track_serializer.save(album=album)
        return album

    def update(self, instance, validated_data):
        validated_data.pop("tracks_input", None)
        return super().update(instance, validated_data)


class AlbumListSerializer(serializers.ModelSerializer):
    """Short album representation for the list endpoint."""

    artist = ArtistRefSerializer(read_only=True)
    tracks_count = serializers.IntegerField(read_only=True, source="album_songs.count")

    class Meta:
        model = Album
        fields = ["id", "title", "artist", "release_year", "tracks_count"]
