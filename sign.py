import asyncio
import flet as ft
import json as js
import re
import random
import socket

import more


async def sign_app(page: ft.Page):

    async def exiting(e):
        async def yes_exit(e):
            await page.window_destroy_async()

        async def no_exit(e):
            confirm_exit_dialog.open = False
            await page.update_async()

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

        if confirm_smena_password_2.open:
            await page.window_destroy_async()
        else:
            page.dialog = confirm_exit_dialog
            confirm_exit_dialog.open = True
            await page.update_async()

    async def yes_smena_password(e):
        async def hover_button_smena(e):
            e.control.bgcolor = color_3 if e.data == "true" else color_2
            e.control.content.color = color_2 if e.data == "true" else color_3
            e.control.update()

        async def smena_password(e):
            user_login.value = ''
            user_password.value = ''
            user_password2.value = ''
            user_email.value = ''
            user_code.value = ''

            await page.clean_async()
            await page.add_async(
                ft.Container(height=46),
                ft.Container(
                    width=page.window_width,
                    content=ft.Column([
                        ft.Row([
                            ft.Text('Смена пароля', font_family="SemiBold", size=45, color=color_1),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=40),
                        ft.Row([
                            user_login
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=24),
                        ft.Row([
                            ft.Container(
                                width=300, height=60, border_radius=50, border=ft.border.all(5, color_3),
                                bgcolor=color_2, alignment=ft.alignment.center,
                                on_hover=hover_button_smena,
                                on_click=smena_password_2,
                                content=ft.Text("Сменить пароль", font_family="Bold", size=25, color=color_3)
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(
                            height=50
                        )
                    ])
                ),
                ft.Container(
                    width=page.window_width, height=60, bgcolor=color_1,
                    padding=ft.padding.all(0), margin=ft.margin.all(0),
                    content=
                    ft.Row([
                        ft.Container(width=70),
                        ft.TextButton(on_click=log_in, content=ft.Text('Авторизация', size=16, color=color_3)),
                        ft.IconButton(icon='logout', width=50, height=50, on_click=exiting, icon_color=color_3),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

            )

        async def smena_password_2(e):
            login = user_login.value

            with connection.cursor() as cursor:
                cursor.execute("SELECT email FROM users WHERE login = %s", (login,))
                data = cursor.fetchone()
                if data:
                    data = data["email"]
                    code_verify = ''.join(random.choices('123456789', k=6))
                    cursor.execute("UPDATE users SET code_verify = %s WHERE login = %s", (code_verify, login))
                    connection.commit()
                    await more.create_email(data, code_verify, login, [background_color, color_1, color_2, color_3])
                    await smena_password_3(e)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Такого пользователя не существует", size=20, color=color_3))
                    page.snack_bar.open = True
                    await page.update_async()

        async def smena_password_3(e):
            await page.clean_async()
            await page.add_async(
                ft.Container(height=46),
                ft.Container(
                    width=page.window_width,
                    content=ft.Column([
                        ft.Row([
                            ft.Text('Смена пароля', font_family="SemiBold", size=45, color=color_1),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=40),
                        ft.Row([
                            user_code
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=24),
                        ft.Row([
                            ft.Container(
                                width=300, height=60, border_radius=50, border=ft.border.all(5, color_3),
                                bgcolor=color_2, alignment=ft.alignment.center,
                                on_hover=hover_button_smena,
                                on_click=smena_password_4,
                                content=ft.Text("Сменить пароль", font_family="Bold", size=25, color=color_3)
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(
                            height=50
                        )
                    ])
                ),
                ft.Container(
                    width=page.window_width, height=60, bgcolor=color_1,
                    padding=ft.padding.all(0), margin=ft.margin.all(0),
                    content=
                    ft.Row([
                        ft.Container(width=70),
                        ft.TextButton(on_click=log_in, content=ft.Text('Авторизация', size=16, color=color_3)),
                        ft.IconButton(icon='logout', width=50, height=50, on_click=exiting, icon_color=color_3),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

            )
            await page.update_async()

        async def smena_password_4(e):
            code = user_code.value
            login = user_login.value
            with connection.cursor() as cursor:
                cursor.execute("SELECT code_verify FROM users WHERE login = %s", (login,))
                data = cursor.fetchone()
                if data:
                    if int(code) == int(data["code_verify"]):
                        await smena_password_5(e)
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("Код неверный", size=20, color=color_3))
                        page.snack_bar.open = True
                        await page.update_async()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Непредвиденная ошибка в данных пользователя", size=20,
                                                         color=color_3))
                    page.snack_bar.open = True
                    await page.update_async()

        async def smena_password_5(e):
            await page.clean_async()
            await page.add_async(
                ft.Container(height=46),
                ft.Container(
                    width=page.window_width,
                    content=ft.Column([
                        ft.Row([
                            ft.Text('Смена пароля', font_family="SemiBold", size=45, color=color_1),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=10),
                        ft.Row([
                            user_password
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            user_password2
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=0),
                        ft.Row([
                            ft.Container(width=300, height=60, border_radius=50, border=ft.border.all(5, color_3),
                                         bgcolor=color_2, alignment=ft.alignment.center, on_hover=hover_button_smena,
                                         on_click=smena_password_6,
                                         content=ft.Text("Сменить пароль", font_family="Bold", size=25, color=color_3)
                                         )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(
                            height=45
                        )
                    ])
                ),
                ft.Container(
                    width=page.window_width, height=60, bgcolor=color_1,
                    padding=ft.padding.all(0), margin=ft.margin.all(0),
                    content=
                    ft.Row([
                        ft.Container(width=70),
                        ft.TextButton(on_click=sign_in, content=ft.Text('Регистрация', size=16, color=color_3)),
                        ft.IconButton(icon='logout', width=50, height=50, on_click=exiting, icon_color=color_3),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            )
            await page.update_async()

        async def smena_password_6(e):
            password = user_password.value
            password2 = user_password2.value
            login = user_login.value

            pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

            if not re.match(pattern, password):
                page.snack_bar = ft.SnackBar(ft.Text('Некорректный пароль'))
                page.snack_bar.open = True
                await page.update_async()
            else:
                if password == password2:
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE users SET password = %s WHERE login = %s", (password, login,))
                        connection.commit()
                        page.snack_bar = ft.SnackBar(ft.Text('Пароль успешно изменен', size=20, color=color_3))
                        page.snack_bar.open = True
                        await page.update_async()
                        await asyncio.sleep(1)
                        await log_in(e)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text('Пароли не совпадают', size=20, color=color_3))
                    page.snack_bar.open = True
                    await page.update_async()

        confirm_smena_password.open = False
        await page.update_async()
        await asyncio.sleep(0.1)
        await smena_password(e)

    async def no_smena_password(e):
        confirm_smena_password.open = False
        await page.update_async()

    async def sign_in(e):
        async def hover_button_signin(e):
            e.control.bgcolor = color_3 if e.data == "true" else color_2
            e.control.content.color = color_2 if e.data == "true" else color_3
            e.control.update()

        async def sign_in_2(e):
            login = user_login.value
            email = user_email.value

            pattern = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'

            error_message = ''

            try:
                with connection.cursor() as cursor:
                    if not re.match(pattern, email):
                        error_message = 'Некорректный email'
                    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                    data = cursor.fetchall()
                    if data:
                        error_message = 'Такой email уже зарегистрирован'

                    if len(login) <= 5:
                        error_message = 'Логин должен быть больше 5 символов'
                    cursor.execute("SELECT id FROM users WHERE login = %s", (login,))
                    data = cursor.fetchall()
                    if data:
                        error_message = "Такой логин уже зарегистрирован"

                    if error_message == '':
                        await sign_in_3(e)
                    else:
                        page.snack_bar = ft.SnackBar(content=ft.Text(error_message, color=color_3, size=20,
                                                                     font_family="Medium"), bgcolor=color_1)
                        page.snack_bar.open = True
                        await page.update_async()
            except Exception as ex:
                print(f'Error in module sign_in_2 - {ex}')

        async def sign_in_3(e):
            global code_verify, count_attempt

            code_verify = ''.join(random.choices('123456789', k=6))
            count_attempt = 0

            await page.clean_async()
            await page.add_async(
                ft.Container(height=46),
                ft.Container(
                    width=page.window_width,
                    content=ft.Column([
                        ft.Row([
                            ft.Text('Регистрация', font_family="SemiBold", size=45, color=color_1),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=40),
                        ft.Row([
                            user_code
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=24),
                        ft.Row([
                            ft.Container(
                                width=300, height=60, border_radius=50, border=ft.border.all(5, color_3),
                                bgcolor=color_2, alignment=ft.alignment.center, on_click=sign_in_4,
                                on_hover=hover_button_signin,
                                content=ft.Text("Отправить", font_family="Bold", size=35, color=color_3)
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(
                            height=50
                        )
                    ])
                ),
                ft.Container(
                    width=page.window_width, height=60, bgcolor=color_1,
                    padding=ft.padding.all(0), margin=ft.margin.only(0, 0, 0, 0),
                    content=
                    ft.Row([
                        ft.Container(width=70),
                        ft.TextButton(on_click=log_in, content=ft.Text('Авторизация', size=16, color=color_3)),
                        ft.IconButton(icon='logout', width=50, height=50, on_click=exiting, icon_size=color_3),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

            )
            await page.update_async()
            await more.create_email(user_email.value, code_verify, user_login.value,
                                    [background_color, color_1, color_2, color_3])

        async def sign_in_4(e):
            global code_verify, count_attempt

            if code_verify != user_code.value:
                page.snack_bar = ft.SnackBar(ft.Text('Код не верный'))
                page.snack_bar.open = True
                await page.update_async()
                count_attempt += 1
            else:
                await sign_in_5(e)
            if count_attempt >= 5:
                await sign_in(e)

        async def sign_in_5(e):

            await page.clean_async()
            await page.add_async(
                ft.Container(height=46),
                ft.Container(
                    width=page.window_width,
                    content=ft.Column([
                        ft.Row([
                            ft.Text('Регистрация', font_family="SemiBold", size=45, color=color_3),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=10),
                        ft.Row([
                            user_password
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            user_password2
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=0),
                        ft.Row([
                            ft.Container(
                                width=300, height=60, bgcolor=color_2, border_radius=50,
                                border=ft.border.all(5, color_3), alignment=ft.alignment.center,
                                on_click=sign_in_6, on_hover=hover_button_signin,
                                content=ft.Text("Зарегистрироваться", font_family="Bold", size=25, color=color_3)
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(
                            height=45
                        )
                    ])
                ),
                ft.Container(
                    width=page.window_width, height=60, bgcolor=color_1,
                    padding=ft.padding.all(0), margin=ft.margin.all(0),
                    content=
                    ft.Row([
                        ft.Container(width=70),
                        ft.TextButton(on_click=log_in, content=ft.Text('Авторизация', size=16, color=color_3)),
                        ft.IconButton(icon='logout', width=50, height=50, on_click=exiting, icon_color=color_3),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

            )
            await page.update_async()

        async def sign_in_6(e):
            password = user_password.value
            password2 = user_password2.value

            pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

            if not re.match(pattern, password):
                page.snack_bar = ft.SnackBar(ft.Text('Некорректный пароль'))
                page.snack_bar.open = True
                await page.update_async()
            else:
                if password == password2:
                    with connection.cursor() as cursor:
                        page.snack_bar = ft.SnackBar(ft.Text('Успешная регистрация'))
                        page.snack_bar.open = True
                        await page.update_async()
                        cursor.execute("SELECT id FROM users ORDER BY id DESC")
                        data = cursor.fetchone()
                        if data is None:
                            user_id = 0
                        else:
                            user_id = int(data["id"]) + 1

                        query = "INSERT INTO users (id, login, email, password) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query, (user_id, user_login.value, user_email.value, password))
                        connection.commit()
                        query = "INSERT INTO data (id, login) VALUES (%s, %s)"
                        cursor.execute(query, (user_id, user_login.value))
                        connection.commit()
                        await asyncio.sleep(1)
                        await log_in(e)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text('Пароли не совпадают'))
                    page.snack_bar.open = True
                    await page.update_async()

        user_login.value = ''
        user_password.value = ''
        user_password2.value = ''
        user_email.value = ''
        user_code.value = ''
        await page.clean_async()
        await page.add_async(
            ft.Container(height=46),
            ft.Container(
                width=page.window_width,
                content=ft.Column([
                    ft.Row([
                        ft.Text('Регистрация', font_family="SemiBold", size=45, color=color_1),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=10),
                    ft.Row([
                        user_login
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        user_email
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=0),
                    ft.Row([
                        ft.Container(
                            width=300, height=60, bgcolor=color_2, border_radius=50, border=ft.border.all(5, color_3),
                            content=ft.Text("Зарегистрироваться", font_family="Bold", size=25, color=color_3),
                            alignment=ft.alignment.center,
                            on_hover=hover_button_signin,
                            on_click=sign_in_2
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(
                        height=45
                    )
                ])
            ),
            ft.Container(
                width=page.window_width, height=60, bgcolor=color_1,
                padding=ft.padding.all(0), margin=ft.margin.only(0, 0, 0, 0),
                content=ft.Row([
                        ft.Container(width=70),
                        ft.Container(
                            content=ft.TextButton(on_click=log_in, content=ft.Text('Авторизация', size=16, color=color_3)),
                        ),
                        ft.IconButton(icon='logout', width=50, height=50, on_click=exiting, icon_color=color_3),


                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )

        )
        await page.update_async()

    async def log_in(e):
        async def log_in_2(e):
            global count_attempt

            login = user_login.value
            password = user_password.value

            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, password FROM users WHERE login = %s", (login,))
                    data = cursor.fetchall()
                    if data:
                        data = data[0]
                        db_password = data["password"]
                        db_id = data["id"]
                        if db_password == password:
                            await log_in_3(e, db_id, login, password)
                        else:
                            page.snack_bar = ft.SnackBar(content=ft.Text("Пароль неверный", color=color_3,
                                                                         size=20, font_family="Medium"), bgcolor=color_1)
                            page.snack_bar.open = True
                            await page.update_async()
                            count_attempt += 1
                            if count_attempt == 5:
                                page.dialog = confirm_smena_password
                                confirm_smena_password.open = True
                                await page.update_async()
                            if count_attempt >= 10:
                                page.dialog = confirm_smena_password_2
                                confirm_smena_password_2.open = True
                                await page.update_async()
                                await asyncio.sleep(300)
                                confirm_smena_password_2.open = False
                                await page.update_async()
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("Такого пользователя не существует", color=color_3,
                                                             size=20, font_family="Medium"), bgcolor=color_1)
                        page.snack_bar.open = True
                        await page.update_async()
            except Exception as ex:
                print(f'Error in module log_in_2 - {ex}')

        async def log_in_3(e, identificator="False", login="False", password="False"):
            if login != "False" and password != "False" and identificator != "False":
                import app

                data = {"id": identificator, "login": login, "password": password}
                with open("misc\\data\\session.json", "w") as f:
                    f.write(js.dumps(data, indent=4))
                await app.main_app(page, int(identificator), login, password)

        async def log_in_local(e):
            try:
                with open("misc\\data\\session.json", "r") as f:
                    session = js.load(f)

                if session:
                    id = session["id"]
                    login = session["login"]
                    password = session["password"]

                    if id != '' and login != '' and password != '':
                        with connection.cursor() as cursor:
                            query = "SELECT id, password FROM users WHERE login = %s"
                            cursor.execute(query, (login,))
                            data = cursor.fetchone()
                        if data and data["password"] == password and data["id"] == id:
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            except Exception as ex:
                print(f"Error in module log_in_local - {ex}")
                return False

        def hover_button_login(e):
            e.control.bgcolor = color_3 if e.data == "true" else color_2
            e.control.content.color = color_2 if e.data == "true" else color_3
            e.control.update()

        global count_attempt, check_signin

        user_login.value = ''
        user_password.value = ''
        user_password2.value = ''
        user_email.value = ''
        user_code.value = ''

        count_attempt = 0

        if await log_in_local(page):
            with open("misc\\data\\session.json", "r") as f:
                session = js.load(f)

            id = session["id"]
            login = session["login"]
            password = session["password"]
            await log_in_3(e, id, login, password)
        else:
            await page.clean_async()
            await page.add_async(
                ft.Container(height=46),
                ft.Container(
                    width=page.window_width,
                    content=ft.Column([
                        ft.Row([
                            ft.Text('Авторизация', size=45, color=color_1, font_family="SemiBold"),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=10),
                        ft.Row([
                            user_login
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            user_password
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=0),
                        ft.Row([
                            ft.Container(width=200, height=60, bgcolor=color_2,
                                         border_radius=50, border=ft.border.all(5, color_3),
                                         content=ft.Text("Войти", size=35, color=color_3, font_family="Bold"),
                                         alignment=ft.alignment.top_center,
                                         on_hover=hover_button_login,
                                         on_click=log_in_2)
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(
                            height=45
                        )
                    ])
                ),
                ft.Container(
                    width=page.window_width, height=60,
                    bgcolor=color_1, padding=ft.padding.all(0), margin=ft.margin.only(0, 0, 0, 0),
                    content=
                    ft.Row([
                        ft.Container(width=70),
                        ft.Container(
                            content=ft.Row([
                                ft.TextButton(on_click=sign_in,
                                              content=ft.Text('Регистрация', size=16, color=color_3)),
                                ft.TextButton(on_click=yes_smena_password,
                                              content=ft.Text('Сменить пароль', size=16,
                                                              color=color_3))
                            ])
                        ),
                        ft.IconButton(icon='logout', width=50, height=50, on_click=exiting, icon_color=color_3),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

            )
            await page.update_async()

    async def check_ethernet(e, status=True):
        try:
            socket.create_connection(("www.google.com", 80))
            if not status:
                return True
            else:
                nonlocal connection

                try:
                    connection = await more.connect_to_db()
                    await log_in(e)
                except:
                    return False
        except OSError:
            if not status:
                return False

    async def no_ethernet(e):
        await page.clean_async()
        await page.add_async(
            ft.Row([
                ft.Icon(ft.icons.WIFI_SHARP, color=error_color_1, size=200)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Text("Нет интернет соединения", size=35, color=color_3)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Text("попробуйте позже или нажмите", size=20, color=color_2)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Container(height=20)
            ]),
            ft.Row([
                ft.ElevatedButton(width=200, height=60, color=error_color_2, bgcolor=error_color_1,
                                  on_click=check_ethernet, content=ft.Text('Повторить', size=20)),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Container(height=90)
            ])
        )

    with open("misc\\data\\style.json", "r") as f:
        STYLE = js.load(f)

    color_1 = STYLE["colors"]["color-1"]
    color_2 = STYLE["colors"]["color-2"]
    color_3 = STYLE["colors"]["color-3"]
    background_color = STYLE["colors"]["background"]
    error_color_1 = "#CA5555"
    error_color_2 = "#943939"

    count_attempt = 0

    confirm_smena_password = ft.AlertDialog(
        modal=True,
        title=ft.Text("Забыли пароль"),
        content=ft.Text("Хотите его сменить?"),
        actions=[
            ft.ElevatedButton(on_click=yes_smena_password, bgcolor=color_2,
                              content=ft.Text("Сменить", color=color_3, size=18)),
            ft.ElevatedButton(on_click=no_smena_password, bgcolor=error_color_1,
                              content=ft.Text("Нет", color=error_color_2, size=18)),

        ],
        actions_alignment=ft.MainAxisAlignment.CENTER)
    confirm_smena_password_2 = ft.AlertDialog(
        modal=True,
        title=ft.Text("Подозрительная активность", color=error_color_1, size=35),
        content=ft.Text("Приложение будет заморожено на 5 минут в целях безопасности пользователей",
                        color=error_color_2, size=20))

    user_login = ft.TextField(hint_text="Логин", width=400, height=50, border_color=color_3, border_width=3,
                              border_radius=10, color=color_1, focused_border_color=color_1)
    user_password = ft.TextField(hint_text="Пароль", width=400, height=50, can_reveal_password=True, password=True,
                                 border_color=color_3, border_width=3, border_radius=10, color=color_1,
                                 focused_border_color=color_1)
    user_password2 = ft.TextField(hint_text="Поторите пароль", width=400, height=50, password=True,
                                  border_color=color_3, border_width=3, border_radius=10, color=color_1,
                                  focused_border_color=color_1)
    user_email = ft.TextField(hint_text="Почта", width=400, height=50, border_color=color_3, border_width=3,
                              border_radius=10, color=color_1, focused_border_color=color_1)
    user_code = ft.TextField(hint_text="Код подтверждения", width=400, height=50, border_color=color_3, border_width=3,
                              border_radius=10, color=color_1, focused_border_color=color_1)

    page.title = "Backup"

    page.fonts = {
        "Medium": "misc\\font\\OpenSans-Medium.ttf",
        "SemiBold": "misc\\font\\OpenSans-SemiBold.ttf",
        "Bold": "misc\\font\\OpenSans-Bold.ttf",
    }

    with open("misc\\data\\style.json", "r") as f:
        js.load(f)

    page.window_width = 800
    page.window_height = 500
    page.window_resizable = False
    await page.window_center_async()
    await page.window_to_front_async()
    page.window_prevent_close = True
    page.padding = ft.padding.all(0)

    page.theme = ft.theme.Theme(color_scheme=ft.ColorScheme(primary=color_2, secondary=color_3))
    page.bgcolor = background_color

    if await check_ethernet(page, False):
        connection = await more.connect_to_db()
        await log_in(page)
    else:
        connection = ''
        await no_ethernet(page)


async def start():
    try:
        await ft.app_async(sign_app)
    except Exception as e:
        print(f'Error in module sign - {e}')


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start())
    finally:
        loop.close()
