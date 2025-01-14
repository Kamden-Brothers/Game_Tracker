<script setup>
    import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
    import axios from 'axios'

    const NO_DATA = 'Nothing Selected';

    // Webpage responses
    const showSubmit = ref(false);
    const showDeleteSubmit = ref(false);
    const submitQuestion = ref('');
    const serverResponse = ref('');

    // Team input data
    const teamName = ref('');
    const selectUsername1 = ref(NO_DATA);
    const playerName1 = ref('');
    const selectUsername2 = ref(NO_DATA);
    const playerName2 = ref('');
    const teamSelect = ref(NO_DATA);

    const teamOptions = ref([]);
    const playerOptions = ref([]);
    const popupSubmitForm = ref(null);
    const popupDeleteForm = ref(null);
    const popupButton = ref(null);
    const deleteButton = ref(null);

    let postTeamData = {};
    let deleteTeamData = {};
    let teamData = [];
    let playerData = {};
    
    function resetForm() {
        teamName.value = '';
        selectUsername1.value = '';
        playerName1.value = '';
        selectUsername2.value = '';
        playerName2.value = '';
        teamSelect.value = NO_DATA;
    }

    function lettersOnly(str, valName) {
        // Check if value contains only letters and is not empty
        if (!/[A-Za-z_-]+/g.test(str)) {
            throw new Error(`"${valName}" cannot be blank`);
        }
    }

    function validateData(str, valName) {
        // Check letters only and Value is not NO_DATA
        lettersOnly(str, valName);
        if (str.toUpperCase() === NO_DATA.toUpperCase()) {
            throw new Error(`"${valName}" cannot be ${NO_DATA}`);
        }
    };

    function addTeamWarning() {
        try {
            validateData(selectUsername1.value, 'selectUsername1');
            validateData(selectUsername2.value, 'selectUsername2');
            validateData(teamName.value, 'teamName');
            lettersOnly(teamSelect.value, 'teamSelect');

        }
        catch (error) {
            showSubmit.value = false;
            submitQuestion.value = error.message;
            popupSubmitForm.value.classList.add("show");
            return
        }
        
        postTeamData = {}
        postTeamData['player1'] = selectUsername1.value;
        postTeamData['player2'] = selectUsername2.value;
        postTeamData['teamName'] = teamName.value;
        postTeamData['selectedTeam'] = teamSelect.value;

        if (teamSelect.value !== 'None') {
            postTeamData['selectedTeam'] = teamSelect.value;
            postTeamData['updateTeam'] = true;
        } else {
            postTeamData['selectedTeam'] = null;
            postTeamData['updateTeam'] = false;
        }
        
        showSubmit.value = true;
        if (teamSelect.value !== 'None') {
            submitQuestion.value = `Are you sure you want to update ${teamSelect.value} to "${teamName.value}" with username "${selectUsername1.value}", "${selectUsername2.value}"`;
        }
        else {
            submitQuestion.value = `Are you sure you want to add team "${teamName.value}" with users "${selectUsername1.value}" and "${selectUsername2.value}"`;
        }

        popupSubmitForm.value.classList.add("show");
    };

    async function submitTeamData() {
        popupSubmitForm.value.classList.remove("show");
        await submitData();
        await fetchTeams();
    };

    function deleteTeamWarning() {
        try {
            lettersOnly(teamSelect.value, 'For delete teamSelect');
        }
        catch (error) {
            showDeleteSubmit.value = false;
            submitQuestion.value = error.message;
            popupDeleteForm.value.classList.add("show");
            return
        }
        
        deleteTeamData = {}
        deleteTeamData['selectedTeam'] = teamSelect.value;

        showDeleteSubmit.value = true;
        submitQuestion.value = `Are you sure you want to DELETE ${teamSelect.value}`;
        popupDeleteForm.value.classList.add("show");
    };


    function dismissSubmitPopup() {
        popupSubmitForm.value.classList.remove("show");
    };

    function dismissDeletePopup() {
        popupDeleteForm.value.classList.remove("show");
    };
    
    const handleOutsideClickSubmitPopup = (event) => {
        if (popupSubmitForm.value.classList.contains("show")) {
            if (popupSubmitForm.value && !popupSubmitForm.value.contains(event.target) && !popupButton.value.contains(event.target)) {
                dismissSubmitPopup();
            }
        }
    };
    
    const handleOutsideClickDeletePopup = (event) => {
        if (popupDeleteForm.value.classList.contains("show")) {
            if (popupDeleteForm.value && !popupDeleteForm.value.contains(event.target) && !deleteButton.value.contains(event.target)) {
                dismissDeletePopup();
            }
        }
    };
    
    const disablePlayerSelect = computed(() => {
        return teamSelect.value !== NO_DATA;
    })

    watch(teamSelect, (newVal) => {
        let team = teamData[newVal];
        
        if (team) {
            teamName.value = newVal;
            selectUsername1.value = team[0];
            selectUsername2.value = team[1];
        }
        else {
            teamName.value = '';
            selectUsername1.value = '';
            selectUsername2.value = '';
        }
    });

    watch(selectUsername1, (newVal) => {
        let player = playerData[newVal];
        if (player) {
            playerName1.value = player[0];
        }
        else {
            playerName1.value = '';
        }
    });

    watch(selectUsername2, (newVal) => {
        let player = playerData[newVal];
        if (player) {
            playerName2.value = player[0];
        }
        else {
            playerName2.value = '';
        }
    });

    async function deleteTeamEvent() {
        popupDeleteForm.value.classList.remove("show");
        await deleteTeam();
        await fetchTeams();
    }

    const deleteTeam = async () => {
        try {
            const response = await axios({
                method: 'post',
                url: '/delete_team',
                data: deleteTeamData
            });
            
            if (response.data.status === 'success') {
                serverResponse.value = `Successfully deleted ${teamSelect.value}`;
                resetForm();
            } else {
                serverResponse.value = response.data.message;
            }
        } catch (error) {
            serverResponse.value = 'Failed to communicate with server';
            console.error(`Error deleting ${teamSelect.value}:`, error);
        }
    };

    const submitData = async () => {
        try {
            const response = await axios({
                method: 'post',
                url: '/submit_team',
                data: postTeamData
            });

            if (response.data.status === 'success') {
                serverResponse.value = `Successfully added teamName="${teamName.value}" with users "${selectUsername1.value} and ${selectUsername2.value}"`;
                resetForm();
            } else {
                serverResponse.value = response.data.message;
            }

        } catch (error) {
            serverResponse.value = 'Failed to communicate with server';
            console.error('Error fetching data:', error);
        }
    };

    // Load Teams
    const fetchTeams = async () => {
        try {
            const response = await axios.get('http://localhost:5000/current_teams');
            teamData = response.data;
            teamOptions.value = [NO_DATA];
            Object.keys(response.data).forEach(team => {
                teamOptions.value.push(team);
            })

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    // Load players
    const fetchPlayers = async () => {
        try {
            const response = await axios.get('http://localhost:5000/current_players');
            playerData = response.data;
            playerOptions.value = [NO_DATA]
            Object.keys(response.data).forEach(player => {
                playerOptions.value.push(player)
            })

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    onMounted(() => {
        fetchTeams();
        fetchPlayers();
        document.addEventListener("click", handleOutsideClickSubmitPopup);
        document.addEventListener("click", handleOutsideClickDeletePopup);
    });

    onUnmounted(() => {
        document.removeEventListener("click", handleOutsideClickSubmitPopup);
        document.removeEventListener("click", handleOutsideClickDeletePopup);
    });
</script>

<template>
    <div class="response_message" v-if="serverResponse">{{serverResponse}}</div>

    <div class="input_header_div">
        <div class="table_wrapper">
            <table class="drop_down_add_table">
                <tr>
                    <td class="td_border">
                        <div class="label_wrap">
                            <label>Enter Team Name<br /><input v-model="teamName"/></label>
                        </div>
                    </td>
                    <td class="td_border">
                        <div class="label_wrap">
                            <label>Update Team Name<br />
                                <select v-model="teamSelect">
                                    <option v-for="teamOption in teamOptions" :value="teamOption">{{teamOption}}</option>
                                </select>
                            </label>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td class="td_border">
                        <div class="label_wrap">
                            <label>Select Username 1<br />
                                <select v-model="selectUsername1" :disabled="disablePlayerSelect">
                                    <option v-for="playerOption in playerOptions" :value="playerOption">{{playerOption}}</option>
                                </select>
                            </label>
                        </div>
                    </td>
                    <td class="td_border">
                        <div class="label_wrap">
                            <label>Select Username 2<br />
                                <select v-model="selectUsername2" :disabled="disablePlayerSelect">
                                    <option v-for="playerOption in playerOptions" :value="playerOption">{{playerOption}}</option>
                                </select>
                            </label>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td class="td_border">
                        <div class="label_wrap">
                            <label>Player Name 1<br /><input v-model="playerName1" disabled/></label>
                        </div>
                    </td>
                    <td class="td_border">
                        <div class="label_wrap">
                            <label>Player Name 2<br /><input v-model="playerName2" disabled/></label>
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        <div class="submit_buttons">
            <div class="popup">
                <button @click="deleteTeamWarning" ref="deleteButton">Delete Team</button>
                <div class="popuptext" ref="popupDeleteForm">{{submitQuestion}}
                    <br/>
                    <button @click="deleteTeamEvent" v-if="showDeleteSubmit">Yes</button>
                    <button @click="dismissDeletePopup" v-if="showDeleteSubmit">No</button>
                </div>
            </div>
            <div class="popup">
                <button @click="addTeamWarning" ref="popupButton">Add Team</button>
                <div class="popuptext" ref="popupSubmitForm">{{submitQuestion}}
                    <br/>
                    <button @click="submitTeamData" v-if="showSubmit">Yes</button>
                    <button @click="dismissSubmitPopup" v-if="showSubmit">No</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
.response_message {
    display: inline-block;
    width: 100%;
    height: 30px;
    text-align: center;
    background: #23b115;
    font-size: 20px;
}

.submit_buttons {
    padding: 10px;
    align-content: center;
    text-align: center;
}

.table_wrapper{
    display: inline-block;
    padding: 10px;
}

.drop_down_add_table {
    background: #9BCBEB;
    border: solid;
    width: 500px;
}

.input_header_div {
    background: #9BCBEB;
    padding: 4px;
    text-align: center;
    align-content: center;
    display: inline-block;
    width: 100%;
}

.td_border {
    background: #9BCBEB;
    border: solid;
    text-align: center;
}

.label_wrap {
    display: inline-block;
    width: 250px;
}


/* Popup container */
.popup {
  position: relative;
  display: inline-block;
}

/* The actual popup (appears on top) */
.popup .popuptext {
  visibility: hidden;
  width: 400px;
  background-color: #555;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 8px 0;
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  margin-left: -200px;
}

/* Popup arrow */
.popup .popuptext::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #555 transparent transparent transparent;
}

/* Toggle this class when clicking on the popup container (hide and show the popup) */
.popup .show {
  visibility: visible;
  -webkit-animation: fadeIn 1s;
  animation: fadeIn 1s
}

/* Add animation (fade in the popup) */
@-webkit-keyframes fadeIn {
  from {opacity: 0;}
  to {opacity: 1;}
}

@keyframes fadeIn {
  from {opacity: 0;}
  to {opacity:1 ;}
}
</style>