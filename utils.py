import json
import datetime
import os
import sys
import shutil

BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(__file__))

USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".todolist_cli")
os.makedirs(USER_DATA_DIR, exist_ok=True)

TASKS_FILE = os.path.join(USER_DATA_DIR, "tasks.json")

_default_tasks = os.path.join(BUNDLE_DIR, "tasks.json")
if not os.path.exists(TASKS_FILE) and os.path.exists(_default_tasks):
    shutil.copyfile(_default_tasks, TASKS_FILE)

# Benutze TASKS_FILE in deinen read/write-Funktionen
def read_tasks():
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data

def write_task(id:int, name:str, due_date:str, done:bool):
    old_tasks = read_tasks()
    old_tasks[str(id)] = {"name":name, "due_date": due_date, "done":done}
    
    json_task = json.dumps(old_tasks, indent=1)
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        f.write(json_task)

def get_task(id:int):
    return read_tasks().get(str(id))
    
def delete_task(id:int):
    old_tasks = read_tasks()
    old_tasks[str(id)] = { }
    json_task = json.dumps(old_tasks, indent=1)
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        f.write(json_task)

def add_task(name:str, due_date:str, done:bool):
    all_tasks = read_tasks()
    y = 0
    for x in all_tasks:
        if all_tasks[x] == { }:
            write_task(x, name, due_date, done)
            return
        y += 1
    write_task(str(y + 1 ), name, due_date, done)

def update_task(id:int, key:str, value):
    old_tasks = read_tasks()
    old_tasks[str(id)][key] = value

    json_task = json.dumps(old_tasks, indent=1)
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        f.write(json_task)
    
def get_time_left(due:str):
    split_due = due.split("-")
    due_date = datetime.date(int(split_due[2]), int(split_due[1]), int(split_due[0]))
    now = datetime.date.today()
    if due_date > now:
        date_left = due_date - now
        return(str(date_left).split(",")[0] + " Left")
    else:
        return("Deadline Missed")
