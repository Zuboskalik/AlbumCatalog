import { defineStore } from "pinia";
import * as songsApi from "../api/songs";
import { getErrorMessage } from "../api/errors";
import type { Song, SongDetail } from "../types/models";

interface State {
  items: Song[];
  current: SongDetail | null;
  loading: boolean;
  error: string | null;
  query: string;
}

export const useSongsStore = defineStore("songs", {
  state: (): State => ({
    items: [],
    current: null,
    loading: false,
    error: null,
    query: "",
  }),
  actions: {
    async fetchAll() {
      this.loading = true;
      this.error = null;
      try {
        this.items = await songsApi.getSongs();
      } catch (error) {
        this.error = getErrorMessage(error);
      } finally {
        this.loading = false;
      }
    },

    async search(query: string) {
      this.query = query;
      this.loading = true;
      this.error = null;
      try {
        this.items = await songsApi.getSongs(query);
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
        this.current = await songsApi.getSong(id);
      } catch (error) {
        this.error = getErrorMessage(error);
      } finally {
        this.loading = false;
      }
    },

    async create(title: string) {
      const created = await songsApi.createSong(title);
      this.items.unshift({ id: created.id, title: created.title, albums_count: 0 });
      return created;
    },

    async remove(id: number) {
      await songsApi.deleteSong(id);
      this.items = this.items.filter((s) => s.id !== id);
    },
  },
});
