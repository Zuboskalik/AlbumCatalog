import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/artists" },
    {
      path: "/artists",
      name: "artists",
      component: () => import("../views/ArtistListView.vue"),
    },
    {
      path: "/albums",
      name: "albums",
      component: () => import("../views/AlbumListView.vue"),
    },
    {
      path: "/songs",
      name: "songs",
      component: () => import("../views/SongListView.vue"),
    },
  ],
});

export default router;
