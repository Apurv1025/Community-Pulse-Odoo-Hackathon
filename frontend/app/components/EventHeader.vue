<template>
  <div class="image-header" >
        <!-- <h1 class="header-title">{{ event_id }}</h1> -->
        <slot></slot>
      </div>
</template>

<script setup>
const props = defineProps({
event_id:{
    type:String
}})

</script>

<style scoped>
.image-header{
    
}
</style>
