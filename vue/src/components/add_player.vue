<script setup>
    import { ref, computed, onMounted, watch, onUnmounted} from 'vue'
    import axios from 'axios'

    const NO_DATA = 'Nothing Selected';

    // Server responses
    const showSubmit = ref(false);
    const showDelete = ref(false);
    const submitQuestion = ref('');
    const deleteQuestion = ref('');
    const serverResponse = ref('');

    // User input
    const firstName = ref('');
    const username = ref('');
    const selectUsername = ref(NO_DATA);

    const dropdownAttributes = ref('');
    const playerOptions = ref([]);
    const popupSubmitForm = ref(null);
    const popupDeleteForm = ref(null);
    const popupButton = ref(null);
    const popupDeleteButton = ref(null);

    let postSubmit = {};
    let postDelete = {};
    let playerData = [];

    function resetForm() {
        firstName.value = '';
        username.value = '';
        selectUsername.value = NO_DATA;
    }

    function lettersOnly(str, valName) {
        // Check if value contains only letters and is not empty
        if (!/[A-Za-z_-]+/g.test(str)) {
            throw new Error(`"${valName}" cannot be blank`);
        }
    };

    function validateData(str, valName) {
        // Check letters only and Value is not NO_DATA
        lettersOnly(str, valName);
        if (str.toUpperCase() === NO_DATA.toUpperCase()) {
            throw new Error(`"${valName}" cannot be ${NO_DATA}`);
        }
    };

    function addPlayerWarning() {
        try {
            validateData(firstName.value, 'firstName');
            validateData(username.value, 'username');
            lettersOnly(selectUsername.value, 'selectUsername');
        }
        catch (error) {
            showSubmit.value = false;
            submitQuestion.value = error.message;
            popupSubmitForm.value.classList.add("show");
            return
        }
        
        postSubmit = {};
        postSubmit['firstName'] = firstName.value;
        postSubmit['username'] = username.value;
        if (selectUsername.value !== 'None') {
            postSubmit['selectedPlayer'] = selectUsername.value;
            postSubmit['updatePlayer'] = true;
        } else {
            postSubmit['selectedPlayer'] = null;
            postSubmit['updatePlayer'] = false;
        }
        
        showSubmit.value = true;
        if (selectUsername.value !== 'None') {
            submitQuestion.value = `Are you sure you want to update ${selectUsername.value} to "${firstName.value}" with username "${username.value}"`;
        }
        else {
            submitQuestion.value = `Are you sure you want to add "${firstName.value}" with username "${username.value}"`;
        }

        popupSubmitForm.value.classList.add("show");
    };

    function deletePlayerWarning() {
        try {
            validateData(selectUsername.value, 'For delete selectUsername');
        }
        catch (error) {
            showDelete.value = false;
            deleteQuestion.value = error.message;
            popupDeleteForm.value.classList.add("show");
            return
        }

        postDelete['selectedPlayer'] = selectUsername.value;
        showDelete.value = true;
        deleteQuestion.value = `Are you sure you want to delete ${selectUsername.value}`;
        popupDeleteForm.value.classList.add("show");
    };

    async function submitPlayerData() {
        popupSubmitForm.value.classList.remove("show");
        await submitData();
        await fetchPlayer();
    };
    
    function dismissSubmitPopup() {
        popupSubmitForm.value.classList.remove("show");
    };

    function dismissDeletePopup() {
        popupDeleteForm.value.classList.remove("show");
    };

    async function deletePlayerData() {
        dismissDeletePopup();
        await deletePlayer();
        await fetchPlayer();
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
            if (popupDeleteForm.value && !popupDeleteForm.value.contains(event.target) && !popupDeleteButton.value.contains(event.target)) {
                dismissDeletePopup();
            }
        }
    }
    
    watch(selectUsername, (newVal) => {
        let player = playerData[newVal];
        if (player) {
            firstName.value = player[0];
            username.value = newVal;
        }
        else {
            firstName.value = '';
            username.value = '';
        }
    });

    const deletePlayer = async () => {
        try {
            const response = await axios({
                method: 'post',
                url: 'delete_player',
                data: postDelete
            });

            if (response.data.status === 'success') {
                serverResponse.value = `Successfully deleted ${postDelete.selectedPlayer}`;
                resetForm();
            } else {
                serverResponse.value = response.data.message;
            }
        } catch (error) {
            serverResponse.value = 'Failed to communicate with server';
            console.error('Error fetching data', error);
        }
    }

    const submitData = async () => {
        try {
            const response = await axios({
                method: 'post',
                url: '/submit_player',
                data: postSubmit
            });

            if (response.data.status === 'success') {
                serverResponse.value = `Successfully added firstName="${firstName.value}", username="${username.value}"`;
                resetForm();
            } else {
                serverResponse.value = response.data.message;
            }

        } catch (error) {
            serverResponse.value = 'Failed to communicate with server';
            console.error('Error fetching data:', error);
        }
    };

    const fetchPlayer = async () => {
        try {
            const response = await axios.get('/current_players');
            playerData = response.data;
            playerOptions.value = [NO_DATA];
            Object.keys(response.data).forEach(player => {
                playerOptions.value.push(player);
            })

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    onMounted(() => {
        fetchPlayer();
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
                            <label>Enter First Name<br /><input v-model="firstName"/></label>
                        </div>
                    </td>
                    <td class="td_border">
                        <div class="label_wrap">
                            <label>Enter Username<br /><input v-model="username"/></label>
                        </div>
                    </td>
                    <td class="td_border">
                        <div class="label_wrap">
                            <label>Update Player Data<br />
                                <select v-model="selectUsername">{{dropdownAttributes}}
                                    <option v-for="playerOption in playerOptions" :value="playerOption">{{playerOption}}</option>
                                </select>
                            </label>
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        <div class="submit_buttons">
            <div class="popup">
                <button @click="deletePlayerWarning" ref="popupDeleteButton">Delete Player</button>
                <div class="popuptext" ref="popupDeleteForm">{{deleteQuestion}}
                    <br/>
                    <button @click="deletePlayerData" v-if="showDelete">Yes</button>
                    <button @click="dismissDeletePopup" v-if="showDelete">No</button>
                </div>
            </div>
            <div class="popup">
                <button @click="addPlayerWarning" ref="popupButton">Add Player</button>
                <div class="popuptext" ref="popupSubmitForm">{{submitQuestion}}
                    <br/>
                    <button @click="submitPlayerData" v-if="showSubmit">Yes</button>
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