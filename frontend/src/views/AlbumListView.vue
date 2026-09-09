<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { useAlbumsStore } from "../stores/albums";
import { useArtistsStore } from "../stores/artists";
import StateMessage from "../components/StateMessage.vue";

const albumsStore = useAlbumsStore();
const artistsStore = useArtistsStore();
const artistFilter = ref<number | "">("");

onMounted(() => {
  albumsStore.fetchAll();
  artistsStore.fetchAll();
});

const filteredAlbums = computed(() => {
  if (artistFilter.value === "") return albumsStore.items;
  return albumsStore.items.filter((album) => album.artist.id === artistFilter.value);
});
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <div class="mb-4 flex items-center justify-between">
      <h1 class="text-2xl font-semibold">Альбомы</h1>
      <RouterLink to="/albums/new" class="rounded bg-gray-900 px-4 py-2 text-white">
        + Новый альбом
      </RouterLink>
    </div>

    <select v-model="artistFilter" class="mb-4 rounded border border-gray-300 px-3 py-2">
      <option value="">Все исполнители</option>
      <option v-for="artist in artistsStore.items" :key="artist.id" :value="artist.id">
        {{ artist.name }}
      </option>
    </select>

    <StateMessage
      :loading="albumsStore.loading"
      :error="albumsStore.error"
      :empty="filteredAlbums.length === 0"
      empty-text="Альбомов пока нет."
    />

    <ul v-if="!albumsStore.loading && !albumsStore.error" class="divide-y divide-gray-200">
      <li v-for="album in filteredAlbums" :key="album.id" class="py-3">
        <RouterLink :to="`/albums/${album.id}`" class="hover:underline">
          {{ album.title }}
          <span class="text-sm text-gray-500">
            — {{ album.artist.name }}, {{ album.release_year }} ({{ album.tracks_count }} треков)
          </span>
        </RouterLink>
      </li>
    </ul>
  </div>
</template>
