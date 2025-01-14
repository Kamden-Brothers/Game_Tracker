<script setup>
    import {onMounted, ref, watch} from 'vue'
    import axios from 'axios';
    import pinochle_input from './games/pinochle_input.vue';
    import spades_input from './games/spades_input.vue';
    import hearts_input from './games/hearts_input.vue';

    const NO_DATA = 'Nothing Selected';
    const serverMessage = ref('');

    const players = ref([]);
    const teams = ref([]);

    const lockTeamsMessage = ref('Lock Teams');
    const teamAndGameLocked = ref(false);

    const pinochleData = ref(null);
    const spadesData = ref(null);
    const heartsData = ref(null);

    const selectedGame = ref('Pinochle');
    const pinochle = ref(true);
    const spades = ref(false);
    const hearts = ref(false);

    function sendServerMessage(msg) {
        serverMessage.value = msg;
    }

    function removeServerMessage() {
        serverMessage.value = ''
    }

    function checkLockReady() {
        let errorMessage;
        if (pinochle.value) {
            console.log('pinochle')
            errorMessage = pinochleData.value.lockReady()
        }
        else if (spades.value) {
            console.log('spades')
            errorMessage = spadesData.value.lockReady()
        }
        else if (hearts.value) {
            console.log('hearts')
            errorMessage = heartsData.value.lockReady()
        }

        // Check if error message was returned
        if (errorMessage) {
            sendServerMessage(errorMessage)
            return false;
        }
        return true;
    }

    function toggleTeamGameLock() {
        if (checkLockReady()) {
            teamAndGameLocked.value = !teamAndGameLocked.value;
            if (teamAndGameLocked.value) {
                lockTeamsMessage.value = 'Unlock Teams';
            }
            else {
                lockTeamsMessage.value = 'Lock Teams';
            }
            removeServerMessage();
        }
    }

    watch(selectedGame, (newVal) => {
        // Update data
        if (newVal === 'Pinochle') {
            pinochle.value = true;
            spades.value = false;
            hearts.value = false;
        }
        else if (newVal === 'Spades') {
            pinochle.value = false;
            spades.value = true;
            hearts.value = false;
        }
        else if (newVal === 'Hearts') {
            pinochle.value = false;
            spades.value = false;
            hearts.value = true;
        }
        removeServerMessage()
    });


    // Load Teams
    const fetchTeams = async () => {
        try {
            const response = await axios.get('/current_teams');
            teams.value = [NO_DATA];
            Object.keys(response.data).forEach(team => {
                teams.value.push(team);
            })

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    // Load players
    const fetchPlayers = async () => {
        try {
            const response = await axios.get('/current_players');
            players.value = [NO_DATA]
            Object.keys(response.data).forEach(player => {
                players.value.push(player)
            })

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    onMounted(() => {
        fetchPlayers();
        fetchTeams();
    })
</script>

<template>
    <div>{{serverMessage}}</div>
    <div>
        <div class="input-div"><b>Select Game</b></div>
        <div class="input-div">
                <select v-model="selectedGame" :disabled="teamAndGameLocked">
                    <option>Pinochle</option>
                    <option>Spades</option>
                    <option>Hearts</option>
                </select>
            <button class="lock-button" @click="toggleTeamGameLock">{{ lockTeamsMessage }}</button>
        </div>
        
        <hr>
        <pinochle_input ref="pinochleData" :teams="teams" :teamAndGameLocked="teamAndGameLocked" v-if="pinochle"/>
        <spades_input ref="spadesData" :teams="teams" :teamAndGameLocked="teamAndGameLocked" v-if="spades"/>
        <hearts_input ref="heartsData" :players="players" :teamAndGameLocked="teamAndGameLocked" v-if="hearts"/>

    </div>
</template>
