// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  runtimeConfig: {
    public: {
      appUrl: "http://localhost:3000",
      backendUrl: "http://localhost:8000",
      razorpayKey: "rzp_test_k19Yd58shg2QrK",
    },
  },

  modules: [
    "@nuxt/ui",
    "@nuxt/eslint",
    "@nuxt/fonts",
    "@nuxt/icon",
    "@nuxt/image",
    "@nuxt/scripts",
    [
      "@pinia/nuxt",
      {
        autoImports: ["defineStore", "acceptHMRUpdate"],
      },
    ],
    "pinia-plugin-persistedstate/nuxt",
    "@nuxtjs/leaflet",
  ],
  plugins: ["~/plugins/razorpay.client.ts"],
  imports: {
    dirs: ["stores"],
  },

  css: ["~/assets/css/main.css"],

  future: {
    compatibilityVersion: 4,
  },

  compatibilityDate: "2024-11-27",
});
