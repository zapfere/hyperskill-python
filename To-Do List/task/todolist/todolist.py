from datetime import datetime, timedelta
from sqlalchemy import Column, Date, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import close_all_sessions, sessionmaker

Base = declarative_base()
connect_str = "sqlite:///todo.db?check_same_thread=False"
date_format = "%Y-%m-%d"
# main menu
menu_text = """
1) Today's tasks
2) Week's tasks
3) All tasks
4) Missed tasks
5) Add task
6) Delete task
0) Exit
"""
# text constants
today_text = "Today {day_month}:"
week_text = "{week_day} {day_month}:"
all_text = "All tasks:"
missed_text = "Missed tasks:"
bye_text = "Bye!"
no_tasks_text = "Nothing to do!"
nothing_missed_text = "Nothing is missed!"
enter_task_text = "Enter task"
enter_date_text = "Enter deadline"
task_added_text = "The task has been added!"
to_delete_text = "Chose the number of the task you want to delete:"
deleted_text = "The task has been deleted!"
# weekdays mapping
week_days = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}


class Table(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return f"task (id={self.id}, " \
               f"task='{self.task}', deadline='{self.deadline}')"

    def __str__(self):
        return self.task


def main():
    """Main loop to choose an action or quit"""
    command = -1

    while command != 0:
        print(menu_text)
        command = int(input())
        choose_action(command)

    print(bye_text)


def choose_action(action_id):
    """Chooses between available actions"""
    if action_id == 1:
        today_list()
    elif action_id == 2:
        week_list()
    elif action_id == 3:
        all_tasks_list()
    elif action_id == 4:
        missed_list()
    elif action_id == 5:
        add_task()
    elif action_id == 6:
        delete_task()


def today_list():
    """Tasks for today"""
    today = datetime.today()
    header = today_text.format(day_month=get_day_and_month(today))
    filter_today = Table.deadline == today.date()
    tasks = query_tasks(query_filter=filter_today)
    print_list(header, tasks)


def week_list():
    """Tasks for a week starting from today"""
    today = datetime.today()
    a_week_after = today + timedelta(days=6)
    filter_between = Table.deadline.between(
        today.date(),
        a_week_after.date()
    )
    tasks = query_tasks(query_filter=filter_between)
    tasks_by_weekday = group_by_week_day(tasks, today)
    print_grouped_tasks(tasks_by_weekday)


def all_tasks_list():
    """All tasks"""
    tasks = query_tasks()
    print_list(all_text, tasks, print_date=True)


def missed_list():
    """Tasks with past deadline"""
    today = datetime.today().date()
    filter_missed = Table.deadline < today
    tasks = query_tasks(query_filter=filter_missed)
    print_list(
        missed_text,
        tasks,
        print_date=True,
        empty_text=nothing_missed_text
    )


def add_task():
    """Add new task"""
    print(enter_task_text)
    name = input()
    print(enter_date_text)
    deadline = datetime.strptime(input(), date_format)
    insert_task(name, deadline)
    print(task_added_text)


def delete_task():
    """Select existing task and remove it"""
    tasks = query_tasks()
    print_list(to_delete_text, tasks, print_date=True)
    task_num = int(input()) - 1
    task_to_delete = tasks[task_num]
    remove_task(task_to_delete)
    print(deleted_text)


def get_day_and_month(date_time):
    """Gets a str like "28 Apr" from a given datetime object"""
    return "{date} {time}".format(
        date=date_time.day,
        time=date_time.strftime("%b")
    )


def group_by_week_day(tasks, day_from):
    """Groups tasks from given list by weekday and returns a dict"""
    tasks_by_day = {}
    # create keys for all days
    for i in range(7):
        day = day_from + timedelta(days=i)
        tasks_by_day[day.date()] = []
    # fill with tasks
    for task in tasks:
        tasks_by_day[task.deadline].append(task)
    return tasks_by_day


def print_grouped_tasks(tasks_by_day):
    """Prints tasks grouped in lists by date"""
    for day, day_tasks in tasks_by_day.items():
        header = week_text.format(
            week_day=week_days[day.weekday()],
            day_month=get_day_and_month(day)
        )
        print_list(header, day_tasks)


def print_list(header, task_list, print_date=False, empty_text=no_tasks_text):
    """Print tasks from given list with header and optional date"""
    print(header)
    if len(task_list) == 0:
        print(empty_text)
    else:
        row_num = 1
        for task in task_list:
            print_task(task, row_num, print_date)
            row_num += 1
    print()


def print_task(task, row_num, print_date):
    """Print a task with given number and optional date"""
    task_text = f"{row_num}. {str(task)}"
    if print_date:
        task_text += ". " + get_day_and_month(task.deadline)
    print(task_text)


def insert_task(name, deadline):
    """Inserts new task into table"""
    new_task = Table(task=name, deadline=deadline)
    session.add(new_task)
    session.commit()


def remove_task(task):
    """Removes given task from table"""
    session.delete(task)
    session.commit()


def query_tasks(query_filter=None, order_by=Table.deadline):
    """Selects tasks with optional given filter and ordering"""
    if query_filter is None:
        return session.query(Table).order_by(order_by).all()
    return session.query(Table).filter(query_filter).order_by(order_by).all()


# init session
engine = create_engine(connect_str)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
# main logic
main()
# close session
close_all_sessions()
