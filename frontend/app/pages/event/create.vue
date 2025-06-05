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
    event_type: 'Free', // Default to Free
    registration_start: '',
    registration_end: '',
    address: '',
    city: '',
    state: '',
    latitude: '',
    longitude: '',
    max_capacity: '',
    error: '',
    isLoading: false,
    locationLoading: false,
    showFileUpload: false,
    createdEventId: null
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

// Get user's current location
const getCurrentLocation = () => {
    if (!navigator.geolocation) {
        toast.add({
            title: 'Error',
            description: 'Geolocation is not supported by your browser',
            color: 'error'
        });
        return;
    }

    state.locationLoading = true;
    navigator.geolocation.getCurrentPosition(
        (position) => {
            state.latitude = position.coords.latitude.toString();
            state.longitude = position.coords.longitude.toString();
            state.locationLoading = false;
            toast.add({
                title: 'Success',
                description: 'Location successfully captured',
                color: 'success'
            });
        },
        (error) => {
            state.locationLoading = false;
            let errorMsg = 'Failed to get your location';
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg = 'Location permission denied';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg = 'Location information unavailable';
                    break;
                case error.TIMEOUT:
                    errorMsg = 'The request to get location timed out';
                    break;
            }
            toast.add({
                title: 'Error',
                description: errorMsg,
                color: 'error'
            });
        }
    );
};

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

    // Validate latitude and longitude
    if (!state.latitude || !state.longitude) {
        state.error = 'Latitude and longitude are required. Use the "Get Current Location" button or enter them manually.';
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
            type: state.event_type, // Send as 'type' to the server
            registration_start: state.registration_start,
            registration_end: state.registration_end,
            address: state.address,
            city: state.city,
            state: state.state,
            latitude: state.latitude,
            longitude: state.longitude,
            max_capacity: parseInt(state.max_capacity) || null
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

        // Save the created event ID and show the file upload component
        state.createdEventId = createdEvent.id;
        state.showFileUpload = true;

        toast.add({
            title: 'Success',
            description: 'Event created successfully. You can now upload images for this event.',
            color: 'success'
        });

        // Don't redirect to home page yet, let the user upload images first
        // router.push('/');
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

const finishAndGoHome = () => {
    router.push('/');
};
</script>

<template>
    <UContainer class="py-8">
        <!-- Event Creation Form -->
        <UCard v-if="!state.showFileUpload" class="w-full max-w-3xl mx-auto">
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

                    <UFormField label="Event Type" name="event_type" required>
                        <USelect v-model="state.event_type" :items="['Free', 'Paid']" placeholder="Select event type"
                            class="w-full" required />
                    </UFormField>

                    <UFormField label="Max Capacity" name="max_capacity" required>
                        <UInput v-model="state.max_capacity" type="number" min="1"
                            placeholder="Maximum number of participants" class="w-full" required />
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

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Latitude" name="latitude" required>
                            <UInput v-model="state.latitude" type="text" placeholder="Latitude" class="w-full"
                                required />
                        </UFormField>

                        <UFormField label="Longitude" name="longitude" required>
                            <UInput v-model="state.longitude" type="text" placeholder="Longitude" class="w-full"
                                required />
                        </UFormField>
                    </div>

                    <div class="flex justify-center mt-4">
                        <UButton label="Get Current Location" type="button" variant="solid" color="secondary" size="xl"
                            class="px-8" :loading="state.locationLoading" @click="getCurrentLocation" />
                    </div>
                </div>

                <div class="flex justify-center mt-4">
                    <UButton label="Create Event" type="submit" variant="solid" color="primary" size="xl" class="px-8"
                        :loading="state.isLoading" />
                </div>

                <p v-if="state.error" class="text-red-500 text-sm text-center">{{ state.error }}</p>
            </UForm>
        </UCard>

        <!-- File Upload Component (shown after event creation) -->
        <div v-else>
            <h2 class="text-2xl font-semibold text-center mb-4">Upload Event Images</h2>
            <p class="text-center text-gray-600 mb-6">Upload up to 5 images for your event</p>

            <!-- File upload component with dynamically created event ID -->
            <fileUpload :linksubset="`/event/${state.createdEventId}`" />

            <div class="flex justify-center mt-6">
                <UButton label="Finish & Go to Home" icon="i-lucide-home" color="primary" @click="finishAndGoHome" />
            </div>
        </div>
    </UContainer>
</template>