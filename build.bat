&commat;ECHO OFF 

pyinstaller --onefile --console --name todolist-cli --add-data="task_app.tcss;." --add-data="tasks.json;." --add-data="utils.py;." main.py