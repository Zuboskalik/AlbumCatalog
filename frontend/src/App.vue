<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="min-h-screen bg-white text-gray-900">
    <nav class="flex gap-4 border-b border-gray-200 px-6 py-4">
      <RouterLink to="/artists" class="hover:underline">Artists</RouterLink>
      <RouterLink to="/albums" class="hover:underline">Albums</RouterLink>
      <RouterLink to="/songs" class="hover:underline">Songs</RouterLink>
    </nav>
    <RouterView />
  </div>
</template>
