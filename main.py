import utils as uti
from textual import on
import textual.app as textapp
import textual.widgets as textwid
import textual.containers as textcon
import datetime


class EditTaskScreen(textapp.Screen):
    BINDINGS = [("escape",  "app.pop_screen", "Cancel")]
    
    def __init__(self,id: str, **kwargs):
        super().__init__(**kwargs)
        self.task_id = id
    
    def compose(self):
        task_content = uti.get_task(self.task_id)
        yield textwid.Header()
        yield textwid.Label("Name")
        yield textwid.Input(placeholder=task_content["name"], id="input-name")
        yield textwid.Label("Due date")
        yield textwid.Input(placeholder=task_content["due_date"], id="input-due")
        yield textcon.Horizontal(
            textwid.Button("Save", id="save-task", variant="success"),
            textwid.Button("Cancel", id="cancel-task", variant="error"),
        )
    
    @on(textwid.Button.Pressed, "#save-task")
    def save_task(self):
        name_w = self.query_one("#input-name", textwid.Input)
        due_w = self.query_one("#input-due", textwid.Input)
        
        task_content = uti.get_task(self.task_id)
        if not name_w.value.strip() == "":
            uti.update_task(self.task_id, "name", name_w.value.strip())
        else:
            uti.update_task(self.task_id, "name", task_content["name"])
            
        if not due_w.value.strip() == "":
            uti.update_task(self.task_id, "due_date", due_w.value.strip())
        else:
            uti.update_task(self.task_id, "due_date", task_content["due_date"])
            
        self.app.reload_tasks()
        self.app.pop_screen()
            
    @on(textwid.Button.Pressed, "#cancel-task")
    def cancel(self):
        self.app.pop_screen()

class AddTaskScreen(textapp.Screen):
    BINDINGS = [("escape",  "app.pop_screen", "Cancel")]
    
    def compose(self):
        yield textwid.Header()
        yield textwid.Label("Name")
        yield textwid.Input(placeholder="Task name", id="input-name")
        yield textwid.Label("Due date")
        yield textwid.Input(placeholder="DD-MM-YY", id="input-due")
        # Checkbox exists in recent Textual versions; falls nicht, benutze Button/Toggle
        yield textcon.Horizontal(
            textwid.Button("Save", id="save-task", variant="success"),
            textwid.Button("Cancel", id="cancel-task", variant="error"),
        )
    
    @on(textwid.Button.Pressed, "#save-task")
    def save_task(self):
        name_w = self.query_one("#input-name", textwid.Input)
        due_w = self.query_one("#input-due", textwid.Input)
        # prüfe die Eingabewerte über .value
        if name_w.value.strip() and due_w.value.strip():
            uti.add_task(name_w.value.strip(), due_w.value.strip(), False)
            self.app.reload_tasks()
            self.app.pop_screen()
            
    @on(textwid.Button.Pressed, "#cancel-task")
    def cancel(self):
        self.app.pop_screen()
            

class Task(textcon.HorizontalGroup):
    def __init__(self, id: int,  name: str, date: str, done: bool) -> None:
        # Klasse zuweisen, damit TCSS gezielt stylen kann
        super().__init__(classes="task-row")
        self.task_id = id
        self.task_name = name
        self.task_date = date
        self.done = done

    def compose(self) -> textapp.ComposeResult:
        # yield textwid.TextArea.code_editor(self.task_name, language="markdown")
        current_date = datetime.date.today()
        
        yield textwid.Label(str(self.task_name), classes="task-name")
        yield textwid.Label(str(self.task_date), classes="task-date")
        if self.done:
            yield textwid.Label("✅")
        else:
            yield textwid.Label("❌")
        yield textwid.Button("Edit", id="task-edit", variant="default")
        yield textwid.Button("Delete", id="task-delete", variant="error")
        yield textwid.Button("Done", id="task-done", variant="success")
        
    @on(textwid.Button.Pressed, "#task-delete")
    def delete_task(self):
        uti.delete_task(self.task_id)
        self.app.reload_tasks()
        
    @on(textwid.Button.Pressed, "#task-done")
    def do_task(self):
        uti.update_task(self.task_id, "done", True)
        self.app.reload_tasks()
    
    @on(textwid.Button.Pressed, "#task-edit")
    def edit_task(self):
        self.app.push_screen(EditTaskScreen(self.task_id))
        

class Todolist(textapp.App):
    CSS_PATH = "task_app.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    
    def compose(self):
        
        tasks_list = []
        task_dic = uti.read_tasks()
        for x in task_dic:
            if not task_dic[x] == {}:
                task = task_dic[x]
                time_left = uti.get_time_left(task["due_date"])
                tasks_list.append(Task(x, task["name"], time_left, task["done"]))
        
        yield textwid.Button("Add Task", id="task_add", variant="success")
        yield textwid.Header()
        yield textcon.VerticalScroll(id="tasks-scroll", *tasks_list)
        yield textwid.Footer()
        
    def reload_tasks(self):
        container = self.query_one("#tasks-scroll", textcon.VerticalScroll)
        # sicher entfernen (je nach Textual-Version)
        if hasattr(container, "remove_children"):
            container.remove_children()
        elif hasattr(container, "clear"):
            container.clear()
        else:
            for child in list(container.children):
                child.remove()

        tasks_list = []
        task_dic = uti.read_tasks()
        for x in task_dic:
            if not task_dic[x] == {}:
                task = task_dic[x]
                time_left = uti.get_time_left(task["due_date"])
                tasks_list.append(Task(x, task["name"], time_left, task["done"]))
        # mount die neuen Items (auch wenn Liste leer ist, ist das unproblematisch)
        if tasks_list:
            container.mount(*tasks_list)
        
    def action_toggle_dark(self):
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
        
    @on(textwid.Button.Pressed, "#task_add")
    def add_task(self):
        self.push_screen(AddTaskScreen())
        
        
if __name__ == "__main__":
    app = Todolist()
    app.run()