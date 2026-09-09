// Mirrors backend/catalog/serializers.py — see docs/02_PLAN.md section 3 for the wire format.

export interface ArtistRef {
  id: number;
  name: string;
}

export interface Artist {
  id: number;
  name: string;
  albums_count: number;
}

export interface ArtistAlbumSummary {
  id: number;
  title: string;
  release_year: number;
}

export interface ArtistDetail extends Artist {
  albums: ArtistAlbumSummary[];
}

export interface Song {
  id: number;
  title: string;
  albums_count: number;
}

export interface SongAlbumMembership {
  album: {
    id: number;
    title: string;
    release_year: number;
    /** Plain artist name, as returned by SongAlbumMembershipSerializer.get_album(). */
    artist: string;
  };
  track_number: number;
}

export interface SongDetail {
  id: number;
  title: string;
  albums: SongAlbumMembership[];
}

export interface Track {
  id: number;
  song: {
    id: number;
    title: string;
  };
  track_number: number;
}

export interface Album {
  id: number;
  title: string;
  artist: ArtistRef;
  release_year: number;
  tracks_count: number;
}

export interface AlbumDetail {
  id: number;
  title: string;
  artist: ArtistRef;
  release_year: number;
  tracks: Track[];
}

/** One row of the nested `tracks` payload sent on Album create — either an
 * existing song (`song_id`) or a new one created on the fly (`new_song_title`). */
export interface TrackInput {
  song_id?: number;
  new_song_title?: string;
  track_number: number;
}

export interface AlbumCreateInput {
  title: string;
  artist_id: number;
  release_year: number;
  tracks?: TrackInput[];
}

export interface AlbumUpdateInput {
  title?: string;
  artist_id?: number;
  release_year?: number;
}
