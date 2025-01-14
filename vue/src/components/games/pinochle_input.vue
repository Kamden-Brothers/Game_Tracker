<script setup>
    import { ref, watch, defineExpose } from 'vue';
    import axios from 'axios';
    import date_handling from './date_handling.vue';

    let selectedDate;
    let selectedGameOfDay;

    const NO_DATA = 'Nothing Selected';
    const serverResponse = ref('')

    const teamOne = ref(NO_DATA);
    const teamTwo = ref(NO_DATA);
    const matches = ref([]);

    const roundNumbers = ref([]);
    const roundSelected = ref(false);
    const roundData = ref([]);
    const currentMatch = ref('');

    function calculateTotals() {
        let previousTotal_1 = 0;
        let previousTotal_2 = 0;
        roundNumbers.value.forEach(roundNumber => {
            roundNumber.change_1 = roundNumber.meld_1 + roundNumber.tricks_1;
            previousTotal_1 = roundNumber.total_1 = roundNumber.change_1 + previousTotal_1;
            
            roundNumber.change_2 = roundNumber.meld_2 + roundNumber.tricks_2;
            previousTotal_2 = roundNumber.total_2 = roundNumber.change_2 + previousTotal_2;
        })
    }

    const createMatch = async (dateData) => {
        const matchData = {};
        matchData.date = selectedDate = dateData.date;
        matchData.gameOfDay = selectedGameOfDay = dateData.gameOfDay;
        matchData.team1 = teamOne.value;
        matchData.team2 = teamTwo.value;

        try {
            const response = await axios({
                method: 'post',
                url: '/create_pinochle_match',
                data: matchData
            });

            if (response.data.status === 'success') {
                await fetchMatches();
            } else {
                serverResponse.value = response.data.message;
            }

        } catch (error) {
            serverResponse.value = 'Failed to communicate with server';
            console.error('Error fetching data:', error);
        }
    }

    // Load Matches
    const fetchMatch = async () => {
        try {
            const matchData = {'team1': teamOne.value, 'team2': teamTwo.value, 'date': selectedDate, 'gameOfDay': selectedGameOfDay}
            console.log(matchData)
            const response = await axios({
                method: 'post',
                url: 'load_pinochle_match',
                data: matchData
            });
            console.log(response.data)

            if (response.data.status === 'success') {
                roundSelected.value = true;
                console.log(response.data.data);
                roundNumbers.value = response.data.data
                calculateTotals()

            } else {
                serverResponse.value = 'Failed to load match data ' + response.data.message;
            }
        } catch (error) {
            serverResponse.value = 'Failed to communicate with server';
            console.error('Error fetching data', error);
        }
    }

    // Load Matches
    const fetchMatches = async () => {
        try {
            const teamData = {'team1': teamOne.value, 'team2': teamTwo.value}
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
                response.data.data.forEach(match => {
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

    function quickSetup() {
        teamOne.value = 'Kamilya';
        teamTwo.value = 'The Inlaws';
        props.teamAndGameLocked = true;
    }

    function handleDateData(dateData) {
        createMatch(dateData);
    }

    function findMatch() {
        fetchMatch()
    }

    function matchSelected(dateData) {
        currentMatch.value = dateData.dateGameStr;
        selectedDate = dateData.date;
        selectedGameOfDay = dateData.gameOfDay;
    }

    watch(() => props.teamAndGameLocked, () => {
        fetchMatches();
    });

    defineExpose({
        lockReady
    });

</script>

<template>
    <div v-if="serverResponse">{{ serverResponse }}</div>

    <button @click="quickSetup">driver function</button>
    <div>
        <div class="input-div">
            <label>Team One<br><select v-model="teamOne" :disabled="teamAndGameLocked"><option v-for="team in teams" :value="team">{{team}}</option></select></label>
            <label>Team Two<br><select v-model="teamTwo" :disabled="teamAndGameLocked"><option v-for="team in teams" :value="team">{{team}}</option></select></label>
        </div>
    </div>

    <hr>
    <div v-if="teamAndGameLocked"><date_handling :matches="matches" @sendDateData="handleDateData" @sendMatchSelected="matchSelected"/></div>

    <hr>
    <div class="input-div">
        <label>Selected Match<br><input type="text" v-model="currentMatch" disabled></label>
        <button @click="findMatch">Look Up Match</button>
    </div>

    <table class="round-table">
        <tr>
            <td class="input-td">
                Suit
            </td>
            <td class="input-td">
                Top Bidder
            </td>
            <td class="input-td">
                Top Bid
            </td>
            <td class="input-td">
                {{ teamOne }}
            </td>
            <td class="input-td">
                {{ teamTwo }}
            </td>
        </tr>

        <tr v-for="roundNumber in roundNumbers">
            <td class="input-td">
                <select v-model="roundNumber.trump">
                    <option>Select Suit</option>
                    <option value="Clubs">Clubs</option>
                    <option value="Diamonds">Diamonds</option>
                    <option value="Spades">Spades</option>
                    <option value="Hearts">Hearts</option>
                </select>
            </td>
            <td class="input-td">
                <select><option>Top Bidder</option></select>
            </td>
            <td class="input-td"><label class="round-input-label">Top Bid<input v-model="roundNumber.bid" type="number" class="number-input"></label></td>
            <td class="input-td">
                <label class="round-input-label">Meld<input v-model="roundNumber.meld_1" type="number" class="number-input"></label>
                <label class="round-input-label">Tricks<input v-model="roundNumber.tricks_1" type="number" class="number-input"></label>
                <br>
                <label class="round-input-label">Change<input v-model="roundNumber.change_1" type="number" class="number-input" disabled></label>
                <label class="round-input-label">Total<input v-model="roundNumber.total_1" type="number" class="number-input" disabled></label>

            </td>
            <td class="input-td">
                <label class="round-input-label">Meld<input v-model="roundNumber.meld_2" type="number" class="number-input"></label>
                <label class="round-input-label">Tricks<input v-model="roundNumber.tricks_2" type="number" class="number-input"></label>
                <br>
                <label class="round-input-label">Change<input v-model="roundNumber.change_2" type="number" class="number-input" disabled></label>
                <label class="round-input-label">Total<input v-model="roundNumber.total_2" type="number" class="number-input" disabled></label>
            </td>
        </tr>
    </table>

</template>

<style scoped>
    .round-table {
        padding: 10px;
    }

    .input-td {
        border: solid;
        border-collapse: collapse;
        padding: 5px;
    }

    .number-input {
        margin: 5px;
        width: 6ch;
    }


    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
</style>