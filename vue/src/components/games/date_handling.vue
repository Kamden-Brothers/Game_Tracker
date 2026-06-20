<script setup>
    import { ref, watch, defineEmits, onMounted } from 'vue';
    import { parse, format } from 'date-fns';

    const NO_DATA = 'Nothing Selected';

    const date = ref('');
    const gameOfDay = ref(1);
    const createMatch = ref(false);

    const selectedMatch = ref(NO_DATA);

    const emit = defineEmits();

    function parseSelectedMatch(val) {
        const splitVals = val.split('.');
        const fnDate = parse(splitVals[0], 'MM-dd-yyyy', new Date());

        const dateData = {'date': format(fnDate, 'yyyy-MM-dd'),
                            'gameOfDay': splitVals[1],
                            'dateGameStr': val}
        return dateData
    }

    function checkSelected() {
        if (selectedMatch.value && selectedMatch.value !== NO_DATA) {
            return true;
        }
        return false;
    }

    function matchSelected() {
        const dateData = {'date': date.value,
                        'gameOfDay': gameOfDay.value,
                        'dateGameStr': `${date.value}.${gameOfDay.value}`};
        emit('sendDateData', dateData)
    };

    function createNewMatch() {
        if (date.value && gameOfDay.value > 0) {
            matchSelected();
            return;
        };
    };

    function deleteMatch() {
        if (checkSelected()) {
            emit('deleteMatch', parseSelectedMatch(selectedMatch.value))
        }
    }

    function lookUpMatch() {
        console.log('Looking');
    };


    function toggleSelect() {
        createMatch.value = !createMatch.value;
    }

    watch(date, (newVal) => {
        // Update gameOfDay if date was set manually by user
        if (newVal) {
            const selectedDate = format(parse(newVal, 'yyyy-MM-dd', new Date()), 'MM-dd-yyyy')
            const currentHighestMatch = props.matches
                .filter((match) =>  match.includes(selectedDate))
                .reduce((max, match) => {
                    const matchNumber = +match.split('.')[1];
                    return matchNumber > max ? matchNumber : max
                }, 0);
            gameOfDay.value = currentHighestMatch + 1;
        }
    })

    watch(selectedMatch, (newVal) => {
        if (newVal === NO_DATA) {
            date.value = null;
            gameOfDay.value = 1;
        }
        else {
            const splitVals = newVal.split('.');
            const fnDate = parse(splitVals[0], 'MM-dd-yyyy', new Date());

            const dateData = {'date': format(fnDate, 'yyyy-MM-dd'),
                              'gameOfDay': splitVals[1],
                              'dateGameStr': newVal}
            emit('sendMatchSelected', dateData);
        }
    });

    const props = defineProps({
        matches: {
            type: Array,
            required: true
        }
    });


</script>

<template>
    <div class="input-div">
        <div v-if="!createMatch">
            <span class="default-header">Select Match</span><button class="toggle-button left-margin" @click="toggleSelect">Change to Create Match</button>
            <div>
                <div class="match-select">
                    <select v-if="!createMatch" v-model="selectedMatch">
                        <option v-for="match in matches" :value="match">{{ match }}</option>
                    </select>
                </div>
                <button @click="lookUpMatch" class="toggle-button">Look Up Match</button>
                <button @click="deleteMatch" class="toggle-button">Delete Match</button>
            </div>
        </div>

        <div v-if="createMatch">
            <span class="default-header">Create Match</span><button class="toggle-button" @click="toggleSelect">Change to Select Match</button>
            <div>
                <div class="match-select">
                    <input type="date" v-model="date">
                    <input type="number" v-model="gameOfDay" disabled>
                </div>
                <button @click="createNewMatch" class="toggle-button">Create Match</button>
            </div>
        </div>

    </div>
</template>

<style scoped>
    .match-select {
        padding: 10px 10px 10px 0px;
    }

    .display-match-items {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }

    .toggle-button {
        padding: 5px 10px;
        border: none; /* Remove default border */
        border-radius: 5px; /* Rounded corners */
        cursor: pointer; /* Pointer cursor on hover */
        color: white;
        background-color: #33aa33;
    }

    .left-margin {
        margin: 0px 0px 0px 10px;
    }
</style>