<script setup lang="ts">
import { useAuthStore } from "../../../stores/authStore";

const store = useAuthStore();
const router = useRouter();
const config = useRuntimeConfig();
const toast = useToast();

const state = reactive({
    event_name: '',
    event_description: '',
    start_date: '',
    end_date: '',
    category: '',
    registration_start: '',
    registration_end: '',
    address: '',
    city: '',
    state: '',
    img_url: '',
    error: '',
    isLoading: false
});

// Default categories list
const categories = ref([
    'Garage Sales',
    'Sports Matches',
    'Community Classes',
    'Volunteer Opportunities',
    'Exhibitions',
    'Small Festivals or Celebrations',
    'Other'
]);

// No category fetching, just use the default categories

const createEvent = async () => {
    state.isLoading = true;
    state.error = '';

    // Validate dates
    const startDate = new Date(state.start_date);
    const endDate = new Date(state.end_date);
    const regStartDate = new Date(state.registration_start);
    const regEndDate = new Date(state.registration_end);

    if (endDate < startDate) {
        state.error = 'End date cannot be before start date';
        state.isLoading = false;
        toast.add({
            title: 'Validation Error',
            description: state.error,
            color: 'error'
        });
        return;
    }

    if (regEndDate < regStartDate) {
        state.error = 'Registration end date cannot be before registration start date';
        state.isLoading = false;
        toast.add({
            title: 'Validation Error',
            description: state.error,
            color: 'error'
        });
        return;
    }

    try {
        // Create an event object matching the backend EventCreate model
        const eventData = {
            event_name: state.event_name,
            event_description: state.event_description,
            start_date: state.start_date,
            end_date: state.end_date,
            category: state.category,
            registration_start: state.registration_start,
            registration_end: state.registration_end,
            address: state.address,
            city: state.city,
            state: state.state,
            img_url: state.img_url
        };

        console.log('Submitting event:', eventData);

        // Make API call to the backend endpoint
        const response = await fetch(config.public.backendUrl + '/event/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${store.session}` // Use auth token from store
            },
            body: JSON.stringify(eventData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create event');
        }

        const createdEvent = await response.json();
        console.log('Event created:', createdEvent);

        toast.add({
            title: 'Success',
            description: 'Event created successfully',
            color: 'success'
        });

        router.push('/');
    } catch (error: Error | unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to create event. Please try again.';
        state.error = errorMessage;
        toast.add({
            title: 'Event Creation Failed',
            description: state.error,
            color: 'error'
        });
    } finally {
        state.isLoading = false;
    }
};
</script>

<template>
    <UContainer class="py-8">
        <UCard class="w-full max-w-3xl mx-auto">
            <template #header>
                <div class="flex flex-col gap-1">
                    <h2 class="text-xl font-semibold">Create New Event</h2>
                    <p class="text-sm text-gray-500">Fill in the details to create a new community event</p>
                </div>
            </template>

            <UForm :state="state" class="flex flex-col gap-6" @submit.prevent="createEvent">
                <!-- Basic Event Info -->
                <div class="space-y-4">
                    <h3 class="font-medium">Event Details</h3>
                    <UFormField label="Event Name" name="event_name" required>
                        <UInput v-model="state.event_name" type="text" placeholder="Enter event name" class="w-full"
                            required />
                    </UFormField>

                    <UFormField label="Event Description" name="event_description" required>
                        <UTextarea v-model="state.event_description" placeholder="Describe your event..." rows="4"
                            class="w-full" required />
                    </UFormField>

                    <UFormField label="Category" name="category" required>
                        <USelect v-model="state.category" :items="categories" placeholder="Select event category"
                            class="w-full" required />
                    </UFormField>

                    <UFormField label="Image URL" name="img_url" required>
                        <UInput v-model="state.img_url" type="url" placeholder="URL to event image" class="w-full"
                            required />
                    </UFormField>
                </div>

                <!-- Event Dates -->
                <div class="space-y-4">
                    <h3 class="font-medium">Event Schedule</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Start Date" name="start_date" required>
                            <UInput v-model="state.start_date" type="datetime-local" class="w-full" required />
                        </UFormField>

                        <UFormField label="End Date" name="end_date" required>
                            <UInput v-model="state.end_date" type="datetime-local" class="w-full" required />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Registration Start" name="registration_start" required>
                            <UInput v-model="state.registration_start" type="datetime-local" class="w-full" required />
                        </UFormField>

                        <UFormField label="Registration End" name="registration_end" required>
                            <UInput v-model="state.registration_end" type="datetime-local" class="w-full" required />
                        </UFormField>
                    </div>
                </div>

                <!-- Event Location -->
                <div class="space-y-4">
                    <h3 class="font-medium">Event Location</h3>
                    <UFormField label="Address" name="address" required>
                        <UInput v-model="state.address" type="text" placeholder="Street address" class="w-full"
                            required />
                    </UFormField>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="City" name="city" required>
                            <UInput v-model="state.city" type="text" placeholder="City" class="w-full" required />
                        </UFormField>

                        <UFormField label="State" name="state" required>
                            <UInput v-model="state.state" type="text" placeholder="State" class="w-full" required />
                        </UFormField>
                    </div>
                </div>

                <div class="flex justify-center mt-4">
                    <UButton label="Create Event" type="submit" variant="solid" color="primary" size="xl" class="px-8"
                        :loading="state.isLoading" />
                </div>

                <p v-if="state.error" class="text-red-500 text-sm text-center">{{ state.error }}</p>
            </UForm>
        </UCard>
    </UContainer>
</template>