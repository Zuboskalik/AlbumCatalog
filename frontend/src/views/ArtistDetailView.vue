<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { useArtistsStore } from "../stores/artists";
import { getErrorMessage } from "../api/errors";
import StateMessage from "../components/StateMessage.vue";

const route = useRoute();
const store = useArtistsStore();

const editingName = ref("");
const saveError = ref<string | null>(null);
const saving = ref(false);

function load() {
  store.fetchOne(Number(route.params.id));
}

onMounted(load);
watch(() => route.params.id, load);
watch(
  () => store.current?.name,
  (name) => {
    editingName.value = name ?? "";
  },
  { immediate: true }
);

async function handleSave() {
  if (!store.current || !editingName.value.trim()) return;
  saving.value = true;
  saveError.value = null;
  try {
    await store.update(store.current.id, editingName.value.trim());
  } catch (error) {
    saveError.value = getErrorMessage(error);
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <RouterLink to="/artists" class="text-sm text-gray-500 hover:underline">&larr; Исполнители</RouterLink>

    <StateMessage :loading="store.loading" :error="store.error" class="mt-4" />

    <div v-if="!store.loading && !store.error && store.current" class="mt-4">
      <form class="mb-6 flex gap-2" @submit.prevent="handleSave">
        <input v-model="editingName" type="text" class="flex-1 rounded border border-gray-300 px-3 py-2" />
        <button
          type="submit"
          :disabled="saving || !editingName.trim()"
          class="rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50"
        >
          Сохранить
        </button>
      </form>
      <p v-if="saveError" class="-mt-4 mb-4 text-sm text-red-600">{{ saveError }}</p>

      <h2 class="mb-2 text-lg font-medium">Альбомы</h2>
      <ul v-if="store.current.albums.length > 0" class="divide-y divide-gray-200">
        <li v-for="album in store.current.albums" :key="album.id" class="py-2">
          <RouterLink :to="`/albums/${album.id}`" class="hover:underline">
            {{ album.title }} <span class="text-sm text-gray-500">({{ album.release_year }})</span>
          </RouterLink>
        </li>
      </ul>
      <p v-else class="text-gray-500">У этого исполнителя пока нет альбомов.</p>
    </div>
  </div>
</template>
