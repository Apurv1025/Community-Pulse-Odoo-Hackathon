<script setup>
import { useAuthStore } from "../../../../stores/authStore";

const store = useAuthStore();
const router = useRouter();
const config = useRuntimeConfig();
const toast = useToast();
const route = useRoute();

// Get the issue ID from the route
const issueId = computed(() => route.params.id);

// State to track form data and loading state
const state = reactive({
    category: '',
    description: '',
    latitude: '',
    longitude: '',
    personal: '',
    isAnonymous: false,
    status: '',
    error: '',
    isLoading: false,
    fetchLoading: true,
    locationLoading: false
});

// Default categories list
const categories = ref([
    'Infrastructure',
    'Sanitation',
    'Public Safety',
    'Environment',
    'Noise Pollution',
    'Public Services',
    'Traffic',
    'Other'
]);

// Track which fields have been modified
const modifiedFields = reactive({
    category: false,
    description: false,
    latitude: false,
    longitude: false,
    status: false
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

// Fetch the current issue data
const fetchIssue = async () => {
    state.fetchLoading = true;
    try {
        const response = await fetch(`${config.public.backendUrl}/issue/${issueId.value}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${store.session}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch issue details');
        }

        const issueData = await response.json();
        console.log("API Response:", issueData);

        // Check if the issue was submitted anonymously (personal field is empty)
        const isAnonymous = !issueData.personal;

        // Populate form with existing data
        state.category = issueData.category || '';
        state.description = issueData.description || '';
        state.latitude = issueData.latitude?.toString() || '';
        state.longitude = issueData.longitude?.toString() || '';
        state.personal = issueData.personal || '';
        state.isAnonymous = isAnonymous;
        state.status = issueData.status || 'open';

        // Check if current user is authorized to edit the issue
        if (issueData.personal && issueData.personal !== store.user?.username) {
            // If personal doesn't match current username, show error and redirect back
            toast.add({
                title: 'Unauthorized',
                description: 'You are not authorized to edit this issue.',
                color: 'error'
            });
            // Short delay before redirecting
            setTimeout(() => router.back(), 1500);
            return;
        }

        // If issue was submitted anonymously, show warning
        if (isAnonymous) {
            toast.add({
                title: 'Anonymous Issue',
                description: 'This issue was submitted anonymously. Only admins can edit anonymous issues.',
                color: 'warning'
            });
        }

    } catch (error) {
        console.error('Error fetching issue:', error);
        toast.add({
            title: 'Error',
            description: error.message || 'Failed to load issue data',
            color: 'error'
        });
    } finally {
        state.fetchLoading = false;
    }
};

// Call fetch on mount
onMounted(fetchIssue);

// Field change handler to track modifications
const handleFieldChange = (field) => {
    modifiedFields[field] = true;
};

// Available status options
const statusOptions = ref([
    { value: 'open', label: 'Open' },
    { value: 'in-progress', label: 'In Progress' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'closed', label: 'Closed' }
]);

// Update issue handler
const updateIssue = async () => {
    state.isLoading = true;
    state.error = '';

    try {
        // Create update object with only modified fields
        const updateData = {};
        Object.keys(modifiedFields).forEach(field => {
            if (modifiedFields[field]) {
                if (field === 'latitude' || field === 'longitude') {
                    updateData[field] = state[field] ? parseFloat(state[field]) : null;
                } else {
                    updateData[field] = state[field];
                }
            }
        });

        // Only proceed if there are changes
        if (Object.keys(updateData).length === 0) {
            toast.add({
                title: 'No Changes',
                description: 'No changes were made to the issue',
                color: 'info'
            });
            state.isLoading = false;
            return;
        }

        console.log('Updating issue with data:', updateData);

        // Make API call to update the issue
        const response = await fetch(`${config.public.backendUrl}/issues/edit/${issueId.value}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${store.session}`
            },
            body: JSON.stringify(updateData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update issue');
        }

        const updatedIssue = await response.json();
        console.log('Issue updated:', updatedIssue);

        toast.add({
            title: 'Success',
            description: 'Issue updated successfully',
            color: 'success'
        });

        // Navigate back to issue details
        router.push(`/issue/${issueId.value}`);
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to update issue. Please try again.';
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
                    <h2 class="text-xl font-semibold">Update Issue</h2>
                    <p class="text-sm text-gray-500">Edit the details of your reported issue</p>
                </div>
            </template>

            <div v-if="state.fetchLoading" class="flex justify-center py-8">
                <UButton loading variant="ghost" />
            </div>

            <UForm v-else :state="state" class="flex flex-col gap-6" @submit.prevent="updateIssue">
                <!-- Issue Details -->
                <div class="space-y-4">
                    <h3 class="font-medium">Issue Details</h3>
                    <UFormField label="Category" name="category">
                        <USelect 
                            v-model="state.category" 
                            :items="categories" 
                            placeholder="Select issue category"
                            class="w-full" 
                            @input="handleFieldChange('category')" />
                    </UFormField>

                    <UFormField label="Description" name="description">
                        <UTextarea 
                            v-model="state.description" 
                            placeholder="Describe the issue in detail..." 
                            :rows="4"
                            class="w-full" 
                            @input="handleFieldChange('description')" />
                    </UFormField>

                    <UFormField label="Status" name="status">
                        <USelect 
                            v-model="state.status" 
                            :items="statusOptions" 
                            placeholder="Select issue status"
                            class="w-full" 
                            @update:model-value="handleFieldChange('status')" />
                    </UFormField>

                    <!-- Anonymous submission notice (readonly) -->
                    <div v-if="state.isAnonymous" class="bg-amber-50 p-3 rounded border border-amber-200 text-amber-700">
                        <p class="flex items-center">
                            <UIcon name="i-lucide-info" class="mr-2" />
                            <span>This issue was submitted anonymously</span>
                        </p>
                    </div>
                </div>

                <!-- Issue Location -->
                <div class="space-y-4">
                    <h3 class="font-medium">Issue Location</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Latitude" name="latitude">
                            <UInput 
                                type="text" 
                                inputmode="decimal" 
                                placeholder="Latitude" 
                                class="w-full"
                                :value="state.latitude"
                                @keypress="(e) => { 
                                    if (!/[0-9.-]/.test(e.key) || 
                                        (e.key === '.' && state.latitude.includes('.')) || 
                                        (e.key === '-' && state.latitude !== '')) 
                                            e.preventDefault(); 
                                }"
                                @input="(e) => {
                                    state.latitude = e.target.value.replace(/[^0-9.-]/g, '');
                                    handleFieldChange('latitude');
                                }" />
                        </UFormField>

                        <UFormField label="Longitude" name="longitude">
                            <UInput 
                                type="text" 
                                inputmode="decimal" 
                                placeholder="Longitude" 
                                class="w-full"
                                :value="state.longitude"
                                @keypress="(e) => { 
                                    if (!/[0-9.-]/.test(e.key) || 
                                        (e.key === '.' && state.longitude.includes('.')) || 
                                        (e.key === '-' && state.longitude !== '')) 
                                            e.preventDefault(); 
                                }"
                                @input="(e) => {
                                    state.longitude = e.target.value.replace(/[^0-9.-]/g, '');
                                    handleFieldChange('longitude');
                                }" />
                        </UFormField>
                    </div>

                    <div class="flex justify-center mt-4">
                        <UButton 
                            label="Get Current Location" 
                            type="button" 
                            variant="solid" 
                            color="secondary" 
                            size="xl"
                            class="px-8" 
                            :loading="state.locationLoading" 
                            @click="getCurrentLocation" />
                    </div>
                </div>

                <div class="flex justify-center mt-4 space-x-4">
                    <UButton 
                        type="button" 
                        variant="outline" 
                        color="neutral" 
                        @click="router.back()">
                        Cancel
                    </UButton>
                    <UButton 
                        type="submit" 
                        variant="solid" 
                        color="primary" 
                        size="xl" 
                        class="px-8"
                        :loading="state.isLoading">
                        Update Issue
                    </UButton>
                </div>

                <p v-if="state.error" class="text-red-500 text-sm text-center">{{ state.error }}</p>
            </UForm>
        </UCard>
    </UContainer>
</template>