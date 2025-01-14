<script setup>
    import { ref, watch, defineEmits, onMounted } from 'vue';
    import { parse, format } from 'date-fns';

    const NO_DATA = 'Nothing Selected';

    const date = ref('');
    const gameOfDay = ref(1);

    const selectedMatch = ref(NO_DATA);

    const emit = defineEmits();

    function matchSelected() {
        const dateData = {'date': date.value,
                          'gameOfDay': gameOfDay.value,
                          'dateGameStr': `${date.value}.${gameOfDay.value}`};
        emit('sendDateData', dateData)
    };

    watch(date, (newVal) => {
        // Update gameOfDay if date was set manually by user
        if (selectedMatch.value === NO_DATA && newVal) {
            let selectedDate = format(parse(newVal, 'yyyy-MM-dd', new Date()), 'MM-dd-yyyy')
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
        <label>Select Match<select v-model="selectedMatch"><option v-for="match in matches" :value="match">{{ match }}</option></select></label>
        
        <div>
            <div class="label-padding">Create New match</div>
            <div class="input-div">
                <input type="date" v-model="date">
                <input type="number" v-model="gameOfDay" disabled>
                <button @click="matchSelected">Create Match</button>
            </div>
        </div>
    </div>
</template>