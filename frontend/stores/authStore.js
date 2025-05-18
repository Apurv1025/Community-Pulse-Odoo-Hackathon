import { defineStore } from "pinia";

export const useAuthStore = defineStore("authStore", {
  state: () => ({
    user: null,
    session: null,
  }),
  actions: {
    async fetchUser() {
      // Fetch the user from the backend using the session token
      const config = useRuntimeConfig();

      const { data, error } = await useFetch(
        config.public.backendUrl + "/users/me/",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${this.session}`,
          },
        }
      );

      if (error.value) {
        throw new Error(error.value.message || "Failed to fetch user");
      }

      this.user = data.value;
    },
    async registerUser(username, password, email, phone) {
      // Send a Post request to backend with username, password, email and phone
      const config = useRuntimeConfig();
      const { data, error } = await useFetch(
        config.public.backendUrl + "/register",
        {
          method: "POST",
          body: { username, password, email, phone }, // Send as object, Nuxt handles the JSON conversion
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (error.value) {
        throw new Error(error.value.message || "Registration failed");
      }

      this.session = data.value.access_token;
      await this.fetchUser();
    },
    async createUserSession(username, password) {
      // Send a Post request to backend with username and password
      const config = useRuntimeConfig();
      const { data, error } = await useFetch(
        config.public.backendUrl + "/api/login",
        {
          method: "POST",
          body: { username, password }, // Send as object, Nuxt handles the JSON conversion
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (error.value) {
        throw new Error(error.value.message || "Login failed");
      }

      this.session = data.value.access_token;
      await this.fetchUser();
    },
    deleteUserSession() {
      this.session = null;
      this.user = null;
    },
  },
  persist: true,
});
