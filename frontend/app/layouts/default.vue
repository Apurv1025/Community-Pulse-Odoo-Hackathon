<template>
    <div>
        <Navbar v-if="!isAdminRoute && !isLoginRoute" />
        <slot />
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

// Check if current route starts with '/admin'
const isAdminRoute = computed(() => {
    return route.path.startsWith('/admin');
});

const isLoginRoute = computed(() => {
    return route.path.startsWith("/login")
})
</script>