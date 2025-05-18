<template>
  this is ghomepage

  <div class="events">
    <EventCard 
      v-for="event in events" 
      :key="event.id"
      :event_name="event.name"
      :event_date="event.date"
      :event_location="event.location"
      :event_url="event.url"
    />
  </div>
</template>

<script setup>
// Define an array of events with all required properties
const events = [
  {
    id: 1,
    name: 'Summer Music Festival',
    date: 'June 15, 2025',
    location: 'Central Park',
    url: '/event/summer-music-festival'
  },
  {
    id: 2,
    name: 'Tech Conference 2025',
    date: 'July 23, 2025',
    location: 'Convention Center',
    url: '/event/tech-conference'
  },
  {
    id: 3,
    name: 'Food & Wine Expo',
    date: 'August 10, 2025',
    location: 'City Square',
    url: '/event/food-wine-expo'
  }
]

// If you need to fetch events from an API:
// const { data: events } = await useFetch('/api/events')

// Or if you want to use computed properties:
// const featuredEvents = computed(() => {
//   return events.filter(event => event.isFeatured)
// })
</script>

<style>
.events {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}
</style>
