<script setup>
    import { ref, watch, defineExpose } from 'vue';

    const NO_DATA = 'Nothing Selected';

    const teamOne = ref(NO_DATA);
    const teamTwo = ref(NO_DATA);

    const matches = ref([])

    // Load Matches
    const fetchMatches = async () => {
        try {
            const teamData = {'team_1': teamOne.value, 'team_2': teamTwo.value}
            console.log(teamData)
            const response = await axios({
                method: 'post',
                url: 'pinochle_matches',
                data: teamData
            });
            console.log(response.data)

            if (response.data.status === 'success') {
                console.log(response.data.data);
                matches.value = [NO_DATA]
                Object.keys(response.data.data).forEach(match => {
                    matches.value.push(match)
                })

            } else {
                serverResponse.value = 'Failed to load match data ' + response.data.message;
            }
        } catch (error) {
            serverResponse.value = 'Failed to communicate with server';
            console.error('Error fetching data', error);
        }
    }

    const lockReady = () => {
        let errorMessage = '';
        if (teamOne.value === NO_DATA || teamOne.value === '') {
            errorMessage += 'Team one cannot be blank.';
        }
        if (teamTwo.value === NO_DATA || teamTwo.value === '') {
            errorMessage += ' Team two cannot be blank.';
        }
        if (!errorMessage && teamOne.value === teamTwo.value) {
            errorMessage = 'Teams must be unique'
        }
        
        return errorMessage.trim();
    }

    const props = defineProps({
        teams: {
            type: Array,
            required: true
        },
        teamAndGameLocked: {
            type: Boolean,
            required: true
        }
    });
    
    watch(() => props.teamAndGameLocked, () => {
        fetchMatches();
    });

    defineExpose({
        lockReady
    });

</script>

<template>
    <div>
        <div class="input-div">
            <label>Team One<br><select v-model="teamOne" :disabled="teamAndGameLocked"><option v-for="team in teams" :value="team">{{team}}</option></select></label>
            <label>Team Two<br><select v-model="teamTwo" :disabled="teamAndGameLocked"><option v-for="team in teams" :value="team">{{team}}</option></select></label>
        </div>
    </div>
</template>