#!/usr/bin/python3
import os
import json

from sys import argv

FILE_NAME = 'pydo.td'
PATH_FILE_NAME = '/pydo.td'
SPACING = ':  '
COMPLETE_MARK = ' [x]'
INIT_TODO = {
    "remember-header": "\n REMEMBER\n --------",
    "remember-items": [

    ],
    "header": "\n TODO\n ----",
    "tasks": [
    ],
    "completed-tasks": 0,
    "unfinished-tasks": 0
}
COMMAND = 1
ARGUMENT = 2
ADDITIONAL_ARG = 3
DELETE_REPLY_CHOICE = 'Are you sure you want to delete your pydo from this directory (y/n): '
DELETE_TASK = 'DELETING PYDO FROM DIRECTORY'
INIT_TASK = 'Initializing TODO in '
INIT_TASK_COMPLETE = 'Todo has already been initialized'
INIT_REPLY_CHOICE = 'Todo has not yet been created \n do you want to initialize one (y/n): '
INSERT_ERROR = 'You need to pass in a line index to insert (pydo insert x)'
RESET_WARNING_CHOICE = 'Do you really want to reset (y/n): '
RESET_TASK = 'resetting pydo'
INDEX_INVALID_WARNING = 'Not a valid Index'
BACKWARD_COMPATIBILITY_NOTICE = 'Updating Pydo list to fit newest format'
HELP = '\nPYDO\n____\n\n Available commands:\n- add\n- reset\n- remove <INDEX>\n- remove all (removes all completed)\n- complete <INDEX>\n- delete\n- insert <TASK> <INDEXTOINSERT>\n- remember <REMEMBERTEXT>\n- remove-remember <REMEMBERINDEX>'


class Colors:
    Warning = '\033[93m'
    Done = '\033[92m'
    Normal = '\033[94m'
    End = '\x1b[0m'


def get_reply(reply_choice):
    return str(input(reply_choice)).lower().strip()


def delete_todo():
    if get_reply(DELETE_REPLY_CHOICE) == 'y':
        print(Colors.Warning, DELETE_TASK, Colors.End)
        os.remove(FILE_NAME)


def write_todo(text, is_init=False):
    try:
        with open(dir_path + PATH_FILE_NAME, "x") as f:
            if is_init:
                json.dump(text, f, indent=4)
    except FileExistsError:
        with open(dir_path + PATH_FILE_NAME, "w") as f:
            json.dump(text, f, indent=4)


def reset_todo():
    if get_reply(RESET_WARNING_CHOICE) == 'y':
        print(Colors.Warning, RESET_TASK, Colors.End)
        write_todo(INIT_TODO)


def init_todo():
    print(Colors.Normal, INIT_TASK + dir_path, Colors.End)
    write_todo(INIT_TODO, True)

#Edge case for a older version probably not needed anymore
def backwards_compatibility(td):
    try:
        has_count = td['unfinished-tasks'] + td['completed-tasks']
    except:
        print(Colors.Normal, BACKWARD_COMPATIBILITY_NOTICE, Colors.End)
        td['unfinished-tasks'] = 0
        td['completed-tasks'] = 0
        write_todo(td)


dir_path = os.getcwd()
todo = {}


def help():
    print(Colors.Normal, HELP, Colors.End)


def print_todo():
    print(Colors.Normal, todo['remember-header'], Colors.End)
    loop_index = 0
    for remember in todo['remember-items']:
        print(Colors.Normal, str(loop_index) + SPACING + remember['item'])
        loop_index += 1

    print(Colors.Normal, todo['header'] +
          ' Completed: ' + str(todo['completed-tasks']) + '/' + str(todo['unfinished-tasks']), Colors.End)
    loop_index = 0
    for task in todo['tasks']:
        color = Colors.Done if task['completed'] else Colors.Warning
        mark = '  \u2B24' if task['completed'] else '  \u25EF'
        print(color, str(loop_index) + SPACING +
              task['task'] + mark, Colors.End)
        loop_index += 1
    print()


def remember_todo(arguments):
    arg = arguments[ARGUMENT] if arguments[ARGUMENT] != None else ''
    todo['remember-items'].append({"item": arg})
    write_todo(todo)


def remove_completed():
    index = 0
    for task in todo['tasks']:
        if task['completed']:
            print('removing task ' + task['task'])
            del todo['tasks'][index]
            write_todo(todo)
            remove_completed()
        else:
            index += 1


def remove_remember(arguments):
    try:
        index = int(arguments[ARGUMENT])
        del todo['remember-items'][index]
        write_todo(todo)
    except:
        print(Colors.Warning, INDEX_INVALID_WARNING, Colors.End)


def add(arguments):
    arg = arguments[ARGUMENT] if arguments[ARGUMENT] != None else ''
    todo['tasks'].append({"task": arg, "completed": False})
    todo['unfinished-tasks'] += 1
    write_todo(todo)


def complete_todo(arguments):
    try:
        index = int(arguments[ARGUMENT])
        todo['tasks'][index]['completed'] = not todo['tasks'][index]['completed']
        if todo['tasks'][index]['completed']:
            todo['completed-tasks'] += 1
        else:
            todo['completed-tasks'] -= 1
        write_todo(todo)
    except:
        print(Colors.Warning, INDEX_INVALID_WARNING, Colors.End)


def remove_line(arguments):
    try:
        index = int(arguments[ARGUMENT])
        if not todo['tasks'][index]['completed']:
            todo['unfinished-tasks'] -= 1
        del todo['tasks'][index]
        write_todo(todo)
    except:
        try:
            if arguments[ARGUMENT] == 'all':
                remove_completed()
                print('all completed have been removed')
        except:
            print(Colors.Warning, INDEX_INVALID_WARNING, Colors.End)


def insert_todo(arguments):
    try:
        arg = arguments[ARGUMENT] if arguments[ARGUMENT] != None else ''
        index = int(arguments[ADDITIONAL_ARG])
        todo['tasks'].insert(index, {"task": arg, "completed": False})
        todo['unfinished-tasks'] += 1
        write_todo(todo)
    except:
        print(Colors.Warning, INSERT_ERROR, Colors.End)


switch_case = {
    'help': help,
    '-h': help,
    'add': add,
    'reset': reset_todo,
    'remove': remove_line,
    'complete': complete_todo,
    'delete': delete_todo,
    'insert': insert_todo,
    'remember': remember_todo,
    'remove-remember': remove_remember
}

if os.path.exists(FILE_NAME):
    with open(dir_path + PATH_FILE_NAME) as todo_file:
        todo = json.load(todo_file)
        backwards_compatibility(todo)
    try:
        cmd = argv[COMMAND]
        func = switch_case.get(cmd, print_todo)
        try:
            func(argv)
        except:
            func()
    except:
        print_todo()
elif get_reply(INIT_REPLY_CHOICE) == 'y':
    init_todo()
