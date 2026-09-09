<script setup lang="ts">
import { onMounted, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { useSongsStore } from "../stores/songs";
import StateMessage from "../components/StateMessage.vue";

const route = useRoute();
const store = useSongsStore();

function load() {
  store.fetchOne(Number(route.params.id));
}

onMounted(load);
watch(() => route.params.id, load);
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <RouterLink to="/songs" class="text-sm text-gray-500 hover:underline">&larr; Песни</RouterLink>

    <StateMessage :loading="store.loading" :error="store.error" class="mt-4" />

    <div v-if="!store.loading && !store.error && store.current" class="mt-4">
      <h1 class="mb-4 text-2xl font-semibold">{{ store.current.title }}</h1>

      <h2 class="mb-2 text-lg font-medium">Альбомы</h2>
      <p v-if="store.current.albums.length === 0" class="text-gray-500">
        Эта песня пока не входит ни в один альбом.
      </p>
      <table v-else class="w-full border-collapse text-left">
        <thead>
          <tr class="border-b border-gray-300 text-sm text-gray-500">
            <th class="py-2 pr-4">Исполнитель</th>
            <th class="py-2 pr-4">Альбом</th>
            <th class="py-2 pr-4">Год</th>
            <th class="py-2 pr-4">Трек №</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in store.current.albums"
            :key="`${entry.album.id}-${entry.track_number}`"
            class="border-b border-gray-100"
          >
            <td class="py-2 pr-4">{{ entry.album.artist }}</td>
            <td class="py-2 pr-4">
              <RouterLink :to="`/albums/${entry.album.id}`" class="hover:underline">
                {{ entry.album.title }}
              </RouterLink>
            </td>
            <td class="py-2 pr-4">{{ entry.album.release_year }}</td>
            <td class="py-2 pr-4">{{ entry.track_number }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
