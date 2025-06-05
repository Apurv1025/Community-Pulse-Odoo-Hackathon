<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui'
import { useAuthStore } from "../../stores/authStore";

const store = useAuthStore()
const router = useRouter()
const toast = useToast()

const items = [
  {
    label: 'Login',
    description: 'Enter your credentials to access your account.',
    icon: 'i-lucide-log-in',
    slot: 'account' as const
  },
  {
    label: 'Register',
    description: 'Create a new account to get started.',
    icon: 'i-lucide-user-pen',
    slot: 'password' as const
  }
] satisfies TabsItem[]

const state = reactive({
  username: '',
  password: '',
  email: '',
  phone: '',
  newPassword: '',
  loginError: '',
  registerError: '',
  isLoading: false
})

const login = async () => {
  state.isLoading = true
  state.loginError = ''

  try {
    await store.createUserSession(state.username, state.password)
    toast.add({
      title: 'Success',
      description: 'You have been logged in successfully',
      color: 'success'
    })
    console.log(store.user)

    // Check if the user is admin and redirect accordingly
    if (store.user && store.user.isAdmin) {
      router.push('/admin')
    } else {
      router.push('/')
    }

    // Reload the page to ensure all components update with user state
    setTimeout(() => {
      window.location.reload()
    }, 100)
  } catch (error: Error | unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Login failed. Please try again.';
    state.loginError = errorMessage;
    toast.add({
      title: 'Login failed',
      description: state.loginError,
      color: 'error'
    })
  } finally {
    state.isLoading = false
  }
}

const register = async () => {
  state.isLoading = true
  state.registerError = ''

  try {
    await store.registerUser(state.username, state.newPassword, state.email, state.phone)
    toast.add({
      title: 'Success',
      description: 'Registration successful! You are now logged in.',
      color: 'success'
    })

    // Newly registered users aren't admins, redirect to home
    router.push('/')

    // Reload the page to ensure all components update with user state
    setTimeout(() => {
      window.location.reload()
    }, 100)
  } catch (error: Error | unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Registration failed. Please try again.';
    state.registerError = errorMessage;
    toast.add({
      title: 'Registration failed',
      description: state.registerError,
      color: 'error'
    })
  } finally {
    state.isLoading = false
  }
}
</script>

<template>
  <UTabs :items="items" variant="pill" class="gap-4 w-full" :ui="{ trigger: 'grow' }">
    <template #account="{ item }">
      <p class="text-muted mb-4">
        {{ item.description }}
      </p>

      <UForm :state="state" class="flex flex-col gap-4" @submit.prevent="login">
        <UFormField label="Username" name="username" required>
          <UInput v-model="state.username" type="text" class="w-full" required />
        </UFormField>
        <UFormField label="Password" name="password" required>
          <UInput v-model="state.password" type="password" class="w-full" required />
        </UFormField>

        <UButton label="Login Now" type="submit" variant="subtle" size="xl" class="self-center"
          :loading="state.isLoading" />
        <p v-if="state.loginError" class="text-red-500 text-sm text-center">{{ state.loginError }}</p>
      </UForm>
    </template>

    <template #password="{ item }">
      <p class="text-muted mb-4">
        {{ item.description }}
      </p>

      <UForm :state="state" class="flex flex-col gap-4" @submit.prevent="register">
        <UFormField label="Username" name="username" required>
          <UInput v-model="state.username" type="text" required class="w-full" />
        </UFormField>
        <UFormField label="Email" name="email" required>
          <UInput v-model="state.email" type="email" required class="w-full" />
        </UFormField>
        <UFormField label="Phone" name="phone" required>
          <UInput v-model="state.phone" type="tel" required class="w-full" />
        </UFormField>
        <UFormField label="Password" name="new" required>
          <UInput v-model="state.newPassword" type="text" minlength="8" required class="w-full" />
        </UFormField>

        <UButton label="Register Now" type="submit" variant="subtle" size="xl" class="self-center"
          :loading="state.isLoading" />
        <p v-if="state.registerError" class="text-red-500 text-sm text-center">{{ state.registerError }}</p>
      </UForm>
    </template>
  </UTabs>
</template>
