<template>
    <nav class="bg-gray-900 p-4">
        <div class="container mx-auto">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <!-- Left section with logo/brand -->
                <div class="flex items-center mb-4 md:mb-0">
                    <NuxtLink to="/" class="text-white text-xl font-bold">Community Pulse Admin</NuxtLink>
                </div>

                <!-- Middle section with event/user search -->
                <div class="w-full md:w-1/2 mb-4 md:mb-0 flex space-x-2">
                    <form class="flex w-1/2" @submit.prevent="searchEvents">
                        <input v-model="searchEventTerm" type="text" placeholder="Search events..."
                            class="w-full px-4 py-2 rounded-l focus:outline-none">
                        <button type="submit"
                            class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600 focus:outline-none">
                            Search Events
                        </button>
                    </form>
                    <form class="flex w-1/2" @submit.prevent="searchUsers">
                        <input v-model="searchUserTerm" type="text" placeholder="Search users..."
                            class="w-full px-4 py-2 rounded-l focus:outline-none">
                        <button type="submit"
                            class="bg-green-500 text-white px-4 py-2 rounded-r hover:bg-green-600 focus:outline-none">
                            Search Users
                        </button>
                    </form>
                </div>

                <!-- Right section with admin actions and logout -->
                <div class="flex items-center space-x-4">
                    <NuxtLink to="/admin/requestevents" class="text-white hover:text-yellow-300">
                        Pending Events
                    </NuxtLink>
                    <NuxtLink to="/admin/users" class="text-white hover:text-yellow-300">
                        Manage Users
                    </NuxtLink>
                    <button class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 focus:outline-none"
                        @click="logout">
                        Logout
                    </button>
                </div>
            </div>
        </div>
    </nav>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();

const searchEventTerm = ref('');
const searchUserTerm = ref('');

// Route to event search results page
function searchEvents() {
    if (searchEventTerm.value.trim()) {
        router.push(`/search/${encodeURIComponent(searchEventTerm.value.trim())}`);
    }
}

// Route to admin user search results page
function searchUsers() {
    if (searchUserTerm.value.trim()) {
        router.push(`/admin/usersearch/${encodeURIComponent(searchUserTerm.value.trim())}`);
    }
}

// Logout user
function logout() {
    authStore.deleteUserSession();
    router.push('/login');
}
</script>

<style scoped>
/* Additional custom styles for admin navbar can be added here */
</style>