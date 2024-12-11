This app is used for storing and analyzing scores of Pinochle games. <br>
<br>
It uses an SQL database to store the data, Flask/HTML/JS/CSS to input and display data, and a Flask RESTful API for easy distribution of the data. <br>
The app is split up into 3 Microservices.
1. Input - Add data to the database through a flask server
2. Display - Display data to users
3. RESTful API - Allow users to 
<br>
![image](https://github.com/user-attachments/assets/1128b42a-6705-4ede-824e-08af8bd7882f)
<br><br><br>


**Database Structure**:<br><br>
**Player**<br>
player_id PK INT<br>
name STR<br>
<br>
<br>

**Team**<br>
team_id PK INT<br>
player_one_id FK INT<br>
player_two_id FK INT<br>
team_name STR<br>

**Game**<br>
game_id PK INT<br>
team_one FK INT<br>
team_two FK INT<br>
date DATE<br>
game_of_day INT<br>


**Round**<br>
round_id PK INT<br>
game_id FK INT<br>
round_number INT<br>
bid INT (>50)<br>
trump STR (Clubs, Spades, Diamonds, Hearts)<br>
top_bidder FK INT(player_id)<br>
meld_1 INT (>0)<br>
meld_2 INT (>0)<br>
tricks_1 INT (0-50)<br>
tricks_2 INT (0-50)<br>
points_gain_1 INT (>0)<br>
points_gain_2 INT (>0)<br>
