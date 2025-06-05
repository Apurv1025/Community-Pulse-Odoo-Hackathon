<template>
  <NuxtLink :to="issueUrl" class="block">
    <UCard class="issue-card">
      <!-- Top Image -->
      <img v-if="issueImg && issueImg !== ''" :src="issueImg" :alt="issueCategory" class="w-full h-48 object-cover rounded-t-md mb-4">
      <div v-else class="w-full h-48 bg-gray-200 rounded-t-md mb-4 flex items-center justify-center">
        <UIcon name="i-lucide-alert-triangle" class="w-10 h-10 text-gray-400" />
      </div>

      <!-- Issue Category as Title -->
      <div class="flex justify-between items-center mb-2">
        <h3 class="text-lg font-semibold">
          {{ issueCategory }}
        </h3>
        <UBadge :color="getStatusColor(issueStatus)">{{ formatStatus(issueStatus) }}</UBadge>
      </div>

      <!-- Issue Details -->
      <div class="text-sm text-gray-500 mb-3">
        <div class="flex items-center gap-1 mb-1">
          <UIcon name="i-lucide-user" class="w-4 h-4" />
          <span>{{ issueReporter }}</span>
        </div>
        <div class="flex items-center gap-1 mb-1">
          <UIcon name="i-lucide-map-pin" class="w-4 h-4" />
          <span>{{ issueLocation }}</span>
        </div>
        <div class="flex items-center gap-1">
          <UIcon name="i-lucide-thumbs-up" class="w-4 h-4" />
          <span>{{ upvotes }} upvotes</span>
        </div>
      </div>

      <!-- Issue Description (if provided) -->
      <p v-if="issueDescription" class="text-gray-700 mb-4 line-clamp-3">{{ issueDescription }}</p>
    </UCard>
  </NuxtLink>
</template>

<style scoped>
.issue-card {
  width: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.issue-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>

<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps({
  issueCategory: {
    type: String,
    default: 'Issue Category'
  },
  issueDate: {
    type: String,
    default: 'Report Date'
  },
  issueLocation: {
    type: String,
    default: 'Issue Location'
  },
  issueImg: {
    type: String,
    default: ''
  },
  issueUrl: {
    type: String,
    default: '#'
  },
  issueReporter: {
    type: String,
    default: 'Anonymous'
  },
  issueDescription: {
    type: String,
    default: ''
  },
  issueStatus: {
    type: String,
    default: 'open'
  },
  id: {
    type: [Number, String], 
    default: null
  }
});

const config = useRuntimeConfig();
const upvotes = ref(0);

const issueImg = ref(props.issueImg || '');

// Fetch issue data and upvotes count when component mounts
onMounted(async () => {
  if (props.id) {
    try {
      // Fetch upvotes
      const upvotesResponse = await fetch(`${config.public.backendUrl}/issues/${props.id}/upvotes`);
      if (upvotesResponse.ok) {
        upvotes.value = await upvotesResponse.json();
      }
      
      // Fetch complete issue data to get images
      const issueResponse = await fetch(`${config.public.backendUrl}/issue/${props.id}`);
      if (issueResponse.ok) {
        const issueData = await issueResponse.json();
        console.log(`Issue ${props.id} data:`, issueData);
        
        // Set image URL if images are available
        if (issueData.images && Array.isArray(issueData.images) && issueData.images.length > 0) {
          issueImg.value = `${config.public.backendUrl}/uploads/${issueData.images[0]}`;
          console.log(`Issue ${props.id} image URL set to: ${issueImg.value}`);
        }
      }
    } catch (error) {
      console.error('Failed to fetch issue data:', error);
    }
  }
});

// Format issue status
const formatStatus = (status) => {
  if (!status) return 'Unknown';
  
  switch (status.toLowerCase()) {
    case 'open':
      return 'Open';
    case 'in_progress':
      return 'In Progress';
    case 'resolved':
      return 'Resolved';
    case 'closed':
      return 'Closed';
    default:
      return status.charAt(0).toUpperCase() + status.slice(1);
  }
};

// Get color based on status
const getStatusColor = (status) => {
  if (!status) return 'gray';
  
  switch (status.toLowerCase()) {
    case 'open':
      return 'amber';
    case 'in_progress':
      return 'blue';
    case 'resolved':
      return 'green';
    case 'closed':
      return 'gray';
    default:
      return 'gray';
  }
};
</script>