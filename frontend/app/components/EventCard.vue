<template>
    <div class="event-card">
    <UCard>
    <Placeholder class="h-40 mb-4" /> <!-- Image placeholder -->
    <div class="name-date" style="display:flex">
    <div class="event-name" style="float:left;padding-right: 60px;">
       <NuxtLink :to="event_url" class="event-link">{{ event_name || 'Event Name' }}</NuxtLink>

    </div>
    <div class="event-date-time" style="float:right">{{ event_date || 'Event Date' }}</div></div>
    <div style="padding: 10px 0;">
        {{ event_type || 'Event Type' }}
    </div>

    
    <template #footer>

        <div class="footer" style="display:flex;">
       <UIcon name="mdi-light:map-marker" class="size-5" />
       <div style="padding-left: 10px;font-size: medium ;">{{ event_location || 'Event Location'}}</div></div>
       
    </template>
  </UCard></div>
</template>

<style>
.event-card {
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
}

</style>

<script setup>
const props = defineProps({
  event_name: {
    type: String,
    required: false
  },
  event_date: {
    type: String,
    required: false
  },
    event_location: {
        type: String,
        required: false
    },
    event_url: {
    type: String,
    required: false,
    default: '#'
  },
  event_type:{
    type:String,
    required:false
  }


})
</script>
