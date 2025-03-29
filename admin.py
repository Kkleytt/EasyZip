import flet as ft
import json as js
import keyboard as kb
import pymysql
from dotenv import load_dotenv, find_dotenv
import os
import time

from more import delete_user, reset_data


def app(page: ft.Page):
    global logs_text

    def on_enter(e):
        global logs_text

        if kb.is_pressed('enter'):
            command = command_field.value
            command_field.value = ""
            command_field.update()

            ext_lst = ['stop', 'exit', 'stop()', 'exit()', 'ext', 'ext()', 'quit', 'quit()', 'break', 'break()']
            logs_text += f">>> {command}\n"
            if command in ext_lst:
                logs_text += "Exit\n"
                page.window_destroy()
            else:
                if command[0:14:1] == "RESET DATA --v":
                    result = reset_data(CODE_1, CODE_2, False, connection)
                    logs_text += f"{result}"
                elif command[0:14:1] == "RESET DATA --r":
                    text = command.split(';')
                    if len(text) == 2:
                        code1 = text[0][15::1]
                        code2 = text[1][1::1]
                        if code1 == CODE_1 and code2 == CODE_2:
                            result = reset_data(CODE_1, CODE_2, False, connection)
                            logs_text += f"{result}"
                        else:
                            logs_text += "Неправильные пароли для сброса данных\n"
                    else:
                        logs_text += "Неправильные команда для сброса данных\n"

                elif command[0:12:1] == "DEL USER --n":
                    text = command.split('"')
                    if len(text) > 1:
                        name = text[1]
                        result = delete_user(name, HOST, USER, PASSWORD, DB_NAME)
                        logs_text += f"{result}"
                    else:
                        logs_text += "Неправильные команда для удаления пользователя\n"
                elif command[0:13:1] == "DEL USER --id":
                    text = command.split('"')
                    if len(text) > 2:
                        id = text[1]
                        result = delete_user(id, HOST, USER, PASSWORD, DB_NAME)
                        logs_text += f"{result}"
                    else:
                        logs_text += "Неправильная команда для удаления пользователя\n"
                elif command == "--HELP" or command == "--h":
                    logs_text += "CREATE TABLE: создает новую таблицу\n" \
                                 "USE: выбирает базу данных для работы\n" \
                                 "SHOW DATABASES: отображает список всех баз данных\n" \
                                 "SHOW TABLES: отображает список всех таблиц в текущей базе данных\n" \
                                 "DESCRIBE: отображает структуру таблицы\n" \
                                 "SELECT: выбирает данные из таблицы\n" \
                                 "INSERT: вставляет новые данные в таблицу\n" \
                                 "UPDATE: обновляет существующие данные в таблице\n" \
                                 "DELETE: удаляет данные из таблицы\n" \
                                 "ALTER TABLE: изменяет структуру таблицы\n" \
                                 "DROP DATABASE: удаляет базу данных\n" \
                                 "DROP TABLE: удаляет таблицу\n"
                elif command == 'CLEAR' or command == 'cls' or command == 'CLS' or command == 'clear':
                    logs_text = ""
                else:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(command)
                            answer = cursor.fetchall()
                            if not answer:
                                logs_text += "Empty\n"
                            elif answer:
                                logs_text += f"{answer}\n"
                            connection.commit()
                    except Exception as ex:
                        logs_text += f"Error in command SQL - {ex}\n"

            label_logs.value = logs_text
            label_logs.update()
            command_field.focus()

    def info(e):
        global logs_text

        logs_text += ">>> INFO\n" \
                     'DEL USER --id "id_user" - Удаление пользователя по id\n' \
                     'DEL USER --n "name_user" - Удаление пользователя по имени\n' \
                     "RESET DATA --v - Сброс данных без подтверждения кодов\n" \
                     "RESET DATA --r {CODE_1}; {CODE_2} - Сброс данных с подтверждением кодов\n" \
                     "--HELP / --h - Список команд\n" \
                     "OTHER MYSQL COMMANDS - Все остальные команды MySQL\n"

        label_logs.value = logs_text
        label_logs.update()

    def exiting(e):
        def yes_exit(e):
            page.window_destroy()

        def no_exit(e):
            confirm_exit_dialog.open = False
            page.update()

        confirm_exit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Подтвердите выход"),
            content=ft.Text("Вы действительно хотите выйти?"),
            actions=[
                ft.ElevatedButton(on_click=no_exit, bgcolor=color_2,
                                  content=ft.Text("Остаться", color=color_3, size=18)),
                ft.ElevatedButton(on_click=yes_exit, bgcolor=error_color_1,
                                  content=ft.Text("Выйти", color=error_color_2, size=18))
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.dialog = confirm_exit_dialog
        confirm_exit_dialog.open = True
        page.update()

    def reset(e):
        global logs_text

        result = reset_data(CODE_1, CODE_2, False, connection)
        time.sleep(1)
        logs_text += f">>> RESET DATA\n{result}"

        label_logs.value = logs_text
        label_logs.update()

    def main(e):
        page.clean()
        page.add(
            ft.Row([
                ft.Container(
                    content=
                    ft.Column([
                        ft.Row([
                            ft.Container(
                                content=label_logs,
                                width=100000,
                            )
                        ], scroll=ft.ScrollMode.ALWAYS),
                    ], scroll=ft.ScrollMode.ALWAYS),
                    width=770, height=520, bgcolor=color_2, border_radius=10, padding=10,
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                command_field,
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(
                width=770,
                content=ft.Row([
                    ft.IconButton(icon="INFO", icon_size=40, on_click=info, icon_color=color_3),
                    ft.IconButton(icon="SUPERVISED_USER_CIRCLE_OUTLINED", icon_size=40, on_click=users,
                                  icon_color=color_3),
                    ft.IconButton(icon="RESTORE", icon_size=40, on_click=reset, icon_color=color_3),
                    ft.IconButton(icon="EXIT_TO_APP", icon_size=40, on_click=exiting, icon_color=color_3),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
            )

        )

        page.update()

    def users(e):
        def hover_back(e):
            e.control.bgcolor = color_3 if e.data == "true" else color_2
            e.control.content.color = color_2 if e.data == "true" else color_3
            e.control.update()

        data = ft.DataTable(columns=[
                        ft.DataColumn(ft.Text("ID", size=30, color=color_2), numeric=True),
                        ft.DataColumn(ft.Text("Login", size=30, color=color_2)),
                        ft.DataColumn(ft.Text("Email", size=30, color=color_2))])
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Container(
                        width=120, height=60, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                        alignment=ft.alignment.center, on_click=main, on_hover=hover_back,
                        content=ft.Text("Назад", size=30, color=color_3, font_family="Bold"))
                ]),
                ft.Container(
                    width=770,
                    content=ft.Row([data], alignment=ft.MainAxisAlignment.START))
            ], scroll=ft.ScrollMode.ALWAYS))
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, login, email FROM users")
                results = cursor.fetchall()
            for row in results:
                data.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(f'{row["id"]}', color=color_3, font_family="SemiBold", size=22)),
                            ft.DataCell(ft.Text(f'{row["login"]}', color=color_3, font_family="SemiBold", size=22)),
                            ft.DataCell(ft.Text(f'{row["email"]}', color=color_3, font_family="SemiBold", size=22))]))
        except Exception as ex:
            data.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Error")),
                        ft.DataCell(ft.Text("Error")),
                        ft.DataCell(ft.Text("Error"))]))
        page.update()

    with open("misc\\data\\style.json", "r") as f:
        STYLE = js.load(f)

    load_dotenv(find_dotenv())
    HOST = os.getenv("DB_HOST")
    USER = os.getenv("DB_ADMIN_LOGIN")
    PASSWORD = os.getenv("DB_ADMIN_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    CODE_1 = os.getenv("CODE_1")
    CODE_2 = os.getenv("CODE_2")

    connection = pymysql.connect(
        host=HOST,
        port=3306,
        user=USER,
        password=PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

    page.title = "Admin"
    page.window_width = 800
    page.window_height = 700
    page.window_resizable = False
    page.window_center()
    page.window_to_front()
    page.bgcolor = STYLE["colors"]["background"]
    color_1 = STYLE["colors"]["color-1"]
    color_2 = STYLE["colors"]["color-2"]
    color_3 = STYLE["colors"]["color-3"]
    error_color_1 = "#CA5555"
    error_color_2 = "#943939"
    page.theme = ft.theme.Theme(color_scheme=ft.ColorScheme(primary=color_2, secondary=color_3))
    page.window_prevent_close = True

    page.fonts = {
        "SemiBold": "misc\\font\\OpenSans-SemiBold.ttf",
        "Bold": "misc\\font\\OpenSans-Bold.ttf",
    }

    logs_text = ""

    command_field = ft.TextField(hint_text="Введите команду", width=770, height=50, border_color=color_3,
                                 focused_border_color=color_1, color=color_1, border_width=3)
    label_logs = ft.Text(logs_text, bgcolor=color_2, color=color_1, size=18)

    kb.on_press(on_enter)
    main(page)


def start(log=False):
    if log:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    ft.app(target=app)


if __name__ == '__main__':
    start()
