<template>
  <UContainer class="py-8">
    <UCard class="w-full max-w-6xl mx-auto">
      <template #header>
        <div class="flex flex-col gap-1">
          <h2 class="text-xl font-semibold">Community Pulse</h2>
          <p class="text-sm text-gray-500">Discover what's happening around your location</p>

          <!-- Location Permission Request -->
          <div v-if="!locationGranted && !locationDenied" class="mt-4 bg-blue-50 border border-blue-200 rounded p-4">
            <div class="flex items-center mb-2">
              <UIcon name="i-lucide-map-pin" class="text-blue-500 mr-2" />
              <p class="text-blue-700 font-medium">Enable location services</p>
            </div>
            <p class="text-sm text-blue-600 mb-3">Allow location access to see events and issues happening near you.</p>
            <UButton color="blue" variant="solid" size="sm" @click="requestLocation" :loading="locationLoading">
              Share My Location
            </UButton>
          </div>

          <!-- Location Denied Message -->
          <div v-if="locationDenied" class="mt-4 bg-amber-50 border border-amber-200 rounded p-4">
            <div class="flex items-center mb-2">
              <UIcon name="i-lucide-alert-triangle" class="text-amber-500 mr-2" />
              <p class="text-amber-700 font-medium">Location access denied</p>
            </div>
            <p class="text-sm text-amber-600 mb-3">You'll see general listings instead of nearby items.</p>
            <UButton color="amber" variant="outline" size="sm" @click="requestLocation">
              Try Again
            </UButton>
          </div>
        </div>
      </template>

      <!-- Events/Issues Tabs -->
      <UTabs :items="tabItems" variant="pill" class="gap-4 w-full" :ui="{ trigger: 'grow' }">
        <!-- Events Tab -->
        <template #events="{ item }">
          <p class="text-muted mb-4">
            {{ item.description }}
          </p>

          <div v-if="eventsLoading" class="flex justify-center py-8">
            <UButton loading variant="ghost" />
          </div>

          <div v-else-if="eventsError" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {{ eventsError }}
          </div>

          <div v-else-if="events.length === 0" class="text-center py-10">
            <p class="text-gray-500 text-xl">No events found nearby</p>
            <p class="text-gray-400 text-sm mt-2">Try searching in a different area or browse all events</p>
            <UButton class="mt-4" to="/events" variant="outline">Browse All Events</UButton>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
            <EventCard v-for="event in events" :id="event.id" :key="event.id" :event-name="event.event_name"
              :event-date="formatDate(event.start_date)" :event-location="`${event.city || ''}, ${event.state || ''}`"
              :event-url="`/event/${event.id}`" :event-type="event.category"
              :event-description="event.event_description" />
          </div>
        </template>

        <!-- Issues Tab -->
        <template #issues="{ item }">
          <p class="text-muted mb-4">
            {{ item.description }}
          </p>

          <div v-if="issuesLoading" class="flex justify-center py-8">
            <UButton loading variant="ghost" />
          </div>

          <div v-else-if="issuesError" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {{ issuesError }}
          </div>

          <div v-else-if="issues.length === 0" class="text-center py-10">
            <p class="text-gray-500 text-xl">No issues reported nearby</p>
            <p class="text-gray-400 text-sm mt-2">Try searching in a different area or browse all issues</p>
            <UButton class="mt-4" to="/issues" variant="outline">Browse All Issues</UButton>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
            <IssueCard v-for="issue in issues" :id="issue.id" :key="issue.id" :issue-category="issue.category"
              :issue-location="formatLocation(issue.latitude, issue.longitude)" :issue-url="`/issue/${issue.id}`"
              :issue-reporter="issue.personal || 'Anonymous'" :issue-description="issue.description"
              :issue-status="issue.status" />
          </div>
        </template>
      </UTabs>
    </UCard>
  </UContainer>
</template>

<script setup>
import { useAuthStore } from "../../stores/authStore";
import EventCard from "../components/EventCard.vue";
import IssueCard from "../components/IssueCard.vue";

const store = useAuthStore();
const config = useRuntimeConfig();
const toast = useToast();

// Tab items for Events and Issues
const tabItems = [
  {
    label: 'Events',
    description: 'Discover upcoming events in your community',
    icon: 'i-lucide-calendar',
    slot: 'events'
  },
  {
    label: 'Issues',
    description: 'View reported community issues near you',
    icon: 'i-lucide-alert-triangle',
    slot: 'issues'
  }
];

// State management
const events = ref([]);
const issues = ref([]);
const eventsLoading = ref(true);
const issuesLoading = ref(true);
const eventsError = ref(null);
const issuesError = ref(null);
const locationLoading = ref(false);
const locationGranted = ref(false);
const locationDenied = ref(false);
const userCoords = ref({ latitude: null, longitude: null });

// Request location from user
const requestLocation = async () => {
  locationLoading.value = true;

  if (!navigator.geolocation) {
    toast.add({
      title: 'Error',
      description: 'Your browser does not support geolocation',
      color: 'error'
    });
    locationDenied.value = true;
    locationLoading.value = false;
    return;
  }

  try {
    const position = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      });
    });

    userCoords.value = {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude
    };

    locationGranted.value = true;
    locationDenied.value = false;

    // Fetch nearby data
    await Promise.all([
      fetchNearbyEvents(),
      fetchNearbyIssues()
    ]);

    toast.add({
      title: 'Success',
      description: 'Showing items near your location',
      color: 'success'
    });
  } catch (error) {
    console.error('Error getting location:', error);
    locationDenied.value = true;

    toast.add({
      title: 'Location Error',
      description: 'Could not access your location. Showing general listings instead.',
      color: 'warning'
    });

    // Fall back to fetching all events/issues
    await Promise.all([
      fetchEvents(),
      fetchIssues()
    ]);
  } finally {
    locationLoading.value = false;
  }
};

// Load events and issues when the component is mounted
onMounted(async () => {
  // Start with requesting location
  await requestLocation();
});

// Fetch nearby events based on user location
const fetchNearbyEvents = async () => {
  if (!userCoords.value.latitude || !userCoords.value.longitude) {
    return fetchEvents(); // Fall back to all events
  }

  eventsLoading.value = true;
  eventsError.value = null;

  try {
    const response = await fetch(
      `${config.public.backendUrl}/events/nearby?latitude=${userCoords.value.latitude}&longitude=${userCoords.value.longitude}`,
      {
        headers: {
          'Authorization': `Bearer ${store.session}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch nearby events: ${response.status}`);
    }

    const data = await response.json();
    console.log('Fetched nearby events:', data);

    // Process events to include proper image URLs
    events.value = data.map(event => {
      let imageUrl = '';
      if (event.images && Array.isArray(event.images) && event.images.length > 0) {
        imageUrl = `${config.public.backendUrl}/uploads/${event.images[0]}`;
      }
      console.log(`Event ${event.id} image URL: ${imageUrl}`);

      return {
        ...event,
        image_url: imageUrl
      };
    });
  } catch (err) {
    console.error('Error fetching nearby events:', err);
    eventsError.value = 'Failed to load nearby events. Please try again later.';
    toast.add({
      title: 'Error',
      description: eventsError.value,
      color: 'error'
    });
  } finally {
    eventsLoading.value = false;
  }
};

// Fetch nearby issues based on user location
const fetchNearbyIssues = async () => {
  if (!userCoords.value.latitude || !userCoords.value.longitude) {
    return fetchIssues(); // Fall back to all issues
  }

  issuesLoading.value = true;
  issuesError.value = null;

  try {
    const response = await fetch(
      `${config.public.backendUrl}/issues/nearby?latitude=${userCoords.value.latitude}&longitude=${userCoords.value.longitude}`,
      {
        headers: {
          'Authorization': `Bearer ${store.session}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch nearby issues: ${response.status}`);
    }

    const data = await response.json();
    console.log('Fetched nearby issues:', data);

    // Process issues to include proper image URLs
    issues.value = data.map(issue => {
      let imageUrl = '';
      if (issue.images && Array.isArray(issue.images) && issue.images.length > 0) {
        imageUrl = `${config.public.backendUrl}/uploads/${issue.images[0]}`;
      }
      console.log(`Issue ${issue.id} image URL: ${imageUrl}`);

      return {
        ...issue,
        image_url: imageUrl
      };
    });
  } catch (err) {
    console.error('Error fetching nearby issues:', err);
    issuesError.value = 'Failed to load nearby issues. Please try again later.';
    toast.add({
      title: 'Error',
      description: issuesError.value,
      color: 'error'
    });
  } finally {
    issuesLoading.value = false;
  }
};

// Fetch all events from the backend (fallback)
const fetchEvents = async () => {
  eventsLoading.value = true;
  eventsError.value = null;

  try {
    const response = await fetch(`${config.public.backendUrl}/events/`, {
      headers: {
        'Authorization': `Bearer ${store.session}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch events: ${response.status}`);
    }

    const data = await response.json();
    console.log('Fetched all events:', data);

    // Process events to include proper image URLs
    events.value = data.map(event => {
      let imageUrl = '';
      if (event.images && Array.isArray(event.images) && event.images.length > 0) {
        imageUrl = `${config.public.backendUrl}/uploads/${event.images[0]}`;
      }

      return {
        ...event,
        image_url: imageUrl
      };
    });
  } catch (err) {
    console.error('Error fetching events:', err);
    eventsError.value = 'Failed to load events. Please try again later.';
    toast.add({
      title: 'Error',
      description: eventsError.value,
      color: 'error'
    });
  } finally {
    eventsLoading.value = false;
  }
};

// Fetch all issues from the backend (fallback)
const fetchIssues = async () => {
  issuesLoading.value = true;
  issuesError.value = null;

  try {
    const response = await fetch(`${config.public.backendUrl}/issues/`, {
      headers: {
        'Authorization': `Bearer ${store.session}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch issues: ${response.status}`);
    }

    const data = await response.json();
    console.log('Fetched all issues:', data);

    // Process issues to include proper image URLs
    issues.value = data.map(issue => {
      let imageUrl = '';
      if (issue.images && Array.isArray(issue.images) && issue.images.length > 0) {
        imageUrl = `${config.public.backendUrl}/uploads/${issue.images[0]}`;
      }

      return {
        ...issue,
        image_url: imageUrl
      };
    });
  } catch (err) {
    console.error('Error fetching issues:', err);
    issuesError.value = 'Failed to load issues. Please try again later.';
    toast.add({
      title: 'Error',
      description: issuesError.value,
      color: 'error'
    });
  } finally {
    issuesLoading.value = false;
  }
};

// Format date for display
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Format location coordinates for display
const formatLocation = (lat, lng) => {
  if (!lat || !lng) return 'Location unavailable';
  return `${parseFloat(lat).toFixed(4)}, ${parseFloat(lng).toFixed(4)}`;
};
</script>
