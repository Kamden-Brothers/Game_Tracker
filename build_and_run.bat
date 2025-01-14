cd vue
call npm run build

cd ../
call conda activate game_tracker
python app.py
