<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { useSongsStore } from "../stores/songs";
import { getErrorMessage } from "../api/errors";
import StateMessage from "../components/StateMessage.vue";

const store = useSongsStore();
const searchInput = ref("");
const newTitle = ref("");
const createError = ref<string | null>(null);
const creating = ref(false);
let debounceHandle: ReturnType<typeof setTimeout> | undefined;

onMounted(() => store.fetchAll());

watch(searchInput, (value) => {
  clearTimeout(debounceHandle);
  debounceHandle = setTimeout(() => store.search(value), 300);
});

async function handleCreate() {
  if (!newTitle.value.trim()) return;
  creating.value = true;
  createError.value = null;
  try {
    await store.create(newTitle.value.trim());
    newTitle.value = "";
  } catch (error) {
    createError.value = getErrorMessage(error);
  } finally {
    creating.value = false;
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <h1 class="mb-4 text-2xl font-semibold">Песни</h1>

    <input
      v-model="searchInput"
      type="text"
      placeholder="Поиск по названию…"
      class="mb-4 w-full rounded border border-gray-300 px-3 py-2"
    />

    <form class="mb-6 flex gap-2" @submit.prevent="handleCreate">
      <input
        v-model="newTitle"
        type="text"
        placeholder="Название новой песни"
        class="flex-1 rounded border border-gray-300 px-3 py-2"
      />
      <button
        type="submit"
        :disabled="creating || !newTitle.trim()"
        class="rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50"
      >
        Добавить
      </button>
    </form>
    <p v-if="createError" class="-mt-4 mb-4 text-sm text-red-600">{{ createError }}</p>

    <StateMessage
      :loading="store.loading"
      :error="store.error"
      :empty="store.items.length === 0"
      empty-text="Ничего не найдено."
    />

    <ul v-if="!store.loading && !store.error" class="divide-y divide-gray-200">
      <li v-for="song in store.items" :key="song.id" class="py-3">
        <RouterLink :to="`/songs/${song.id}`" class="hover:underline">
          {{ song.title }}
          <span class="text-sm text-gray-500">({{ song.albums_count }} альбомов)</span>
        </RouterLink>
      </li>
    </ul>
  </div>
</template>
