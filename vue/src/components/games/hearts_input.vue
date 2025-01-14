<script setup>
    import { ref, watch, defineExpose } from 'vue';

    const NO_DATA = 'Nothing Selected';

    const playerOne = ref(NO_DATA);
    const playerTwo = ref(NO_DATA);
    const playerThree = ref(NO_DATA);
    const playerFour = ref(NO_DATA);
    
    const lockReady = () => {
        let errorMessage = '';
        if (playerOne.value === NO_DATA || playerOne.value === '') {
            errorMessage += 'Player one cannot be blank.';
        }
        if (playerTwo.value === NO_DATA || playerTwo.value === '') {
            errorMessage += ' Player two cannot be blank.';
        }
        if (playerThree.value === NO_DATA || playerThree.value === '') {
            errorMessage += ' Player three cannot be blank.';
        }
        if (playerFour.value === NO_DATA || playerFour.value === '') {
            errorMessage += ' Player four cannot be blank.';
        }

        if (!errorMessage) {
            const players = [playerOne.value, playerTwo.value, playerThree.value, playerFour.value];
            const uniquePlayers = new Set(players);
            if (uniquePlayers.size !== players.length) {
                errorMessage += ' Players must be unique.';
            }
        }
        
        return errorMessage.trim();
    }

    defineProps({
        players: {
            type: Array,
            required: true
        },
        teamAndGameLocked: {
            type: Boolean,
            required: true
        }
    });
    
    defineExpose({
        lockReady
    });

</script>

<template>
    <div class="input-div">
        <label>Player One<br><select v-model="playerOne" :disabled="teamAndGameLocked"><option v-for="player in players" :value="player">{{player}}</option></select></label>
        <label>Player Two<br><select v-model="playerTwo" :disabled="teamAndGameLocked"><option v-for="player in players" :value="player">{{player}}</option></select></label>
        <label>Player Three<br><select v-model="playerThree" :disabled="teamAndGameLocked"><option v-for="player in players" :value="player">{{player}}</option></select></label>
        <label>Player Four<br><select v-model="playerFour" :disabled="teamAndGameLocked"><option v-for="player in players" :value="player">{{player}}</option></select></label>
    </div>
</template>
