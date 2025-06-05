<script setup>
import { useAuthStore } from "../../../../stores/authStore";

const store = useAuthStore();
const router = useRouter();
const config = useRuntimeConfig();
const toast = useToast();
const route = useRoute();

// Get the event ID from the route
const eventId = computed(() => route.params.id);

// State to track form data and loading state
const state = reactive({
    event_name: '',
    event_description: '',
    start_date: '',
    end_date: '',
    category: '',
    event_type: '', // Added event_type 
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
    fetchLoading: true,
    locationLoading: false
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

// Track which fields have been modified
const modifiedFields = reactive({
    event_name: false,
    event_description: false,
    start_date: false,
    end_date: false,
    category: false,
    event_type: false, // Added event_type
    registration_start: false,
    registration_end: false,
    address: false,
    city: false,
    state: false,
    latitude: false,
    longitude: false
});

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
            // Format to appropriate number of decimal places to avoid extremely long values
            state.latitude = parseFloat(position.coords.latitude.toFixed(6)).toString();
            state.longitude = parseFloat(position.coords.longitude.toFixed(6)).toString();
            modifiedFields.latitude = true;
            modifiedFields.longitude = true;
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

// Fetch the current event data
const fetchEvent = async () => {
    state.fetchLoading = true;
    try {
        const response = await fetch(`${config.public.backendUrl}/event/${eventId.value}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${store.session}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch event details');
        }

        // Parse response which may include both event and images
        const data = await response.json();
        console.log("API Response:", data);

        // Extract event data based on the response format
        const eventData = data.event || data;

        // Format datetime fields for input type="datetime-local"
        const formatDate = (dateString) => {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toISOString().slice(0, 16); // Format: YYYY-MM-DDTHH:MM
        };

        // Populate form with existing data
        state.event_name = eventData.event_name || '';
        state.event_description = eventData.event_description || '';
        state.start_date = formatDate(eventData.start_date);
        state.end_date = formatDate(eventData.end_date);
        state.category = eventData.category || '';
        state.event_type = eventData.type || ''; // Get the type field from backend
        state.registration_start = formatDate(eventData.registration_start);
        state.registration_end = formatDate(eventData.registration_end);
        state.address = eventData.address || '';
        state.city = eventData.city || '';
        state.state = eventData.state || '';
        state.latitude = eventData.latitude?.toString() || '';
        state.longitude = eventData.longitude?.toString() || '';
        state.max_capacity = eventData.max_capacity ? eventData.max_capacity.toString() : '';

    } catch (error) {
        console.error('Error fetching event:', error);
        toast.add({
            title: 'Error',
            description: error.message || 'Failed to load event data',
            color: 'error'
        });
    } finally {
        state.fetchLoading = false;
    }
};

// Call fetch on mount
onMounted(fetchEvent);

// Field change handler to track modifications
const handleFieldChange = (field) => {
    modifiedFields[field] = true;
};

// Update event handler
const updateEvent = async () => {
    state.isLoading = true;
    state.error = '';

    // Optional validation for dates if they've been modified
    if ((modifiedFields.start_date && modifiedFields.end_date) ||
        (modifiedFields.registration_start && modifiedFields.registration_end)) {

        const startDate = new Date(state.start_date);
        const endDate = new Date(state.end_date);
        const regStartDate = new Date(state.registration_start);
        const regEndDate = new Date(state.registration_end);

        if (modifiedFields.start_date && modifiedFields.end_date && endDate < startDate) {
            state.error = 'End date cannot be before start date';
            state.isLoading = false;
            toast.add({
                title: 'Validation Error',
                description: state.error,
                color: 'error'
            });
            return;
        }

        if (modifiedFields.registration_start && modifiedFields.registration_end && regEndDate < regStartDate) {
            state.error = 'Registration end date cannot be before registration start date';
            state.isLoading = false;
            toast.add({
                title: 'Validation Error',
                description: state.error,
                color: 'error'
            });
            return;
        }
    }

    try {
        // Create update object with only modified fields
        const updateData = {};
        Object.keys(modifiedFields).forEach(field => {
            if (modifiedFields[field]) {
                // Special handling for max_capacity to convert to number
                if (field === 'max_capacity') {
                    updateData[field] = parseInt(state[field]) || null;
                }
                // Special handling for event_type to send as 'type' to the server
                else if (field === 'event_type') {
                    updateData['type'] = state[field];
                }
                else {
                    updateData[field] = state[field];
                }
            }
        });

        // Only proceed if there are changes
        if (Object.keys(updateData).length === 0) {
            toast.add({
                title: 'No Changes',
                description: 'No changes were made to the event',
                color: 'info'
            });
            state.isLoading = false;
            return;
        }

        console.log('Updating event with data:', updateData);

        // Make API call to update the event
        const response = await fetch(`${config.public.backendUrl}/event/edit/${eventId.value}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${store.session}`
            },
            body: JSON.stringify(updateData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update event');
        }

        const updatedEvent = await response.json();
        console.log('Event updated:', updatedEvent);

        toast.add({
            title: 'Success',
            description: 'Event updated successfully',
            color: 'success'
        });

        // Navigate back to event details or events list
        router.push(`/event/${eventId.value}`);
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to update event. Please try again.';
        state.error = errorMessage;
        toast.add({
            title: 'Update Failed',
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
                    <h2 class="text-xl font-semibold">Update Event</h2>
                    <p class="text-sm text-gray-500">Edit the details of your event</p>
                </div>
            </template>

            <div v-if="state.fetchLoading" class="flex justify-center py-8">
                <UButton loading variant="ghost" />
            </div>

            <UForm v-else :state="state" class="flex flex-col gap-6" @submit.prevent="updateEvent">
                <!-- Basic Event Info -->
                <div class="space-y-4">
                    <h3 class="font-medium">Event Details</h3>
                    <UFormField label="Event Name" name="event_name">
                        <UInput v-model="state.event_name" type="text" placeholder="Enter event name" class="w-full"
                            @input="handleFieldChange('event_name')" />
                    </UFormField>

                    <UFormField label="Event Description" name="event_description">
                        <UTextarea v-model="state.event_description" placeholder="Describe your event..." rows="4"
                            class="w-full" @input="handleFieldChange('event_description')" />
                    </UFormField>

                    <UFormField label="Category" name="category">
                        <USelect v-model="state.category" :items="categories" placeholder="Select event category"
                            class="w-full" @input="handleFieldChange('category')" />
                    </UFormField>

                    <UFormField label="Event Type" name="event_type"> <!-- Added event_type -->
                        <UInput v-model="state.event_type" type="text" placeholder="Event type cannot be changed"
                            class="w-full" disabled />
                    </UFormField>

                    <UFormField label="Max Capacity" name="max_capacity">
                        <UInput type="text" inputmode="numeric" placeholder="Maximum number of participants"
                            class="w-full" :value="state.max_capacity"
                            @keypress="(e) => { if (!/[0-9]/.test(e.key)) e.preventDefault(); }" @input="(e) => {
                                state.max_capacity = e.target.value.replace(/[^0-9]/g, '');
                                handleFieldChange('max_capacity');
                            }" />
                    </UFormField>
                </div>

                <!-- Event Dates -->
                <div class="space-y-4">
                    <h3 class="font-medium">Event Schedule</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Start Date" name="start_date">
                            <UInput v-model="state.start_date" type="datetime-local" class="w-full"
                                @input="handleFieldChange('start_date')" />
                        </UFormField>

                        <UFormField label="End Date" name="end_date">
                            <UInput v-model="state.end_date" type="datetime-local" class="w-full"
                                @input="handleFieldChange('end_date')" />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Registration Start" name="registration_start">
                            <UInput v-model="state.registration_start" type="datetime-local" class="w-full"
                                @input="handleFieldChange('registration_start')" />
                        </UFormField>

                        <UFormField label="Registration End" name="registration_end">
                            <UInput v-model="state.registration_end" type="datetime-local" class="w-full"
                                @input="handleFieldChange('registration_end')" />
                        </UFormField>
                    </div>
                </div>

                <!-- Event Location -->
                <div class="space-y-4">
                    <h3 class="font-medium">Event Location</h3>
                    <UFormField label="Address" name="address">
                        <UInput v-model="state.address" type="text" placeholder="Street address" class="w-full"
                            @input="handleFieldChange('address')" />
                    </UFormField>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="City" name="city">
                            <UInput v-model="state.city" type="text" placeholder="City" class="w-full"
                                @input="handleFieldChange('city')" />
                        </UFormField>

                        <UFormField label="State" name="state">
                            <UInput v-model="state.state" type="text" placeholder="State" class="w-full"
                                @input="handleFieldChange('state')" />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Latitude" name="latitude">
                            <UInput type="text" inputmode="decimal" placeholder="Latitude" class="w-full"
                                :value="state.latitude"
                                @keypress="(e) => { if (!/[0-9.-]/.test(e.key) || (e.key === '.' && state.latitude.includes('.')) || (e.key === '-' && state.latitude !== '')) e.preventDefault(); }"
                                @input="(e) => {
                                    state.latitude = e.target.value.replace(/[^0-9.-]/g, '');
                                    handleFieldChange('latitude');
                                }" />
                        </UFormField>

                        <UFormField label="Longitude" name="longitude">
                            <UInput type="text" inputmode="decimal" placeholder="Longitude" class="w-full"
                                :value="state.longitude"
                                @keypress="(e) => { if (!/[0-9.-]/.test(e.key) || (e.key === '.' && state.longitude.includes('.')) || (e.key === '-' && state.longitude !== '')) e.preventDefault(); }"
                                @input="(e) => {
                                    state.longitude = e.target.value.replace(/[^0-9.-]/g, '');
                                    handleFieldChange('longitude');
                                }" />
                        </UFormField>
                    </div>

                    <div class="flex justify-center mt-4">
                        <UButton label="Get Current Location" type="button" variant="solid" color="secondary" size="xl"
                            class="px-8" :loading="state.locationLoading" @click="getCurrentLocation" />
                    </div>
                </div>

                <div class="flex justify-center mt-4 space-x-4">
                    <UButton type="button" variant="outline" color="neutral" @click="router.back()">
                        Cancel
                    </UButton>
                    <UButton type="submit" variant="solid" color="primary" size="xl" class="px-8"
                        :loading="state.isLoading">
                        Update Event
                    </UButton>
                </div>

                <p v-if="state.error" class="text-red-500 text-sm text-center">{{ state.error }}</p>
            </UForm>
        </UCard>
    </UContainer>
</template>