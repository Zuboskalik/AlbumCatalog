import { defineStore } from "pinia";
import * as artistsApi from "../api/artists";
import { getErrorMessage } from "../api/errors";
import type { Artist, ArtistDetail } from "../types/models";

interface State {
  items: Artist[];
  current: ArtistDetail | null;
  loading: boolean;
  error: string | null;
}

export const useArtistsStore = defineStore("artists", {
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
        this.items = await artistsApi.getArtists();
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
        this.current = await artistsApi.getArtist(id);
      } catch (error) {
        this.error = getErrorMessage(error);
      } finally {
        this.loading = false;
      }
    },

    async create(name: string) {
      const created = await artistsApi.createArtist(name);
      this.items.push({ id: created.id, name: created.name, albums_count: created.albums_count });
      return created;
    },

    async update(id: number, name: string) {
      const updated = await artistsApi.updateArtist(id, name);
      const index = this.items.findIndex((a) => a.id === id);
      if (index !== -1) this.items[index] = { ...this.items[index], name: updated.name };
      if (this.current?.id === id) this.current = { ...this.current, name: updated.name };
      return updated;
    },

    async remove(id: number) {
      await artistsApi.deleteArtist(id);
      this.items = this.items.filter((a) => a.id !== id);
    },
  },
});
