<script setup>
    import { ref, watch, defineExpose, onMounted } from 'vue';
    import axios from 'axios';
    import date_handling from './date_handling.vue';

    let selectedDate;
    let selectedGameOfDay;
    let teamOneData = {};
    let teamTwoData = {};

    const NO_DATA = 'Nothing Selected';
    const serverResponse = ref('');
    const popupResponse = ref('');
    const teamSwapMessage = ref(false);
    const inputErrorMessage = ref('');

    const teamOne = ref(NO_DATA);
    const teamTwo = ref(NO_DATA);
    const matches = ref([]);

    const rounds = ref([]);
    const roundSelected = ref(false);
    const currentMatch = ref('');
    const lockedPlayers = ref([]);
    const gameOver = ref(false);

    function checkMeld(round, team_number, error) {
        // Check if bid is an acceptable value
        const meld = round[`meld_${team_number}`];
        
        if (!Number.isInteger(meld)) {
            round[`meldError_${team_number}`] = 'invalid-input';
            error.push('Meld must be a whole number');
        }

        if (meld !== 0 && meld < 20) {
            round[`meldError_${team_number}`] = 'invalid-input';
            error.push('Meld must be 0 or at least 20');
        }
    }

    function checkTricks(round, teamBidNumber, error) {
        // Check tricks are acceptable values
        const totalTricks = round.tricks_1 + round.tricks_2;

        if (totalTricks !== 0 && totalTricks !== 50) {
            round.trickError_1 = round.trickError_2 = 'invalid-input';
            error.push('Tricks must add up to 50');
        }

        if (totalTricks === 0 && round[`meld_${teamBidNumber}`] !== 0) {
            round[`trickError_${teamBidNumber}`] = round[`meldError_${teamBidNumber}`] = 'invalid-input';
            error.push('Bidding teams meld must be zero if tricks are zero');
        }

        if (!Number.isInteger(round.tricks_1) || !Number.isInteger(round.tricks_2)) {
            round.trickError_1 = round.trickError_2 = 'invalid-input';
            error.push('Tricks must be a whole number');
        }

        if (round.tricks_1 < 0 ) {
            round.trickError_1 = round.trickError_2 = 'invalid-input';
            error.push('Tricks must be from 0 to 50');
        }

        if (round.tricks_2 < 0 ) {
            round.trickError_1 = round.trickError_2 = 'invalid-input';
            error.push('Tricks must be from 0 to 50');
        }
    }

    function checkBid(round, error) {
        if (!Number.isInteger(round.bid)) {
            round.bidError = 'invalid-input';
            error.push('Bid must be a whole number');
        }
        if (round.bid < 50) {
            round.bidError = 'invalid-input';
            error.push('Bid must be at least 50');
        }
        if (round.bid > 60 && round.bid % 5 !== 0) {
            round.bidError = 'invalid-input';
            error.push('Bids above 60 must be divisible by 5');
        }
    }

    function getTeamBid(round) {
        if (round.top_bidder === teamOneData.player_1 || round.top_bidder === teamOneData.player_2) {
            return ['1', '2'];
        }
        if (round.top_bidder === teamTwoData.player_1 || round.top_bidder === teamTwoData.player_2) {
            return ['2', '1'];
        }
        return ['0', '0'];
    }

    function calcChange(round, teamNumber, tookBid) {
        if (tookBid) {
            if (round[`tricks_${teamNumber}`] < 20 || (round[`meld_${teamNumber}`] + round[`tricks_${teamNumber}`] < round.bid)) {
                round[`change_${teamNumber}`] = -1 * round.bid;
                return -1 * round.bid;
            }

        }
        else {
            if (round[`tricks_${teamNumber}`] < 20 && round.tricks_1 + round.tricks_2) {
                round[`change_${teamNumber}`] = 0;
                return 0;
            }
        }
        round[`change_${teamNumber}`] = round[`meld_${teamNumber}`] + round[`tricks_${teamNumber}`];
        return round[`change_${teamNumber}`];
    }

    function resetErrors() {
        inputErrorMessage.value = '';
        rounds.value.forEach(round => {
            round.meldError_1 = round.meldError_2 = round.trickError_1 = round.trickError_2 = round.bidError = '';
            round.bidderError = round.suitError = round.winner_1 = round.winner_2 = round.roundAfterWinner = '';
        })
    }

    function calculateTotals() {
        let error = [];
        let previousTotal_1 = 0;
        let previousTotal_2 = 0;
        gameOver.value = false;
        resetErrors();

        rounds.value.forEach(round => {
            if (gameOver.value) {
                error.push('Round after winner was declared');
                round.roundAfterWinner = 'invalid-row';
                return;
            }
            let [teamBidNumber, nonTeamBidNumber] = getTeamBid(round);
            if (teamBidNumber === '0') {
                error.push('Failed to find top bidder');
            }

            checkMeld(round, '1', error);
            checkMeld(round, '2', error);

            checkTricks(round, teamBidNumber, error);
            checkBid(round, error);

            if (round.top_bidder === 'Top Bidder') {
                round.bidderError = 'invalid-input';
                error.push('Bidder must be set');
            }
            if (round.trump === 'Select Suit') {
                round.suitError = 'invalid-input';
                error.push('Suit must be selected');
            }

            if (error.length === 0) {
                round.change_1 = calcChange(round, '1', teamBidNumber === '1')
                previousTotal_1 = round.total_1 = round.change_1 + previousTotal_1;

                round.change_2 = calcChange(round, '2', teamBidNumber === '2')
                previousTotal_2 = round.total_2 = round.change_2 + previousTotal_2;

                if (round[`change_${teamBidNumber}`] > 0 && round[`total_${teamBidNumber}`] > round[`total_${nonTeamBidNumber}`]) {
                    if (round[`total_${teamBidNumber}`] >= 500) {
                        round[`winner_${teamBidNumber}`] = 'winning-score';
                        gameOver.value = true;
                    }
                }
            }
            
        })
        if (error.length !== 0) {
            inputErrorMessage.value = error.join(', ')
            return false;
        }
        return true;
    }

    function addEmptyRow() {
        rounds.value.push({
            'round_number': rounds.value.length + 1,
            'bid': 0,
            'change_1': 0,
            'change_2': 0,
            'meld_1': 0,
            'meld_2': 0,
            'total_1': 0,
            'total_2': 0,
            'tricks_1': 0,
            'tricks_2': 0,
            'trump': 'Select Suit',
            'top_bidder': 'Top Bidder',
            'meldError_1': '',
            'meldError_2': '',
            'trickError_1': '',
            'trickError_2': '',
            'bidError': '',
            'bidderError': '',
            'suitError': '',
            'winner_1': '',
            'winner_2': '',
            'roundAfterWinner': ''
        })
    }

    function removeRow() {
        if (rounds.value.length !== 0) {
            rounds.value.pop()
        }
        resetErrors()
    }

    function validateAndAddEmptyRow() {
        calculateTotals()
        addEmptyRow();
    }

    async function submitGames() {
        const gameData = {
            'rounds': [],
            'team1': teamOne.value,
            'team2': teamTwo.value,
            'date': selectedDate,
            'gameOfDay': selectedGameOfDay
        }

        if (calculateTotals()) {
            rounds.value.forEach((round => {
                gameData.rounds.push(
                    {
                        'bid': round.bid,
                        'change_1': round.change_1,
                        'change_2': round.change_2,
                        'meld_1': round.meld_1,
                        'meld_2': round.meld_2,
                        'total_1': round.total_1,
                        'total_2': round.total_2,
                        'tricks_1': round.tricks_1,
                        'tricks_2': round.tricks_2,
                        'trump': round.trump,
                        'top_bidder': round.top_bidder,
                    }
                )
            }))

            try {
                const response = await axios({
                    method: 'post',
                    url: '/submit_pinochle_game',
                    data: gameData
                })
                
                if (response.data.status === 'success') {
                    popupResponse.value = 'Data successfuly submitted'
                } else {
                    popupResponse.value = 'Failed to load match data ' + response.data.message;
                }

            } catch (error) {
                popupResponse.value = 'Failed to communicate with server';
                console.error('Error fetching data:', error);
            }
        }
        console.log(rounds.value[0])
    }

    async function createMatch(dateData) {
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

    async function deleteMatch(dateData) {
        const matchData = {'team1': teamOne.value, 'team2': teamTwo.value, 'date': dateData.date, 'gameOfDay': dateData.gameOfDay}
        try {
            const response = await axios({
                method: 'post',
                url: 'delete_pinochle_match',
                data: matchData
            })
            if (response.data.status === 'success') {
                await fetchMatches();
            } else {
                serverResponse.value = response.data.message;
            }

        } catch (error) {
            serverResponse.value = 'Failed to delete match'
            console.error('Error fetching data', error);
        }
    }

    // Load Matches
    async function fetchMatch() {
        popupResponse.value = '';
        try {
            const matchData = {'team1': teamOne.value, 'team2': teamTwo.value, 'date': selectedDate, 'gameOfDay': selectedGameOfDay}
            const response = await axios({
                method: 'post',
                url: 'load_pinochle_match',
                data: matchData
            });

            if (response.data.status === 'success') {
                roundSelected.value = true;
                console.log(response.data.data);
                rounds.value = response.data.data.rounds;
                
                calculateTotals();
                if (rounds.value.length === 0) {
                    addEmptyRow();
                }
                console.log(rounds.value)

            } else {
                serverResponse.value = 'Failed to load match data ' + response.data.message;
            }
        } catch (error) {
            serverResponse.value = 'Failed to communicate with server';
            console.error('Error fetching data', error);
        }
    }

    // Load Matches
    async function fetchMatches() {
        try {
            const teamData = {'team1': teamOne.value, 'team2': teamTwo.value}
            const response = await axios({
                method: 'post',
                url: 'pinochle_matches',
                data: teamData
            });
            
            if (response.data.status === 'success') {
                matches.value = [NO_DATA]
                const matchData = response.data.data

                matchData.matches.forEach(match => {
                    matches.value.push(match)
                })
                
                if (teamOne.value !== matchData.team1.team_name) {
                    teamSwapMessage.value = true;
                    teamOne.value = matchData.team1.team_name;
                    teamTwo.value = matchData.team2.team_name;
                }

                lockedPlayers.value = []
                teamOneData = matchData.team1;
                teamTwoData = matchData.team2;
                lockedPlayers.value.push(matchData.team1.player_1)
                lockedPlayers.value.push(matchData.team1.player_2)
                lockedPlayers.value.push(matchData.team2.player_1)
                lockedPlayers.value.push(matchData.team2.player_2)
            } else {
                serverResponse.value = 'Failed to load match data ' + response.data.message;
            }
        } catch (error) {
            serverResponse.value = 'Failed to communicate with server';
            console.error('Error fetching data', error);
        }
    }

    function lockReady() {
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

    async function quickSetup() {
        teamOne.value = 'Kamliya';
        teamTwo.value = 'The Inlaws';
        props.teamAndGameLocked = true;
        currentMatch.value = '01-03-2025.1'
        selectedDate = '01-03-2025';
        selectedGameOfDay = 1;
        await fetchMatches();
        await fetchMatch();
    }

    function handleDateData(dateData) {
        createMatch(dateData);
    }

    function handleDeleteMatch(dateData) {
        deleteMatch(dateData)
    }

    function findMatch() {
        fetchMatch();
    }

    function matchSelected(dateData) {
        currentMatch.value = dateData.dateGameStr;
        selectedDate = dateData.date;
        selectedGameOfDay = dateData.gameOfDay;
    }

    watch(() => props.teamAndGameLocked, () => {
        fetchMatches();
        if (!props.teamAndGameLocked) {
            rounds.value = [];
            roundSelected.value = false;
        }
    });

    defineExpose({
        lockReady
    });

    // onMounted(() => {
    //     quickSetup()
    // })
</script>

<template>
    <div v-if="serverResponse">{{ serverResponse }}</div>

    <!-- <button @click="quickSetup">driver function</button> -->
    <div>
        <div class="input-div">
            <label><span class="default-header">Team One</span><br><select v-model="teamOne" :disabled="teamAndGameLocked"><option v-for="team in teams" :value="team">{{team}}</option></select></label>
            <label><span class="default-header">Team Two</span><br><select v-model="teamTwo" :disabled="teamAndGameLocked"><option v-for="team in teams" :value="team">{{team}}</option></select></label>
            <div v-if="teamSwapMessage">Team One and Two were swapped</div>
        </div>
    </div>

    <div v-if="teamAndGameLocked">
        <hr>
        <div><date_handling :matches="matches" @sendDateData="handleDateData" @sendMatchSelected="matchSelected" @deleteMatch="handleDeleteMatch"/></div>

        <hr>
        <div class="input-div">
            <label>Selected Match<br><input type="text" v-model="currentMatch" disabled></label>
            <button @click="findMatch">Look Up Match</button>
            <span v-if="inputErrorMessage" class="error-message">{{inputErrorMessage}}</span>
        </div>
    </div>
    <div v-if="roundSelected && teamAndGameLocked">
        <table class="round-table">
            <tr>
                <td class="input-td">
                    Round
                </td>
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

            <tr v-for="round in rounds" :class="round.roundAfterWinner">
                <td class="input-td">
                    {{ round.round_number }}
                </td>
                <td class="input-td">
                    <div :class="round.suitError">
                        <label><input type="radio" value="Clubs" v-model="round.trump">Clubs</label><br>
                        <label><input type="radio" value="Diamonds" v-model="round.trump">Diamonds</label><br>
                        <label><input type="radio" value="Spades" v-model="round.trump">Spades</label><br>
                        <label><input type="radio" value="Hearts" v-model="round.trump">Hearts</label><br>
                    </div>

                </td>
                <td class="input-td">
                    <div :class="round.bidderError">
                        <div v-for="lockedPlayer in lockedPlayers">
                            <label>
                                <input type="radio" :value="lockedPlayer" v-model="round.top_bidder">
                                {{ lockedPlayer }}
                            </label><br>
                        </div>
                    </div>
                </td>

                <td class="input-td"><label class="round-input-label" :class="round.bidError">Top Bid<input v-model="round.bid" type="number" class="number-input"></label></td>
                <td class="input-td">
                    <label class="round-input-label" :class="round.meldError_1">Meld<input v-model="round.meld_1" type="number" class="number-input"></label>
                    <label class="round-input-label" :class="round.trickError_1">Tricks<input v-model="round.tricks_1" type="number" class="number-input"></label>
                    <br>
                    <label class="round-input-label">Change<input v-model="round.change_1" type="number" class="number-input" disabled></label>
                    <label class="round-input-label">Total<input v-model="round.total_1" type="number" :class="round.winner_1" class="number-input" disabled></label>

                </td>
                <td class="input-td">
                    <label class="round-input-label" :class="round.meldError_2">Meld<input v-model="round.meld_2" type="number" class="number-input"></label>
                    <label class="round-input-label" :class="round.trickError_2">Tricks<input v-model="round.tricks_2" type="number" class="number-input"></label>
                    <br>
                    <label class="round-input-label">Change<input v-model="round.change_2" type="number" class="number-input" disabled></label>
                    <label class="round-input-label">Total<input v-model="round.total_2" type="number" :class="round.winner_2" class="number-input" disabled></label>
                </td>
            </tr>
        </table>

        <div v-if="gameOver">
            Winner
        </div>

        <div class="table-buttons">
            <button @click="validateAndAddEmptyRow">ADD ROW</button>
            <button @click="calculateTotals">Calcualte Totals</button>
            <button @click="submitGames">Submit Data</button>
            <button @click="removeRow">Remove Last Row</button>
        </div>

        {{ popupResponse }}
    </div>

</template>

<style scoped>
    .table-buttons {
        display: flex;
        padding: 10px;
        gap: 10px;
    }

    .round-table {
        margin: 5px;
        padding: 10px;
    }

    .round-input-label {
        padding: 4px;
    }

    .input-td {
        border: solid;
        border-collapse: collapse;
        padding: 5px;
    }

    .winning-score {
        background-color: rgb(60, 169, 10);
    }

    .number-input {
        margin: 5px;
        width: 6ch;
    }

    .invalid-input {
        border: red solid;
    }

    .invalid-row {
        background-color: red;
    }

    .error-message {
        color: red;
    }

    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

</style>