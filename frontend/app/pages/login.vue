<template>
    <UContainer class="flex flex-col items-center justify-center gap-4 h-screen">
        <UCard class="w-full max-w-md">
            <LoginCard />
        </UCard>
    </UContainer>
</template>

<script setup>
import { useAuthStore } from "../../stores/authStore";

const store = useAuthStore();
const router = useRouter();

// Check if user is already authenticated
onMounted(() => {
    if (store.user) {
        // If user is already logged in, redirect based on admin status
        if (store.user.isAdmin) {
            router.push('/admin');
        } else {
            router.push('/');
        }
    }
});
</script>

<style scoped></style>