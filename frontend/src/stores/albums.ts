import { defineStore } from "pinia";
import * as albumsApi from "../api/albums";
import { getErrorMessage } from "../api/errors";
import type {
  Album,
  AlbumCreateInput,
  AlbumDetail,
  AlbumUpdateInput,
  TrackInput,
} from "../types/models";

interface State {
  items: Album[];
  current: AlbumDetail | null;
  loading: boolean;
  error: string | null;
}

export const useAlbumsStore = defineStore("albums", {
  state: (): State => ({
    items: [],
    current: null,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchAll() {
      this.loading = true;
      this.error = null;
      try {
        this.items = await albumsApi.getAlbums();
      } catch (error) {
        this.error = getErrorMessage(error);
      } finally {
        this.loading = false;
      }
    },

    async fetchOne(id: number) {
      this.loading = true;
      this.error = null;
      try {
        this.current = await albumsApi.getAlbum(id);
      } catch (error) {
        this.error = getErrorMessage(error);
      } finally {
        this.loading = false;
      }
    },

    async create(payload: AlbumCreateInput) {
      const created = await albumsApi.createAlbum(payload);
      this.items.unshift({
        id: created.id,
        title: created.title,
        artist: created.artist,
        release_year: created.release_year,
        tracks_count: created.tracks.length,
      });
      return created;
    },

    async update(id: number, payload: AlbumUpdateInput) {
      const updated = await albumsApi.updateAlbum(id, payload);
      if (this.current?.id === id) {
        this.current = { ...this.current, ...updated, tracks: this.current.tracks };
      }
      const index = this.items.findIndex((a) => a.id === id);
      if (index !== -1) {
        this.items[index] = {
          ...this.items[index],
          title: updated.title,
          artist: updated.artist,
          release_year: updated.release_year,
        };
      }
      return updated;
    },

    async remove(id: number) {
      await albumsApi.deleteAlbum(id);
      this.items = this.items.filter((a) => a.id !== id);
    },

    async addTrack(albumId: number, payload: TrackInput) {
      const track = await albumsApi.addTrack(albumId, payload);
      if (this.current?.id === albumId) {
        this.current.tracks = [...this.current.tracks, track].sort(
          (a, b) => a.track_number - b.track_number
        );
      }
      return track;
    },

    async updateTrack(albumId: number, trackId: number, payload: Partial<TrackInput>) {
      const track = await albumsApi.updateTrack(albumId, trackId, payload);
      if (this.current?.id === albumId) {
        this.current.tracks = this.current.tracks
          .map((t) => (t.id === trackId ? track : t))
          .sort((a, b) => a.track_number - b.track_number);
      }
      return track;
    },

    async removeTrack(albumId: number, trackId: number) {
      await albumsApi.removeTrack(albumId, trackId);
      if (this.current?.id === albumId) {
        this.current.tracks = this.current.tracks.filter((t) => t.id !== trackId);
      }
    },
  },
});
