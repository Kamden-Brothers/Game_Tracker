<template>
    <nav class="header">
        <RouterLink class="header_item" to="/">Home</RouterLink>
        <RouterLink class="header_item" to="/add_player">Add Player</RouterLink>
        <RouterLink class="header_item" to="/add_team">Add Team</RouterLink>
        <RouterLink class="header_item" to="/create_game">Create Game</RouterLink>
    </nav>
    <main>
        <RouterView />
    </main>
</template>

<style>        
    .input-div {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 10px;
        padding: 10px;
        margin: 0 auto;
    }

    /* Should be the same as input-div padding */
    .label-padding {
        padding: 0px 0px 0px 10px;
    }

    select {
        padding: 4px;
        font-size: 1rem;
        border: 1px solid #ccc;
        border-radius: 4px;
        width: 100%;
        max-width: 200px;
    }

    select:disabled {
        background-color: #f0f0f0;
        color: #888;
        cursor: not-allowed;
    }

    .lock-button {
        padding: 10px 15px;
        font-size: 1rem;
        color: #fff;
        background-color: #33aa33;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.3s ease;
        width: 100%;
        max-width: 200px;
    }

    .lock-button:hover {
        background-color: #00dd00;
    }

</style>

<style scoped>
    .header {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #6099be;
        padding: 15px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        font-family: 'Arial', sans-serif;
    }

    .header_item {
        margin: 0 20px;
        padding: 10px 15px;
        color: #fff;
        font-size: 30px;
        text-transform: uppercase;
        text-decoration: none;
        border-radius: 12px;
        position: relative;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
    }

    .header_item:hover {
        background-color: #e74c3c;
        box-shadow: 0 0 12px rgba(231, 76, 60, 0.6);
        transform: scale(1.05);
    }

    .header_item:focus {
    outline: 2px solid #fff;
    outline-offset: 2px;
    }

    .header_item:nth-child(1)::before {
    content: '♠';
    font-size: 30px;
    color: black;
    }

    .header_item:nth-child(2)::before {
    content: '♥';
    font-size: 30px;
    color: red;
    }

    .header_item:nth-child(3)::before {
    content: '♣';
    font-size: 30px;
    color: black;
    }

    .header_item:nth-child(4)::before {
    content: '♦';
    font-size: 30px;
    color: red;
    }

</style>