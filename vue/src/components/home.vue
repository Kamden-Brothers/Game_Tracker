<script setup>
    import { ref, computed, onMounted } from 'vue'
    import axios from 'axios'

    const count = ref(0)
    const userInput = ref('Nothing entered')

    const serverData = ref('Test')

    function increment() {
        count.value += 1
    }

    function onInput(e) {
        userInput.value = e.target.value
    }

    const diplayText = computed(() => {
        return userInput.value != '' ? userInput.value : 'Nothing entered'
    })

    // Fetching function
    const fetchData = async () => {
        try {
            const response = await axios.get('http://localhost:5000/current_players'); // Example endpoint
            serverData.value = response.data; // Storing the fetched data
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    // Lifecycle hook to fetch data on mount
    onMounted(() => {
        fetchData();
    });

</script>

<template>
    <button @click="increment">
        {{ count }}
    </button>
    <div>{{diplayText}}</div>
    <input @input="onInput" type="text"/>
    <div>{{serverData}}</div>
</template>
