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
      path: "/artists/:id",
      name: "artist-detail",
      component: () => import("../views/ArtistDetailView.vue"),
    },
    {
      path: "/albums",
      name: "albums",
      component: () => import("../views/AlbumListView.vue"),
    },
    {
      path: "/albums/new",
      name: "album-new",
      component: () => import("../views/AlbumFormView.vue"),
    },
    {
      path: "/albums/:id",
      name: "album-detail",
      component: () => import("../views/AlbumDetailView.vue"),
    },
    {
      path: "/songs",
      name: "songs",
      component: () => import("../views/SongListView.vue"),
    },
    {
      path: "/songs/:id",
      name: "song-detail",
      component: () => import("../views/SongDetailView.vue"),
    },
  ],
});

export default router;
