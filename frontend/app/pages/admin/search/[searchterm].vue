<template>
    <div>
        <AdminNavbar />
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold mb-6 text-indigo-800">Admin Search Results for "{{ searchTerm }}"</h1>

            <!-- Loading state -->
            <div v-if="isLoading" class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500" />
            </div>

            <!-- Error state -->
            <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <p>{{ error }}</p>
            </div>

            <!-- No results state -->
            <div v-else-if="users && users.length === 0" class="text-center py-10">
                <p class="text-xl text-gray-600">No users found matching "{{ searchTerm }}"</p>
                <NuxtLink to="/admin/users"
                    class="mt-4 inline-block bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                    View All Users
                </NuxtLink>
            </div>

            <!-- Results grid -->
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div v-for="user in users" :key="user.username" class="bg-white rounded shadow p-6 flex flex-col gap-2">
                    <div class="font-bold text-lg text-indigo-700">{{ user.username }}</div>
                    <div class="text-gray-700">{{ user.email }}</div>
                    <div class="text-gray-500 text-sm">Name: {{ user.full_name || 'N/A' }}</div>
                    <div class="text-gray-500 text-sm">Phone: {{ user.phone || 'N/A' }}</div>
                    <div class="text-gray-500 text-sm">Role: <span class="font-semibold">{{ user.isAdmin ? 'Admin' : 'User' }}</span></div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../../../stores/authStore';
import AdminNavbar from '../../../components/AdminNavbar.vue';

const route = useRoute();
const authStore = useAuthStore();

// Get search term from route params
const searchTerm = ref(route.params.searchterm || '');

// State variables
const users = ref([]);
const isLoading = ref(true);
const error = ref(null);

// Fetch users based on search term (admin endpoint)
async function fetchUserSearchResults() {
    isLoading.value = true;
    error.value = null;

    try {
        const config = useRuntimeConfig();
        const { data, error: fetchError } = await useFetch(
            `${config.public.backendUrl}/usersearch/${encodeURIComponent(searchTerm.value)}`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.session}`
                }
            }
        );

        if (fetchError.value) {
            throw new Error(fetchError.value.message || 'Failed to fetch user search results');
        }

        users.value = data.value || [];
    } catch (err) {
        console.error('Error fetching user search results:', err);
        error.value = 'Failed to load user search results. Please try again.';
    } finally {
        isLoading.value = false;
    }
}

// Fetch users when component is mounted
onMounted(() => {
    fetchUserSearchResults();
});
</script>

<style scoped>
/* Add any custom styles if needed */
</style>