import flet as ft
import asyncio
import os
import json
import random
import re
import ast

import more
import refactor


async def main_app(page: ft.Page, identificator: int, login: str, password: str):
    async def exiting(e):
        global color_1, color_2, color_3

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
        page.dialog = confirm_exit_dialog
        confirm_exit_dialog.open = True
        await page.update_async()

    async def slider_change(e):
        value_slider_text.value = int(e.control.value)
        await value_slider_text.update_async()

    async def directory_save(e):
        async def save_file(e):
            path_output = e.path
            if path_output:
                if (path_output[-4::1] == ".zip" or
                        path_output[-3::1] == ".7z" or
                        path_output[-4::1] == ".tar" or
                        path_output[-4::1] == ".rar"):
                    out_path = path_output
                    type_file = path_output[-3::1].upper() if out_path[-4] == '.' else path_output[-2::1]
                    directory_output.value = out_path
                    type_archive_text.value = type_file
                    await type_archive_text.update_async()
                    await directory_output.update_async()
                else:
                    out_path = path_output + '.zip'
                    type_file = "ZIP"
                    directory_output.value = out_path
                    type_archive_text.value = type_file
                    await type_archive_text.update_async()
                    await directory_output.update_async()
            return

        save_context.on_result = save_file
        save_context.save_file(file_name="You Archive.zip", file_type=ft.FilePickerFileType.CUSTOM,
                               allowed_extensions=["zip", "7z", "tar", "rar"],
                               initial_directory=os.path.join(os.getenv('USERPROFILE'), 'Desktop'))
        return

    async def start_backup(e):
        preset = profiles_module.value
        output = directory_output.value
        type = type_archive_text.value
        compression = value_slider_text.value
        password_check = status_password_check.value
        password_user = password if password_check else ""

        if not preset or len(type) > 3 or output == "Directory":
            return

        data_in = DATA[preset]["files"]
        data_out = DATA[preset]["ignore"]

        await more.start_backup(data_in, output, type, compression, password_user, data_out)

        with connection.cursor() as cursor:
            from datetime import date as dt
            name_backup = output.split("/")[-1]
            cursor.execute("INSERT INTO history VALUES (%s, %s, %s, %s, %s)",
                           (int(identificator), str(login), str(dt.today()), str(preset), str(name_backup)))
            connection.commit()

    async def check_user(e):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT login, password FROM users WHERE id = %s", (identificator,))
                data = cursor.fetchone()
                if data:
                    user_login = data["login"]
                    user_password = data["password"]
                    if login == user_login and password == user_password:
                        return True
                    else:
                        return False
                else:
                    return False
        except:
            return False

    async def check_version(e):
        def check_version_program():

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM programs_data ORDER BY id DESC")
                server_version = cursor.fetchone()
            current_version = more.check_version()

            server_version_parts = server_version["version"].split("-")
            current_version_parts = current_version["version"].split("-")

            if float(server_version_parts[0]) > float(current_version_parts[0]):
                result = True
                update_info = ast.literal_eval(server_version['info'])
                actual_version = server_version['version']
                actual_date = server_version['date']
                your_version = current_version['version']
                your_date = current_version['date']

                return result, actual_version, actual_date, your_version, your_date, update_info
            elif float(server_version_parts[0]) < float(current_version_parts[0]):
                return False
            elif float(server_version_parts[0]) == float(current_version_parts[0]):
                labels_order = ["stable", "beta", "alpha", "developer"]
                server_label = server_version_parts[1].lower()
                current_label = current_version_parts[1].lower()
                if labels_order.index(server_label) < labels_order.index(current_label):
                    result = True
                    update_info = ast.literal_eval(server_version['info'])
                    actual_version = server_version['version']
                    actual_date = server_version['date']
                    your_version = current_version['version']
                    your_date = current_version['date']

                    return result, actual_version, actual_date, your_version, your_date, update_info
                elif labels_order.index(server_label) > labels_order.index(current_label):
                    return False
                elif labels_order.index(server_label) == labels_order.index(current_label):
                    return False

            return False

        def no_update(e):
            confirm_update_dialog.open = False
            page.update()

        def yes_update(e):
            import webbrowser as wb

            wb.open("https://github.com/Kkleytt/BackApp", new=2, autoraise=True)
            confirm_update_dialog.open = False
            page.update()

        result, actual_version, actual_date, your_version, your_date, update_info = check_version_program()
        if result:
            text2 = f"Актуальная версия: {actual_version} " \
                   f"дата выхода: {actual_date}\nНынящняя версия: {your_version}\nИзменения:\n"
            for item in update_info:
                text2 += f"● {item}\n"

            confirm_update_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Вышла новая версия"),
                content=
                ft.Container(
                    height=300, content=
                    ft.Column([
                        ft.Text("Краткая информация об обновлении:", size=20),
                        ft.Text(text2),
                    ]),
                ),
                actions=[
                    ft.ElevatedButton(on_click=yes_update, bgcolor=color_2,
                                      content=ft.Text("Обновить", color=color_3, size=18)),
                    ft.ElevatedButton(on_click=no_update, bgcolor=error_color_1,
                                      content=ft.Text("Пропустить", color=error_color_2, size=18))
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )
            page.dialog = confirm_update_dialog
            confirm_update_dialog.open = True
            await page.update_async()

    async def user_profile(e):
        async def hover_button(e):
            e.control.bgcolor = color_3 if e.data == "true" else color_2
            e.control.content.color = color_2 if e.data == "true" else color_3
            e.control.update()

        async def hover_button_error(e):
            e.control.bgcolor = error_color_2 if e.data == "true" else error_color_1
            e.control.content.color = error_color_1 if e.data == "true" else error_color_2
            e.control.update()

        async def exit_app(e):
            async def no_exit(e):
                confirm_exit_dialog.open = False
                await page.update_async()

            async def yes_exit(e):
                import sign

                confirm_exit_dialog.open = False
                await page.update_async()
                await asyncio.sleep(0.2)
                try:
                    os.remove("misc\\data\\session.json")
                except:
                    pass
                try:
                    os.remove("misc\\data\\data.json")
                except:
                    pass
                await sign.sign_app(page)

            confirm_exit_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Подтвердите выход"),
                content=ft.Text("Вы действительно хотите выйти из аккаунта?"),
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
            await page.update_async()

        async def delete_account(e):
            async def no_delete(e):
                confirm_dialog.open = False
                await page.update_async()

            async def yes_delete(e):
                async def yes_delete_2(e):
                    if confirm_dialog_2.content.value == password:
                        confirm_dialog.open = False
                        await confirm_dialog.update_async()
                        with connection.cursor() as cursor:
                            try:
                                import sign

                                id = int(identificator)
                                cursor.execute("DELETE FROM users WHERE id = %s", (id,))
                                connection.commit()
                                await page.update_async()

                                await asyncio.sleep(0.2)
                                os.remove("misc\\data\\session.json")
                                await sign.sign_app(page)
                            except Exception as ex:
                                error = ft.SnackBar(
                                    width=1100, bgcolor=color_1,
                                    content=ft.Container(width=1110, height=67, bgcolor=color_1,
                                                         content=ft.Text('Ошибка удаления аккаунта, попробуйте позже',
                                                                         color=error_color_2, size=30)))
                                error.open = True
                                page.dialog = error
                                await error.update_async()
                                await asyncio.sleep(0.2)
                                error.open = False
                                await error.update_async()
                    else:
                        confirm_dialog_2.content.value = "Неверный пароль"
                        await confirm_dialog_2.update_async()

                async def no_delete_2(e):
                    confirm_dialog_2.open = False
                    await page.update_async()

                confirm_dialog.open = False
                await asyncio.sleep(0.2)
                confirm_dialog_2 = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Для подтверждения введит пароль от аккаунта"),
                    content=ft.TextField(hint_text="Пароль", border_color=color_3, border_width=3,
                                         border_radius=10, color=color_1, focused_border_color=color_1),
                    actions=[
                        ft.ElevatedButton(on_click=no_delete_2, bgcolor=color_2,
                                          content=ft.Text("Отмена", color=color_3, size=18)),
                        ft.ElevatedButton(on_click=yes_delete_2, bgcolor=error_color_1,
                                          content=ft.Text("Продолжить", color=error_color_2, size=18))
                    ],
                    actions_alignment=ft.MainAxisAlignment.CENTER,
                )
                page.dialog = confirm_dialog_2
                confirm_dialog_2.open = True
                await page.update_async()

            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Вы уверены что хотите удалить аккаунт?"),
                content=ft.Text("Все ваши личные данные будут потеряны без возможности восстановления"),
                actions=[
                    ft.ElevatedButton(on_click=no_delete, bgcolor=color_2,
                                      content=ft.Text("Отмена", color=color_3, size=18)),
                    ft.ElevatedButton(on_click=yes_delete, bgcolor=error_color_1,
                                      content=ft.Text("Удалить", color=error_color_2, size=18))
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            await page.update_async()

        async def reset_account(e):
            async def no_reset(e):
                confirm_dialog.open = False
                await page.update_async()

            async def yes_reset(e):
                async def no_reset_2(e):
                    confirm_dialog_2.open = False
                    await page.update_async()

                async def yes_reset_2(e):
                    print(password)
                    print(confirm_dialog_2.content.value)
                    if confirm_dialog_2.content.value == password:
                        try:
                            try:
                                os.remove("misc\\data\\data.json")
                            except:
                                pass
                            with connection.cursor() as cursor:
                                cursor.execute("UPDATE data SET dirs=%s WHERE id=%s", (None, identificator))
                                connection.commit()
                                cursor.execute("UPDATE users SET logo=%s WHERE id=%s", (None, identificator))
                                connection.commit()
                            bs = ft.SnackBar(
                                width=1100, bgcolor=color_1,
                                content=ft.Container(width=1110, height=67, bgcolor=color_1,
                                                     content=ft.Text('Ваш аккаунт был сброшен до заводских настроек',
                                                                     color=color_3, size=30)))
                        except:
                            bs = ft.SnackBar(
                                width=1100, bgcolor=color_1,
                                content=ft.Container(width=1110, height=67, bgcolor=color_1,
                                                     content=ft.Text('Произошла ошибка, попробуйте позже',
                                                                     color=color_3, size=30)))

                        confirm_dialog_2.open = False
                        await confirm_dialog_2.update_async()
                        await asyncio.sleep(0.2)
                        bs.open = True
                        page.dialog = bs
                        await page.update_async()
                    else:
                        confirm_dialog_2.content.value = "Неверный пароль"
                        await confirm_dialog_2.update_async()

                confirm_dialog.open = False
                await asyncio.sleep(0.2)
                confirm_dialog_2 = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Для подтверждения введите пароль от аккаунта"),
                    content=ft.TextField(hint_text="Пароль", border_color=color_3, border_width=3,
                                         border_radius=10, color=color_1, focused_border_color=color_1),
                    actions=[
                        ft.ElevatedButton(on_click=no_reset_2, bgcolor=color_2,
                                          content=ft.Text("Отмена", color=color_3, size=18)),
                        ft.ElevatedButton(on_click=yes_reset_2, bgcolor=error_color_1,
                                          content=ft.Text("Сбросить", color=error_color_2, size=18))
                    ],
                    actions_alignment=ft.MainAxisAlignment.CENTER,
                )
                page.dialog = confirm_dialog_2
                confirm_dialog_2.open = True
                await page.update_async()
            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Вы уверены что хотите сбросить данные?"),
                content=ft.Text("Все ваши личные данные будут потеряны без возможности восстановления"),
                actions=[
                    ft.ElevatedButton(on_click=no_reset, bgcolor=color_2,
                                      content=ft.Text("Отмена", color=color_3, size=18)),
                    ft.ElevatedButton(on_click=yes_reset, bgcolor=error_color_1,
                                      content=ft.Text("Сбросить", color=error_color_2, size=18))
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            await page.update_async()

        async def smena_password(e):
            async def hover_button(e):
                e.control.bgcolor = color_3 if e.data == "true" else color_2
                e.control.content.color = color_2 if e.data == "true" else color_3
                e.control.update()

            async def smena_password_2(e):
                try:
                    if int(user_code.value) == int(code_verify):
                        user_code.password = True
                        user_code.value = ""
                        user_code.hint_text = "Новый пароль"

                        await page.clean_async()
                        await page.add_async(
                            ft.Container(height=130),
                            ft.Container(
                                width=page.window_width,
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text('Смена пароля', font_family="SemiBold", size=50, color=color_1),
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                    ft.Container(height=50),
                                    ft.Row([
                                        user_code
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                    ft.Row([
                                        ft.Container(
                                            width=400, height=80, border_radius=50, border=ft.border.all(5, color_3),
                                            bgcolor=color_2, alignment=ft.alignment.center,
                                            on_hover=hover_button,
                                            on_click=smena_password_3,
                                            content=ft.Text("Сменить пароль", font_family="Bold", size=30, color=color_3)
                                        )
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                    ft.Container(
                                        height=98
                                    )
                                ])
                            ),
                            ft.Container(
                                width=page.window_width, height=95, bgcolor=color_1,
                                padding=ft.padding.all(0), margin=ft.margin.all(0),
                                content=
                                ft.Row([
                                    ft.Container(width=40),
                                    ft.Container(
                                        width=80, height=80, bgcolor=color_2, border_radius=20,
                                        border=ft.border.all(5, color_3),
                                        on_click=main_menu, on_hover=hover_button,
                                        content=ft.Icon(name="ARROW_BACK", size=50, color=color_3)
                                    ),
                                    ft.Container(width=804),
                                    ft.Container(
                                        width=80, height=80, bgcolor=color_2, border_radius=20,
                                        border=ft.border.all(5, color_3),
                                        on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                                        content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                                    ),
                                ])
                            )

                        )
                    else:
                        user_code.value = "Неправильный код"
                        await user_code.update_async()
                except:
                    user_code.value = "Неправильный код"
                    await user_code.update_async()

            async def smena_password_3(e):
                pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
                new_password = user_code.value
                if not re.match(pattern, new_password):
                    page.snack_bar = ft.SnackBar(width=1100, bgcolor=color_1,
                                                 content=ft.Container(width=1110, height=67, bgcolor=color_1,
                                                                      content=ft.Text('Некорректный пароль',
                                                                                      color=color_3, size=30)))
                    page.snack_bar.open = True
                    await page.update_async()
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE users SET password = %s WHERE login = %s", (new_password, login,))
                        connection.commit()
                        page.snack_bar = ft.SnackBar(width=1100, bgcolor=color_1,
                                                     content=ft.Container(width=1110, height=67, bgcolor=color_1,
                                                                          content=ft.Text('Пароль успешно изменен',
                                                                                          color=color_3, size=30)))
                        page.snack_bar.open = True
                        await page.update_async()
                        with open("misc\\data\\session.json", "r", encoding="utf-8") as f:
                            old_data = json.load(f)
                        old_data["password"] = new_password
                        with open("misc\\data\\session.json", "w", encoding="utf-8") as f:
                            json.dump(old_data, f, ensure_ascii=False, indent=4)
                        await user_profile(page)

            data = USER_DATA["email"]
            code_verify = ''.join(random.choices('123456789', k=6))
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET code_verify = %s WHERE login = %s", (code_verify, login))
                connection.commit()
            await more.create_email(data, code_verify, login, [background_color, color_1, color_2, color_3])

            user_code = ft.TextField(hint_text="Код подтверждения", width=500, height=100, border_color=color_3,
                                     border_width=5, text_size=30, text_align=ft.TextAlign.CENTER,
                                     border_radius=30, color=color_1, focused_border_color=color_1)

            await page.clean_async()
            await page.add_async(
                ft.Container(height=130),
                ft.Container(
                    width=page.window_width,
                    content=ft.Column([
                        ft.Row([
                            ft.Text('Смена пароля', font_family="SemiBold", size=50, color=color_1),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=50),
                        ft.Row([
                            user_code
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            ft.Container(
                                width=400, height=80, border_radius=50, border=ft.border.all(5, color_3),
                                bgcolor=color_2, alignment=ft.alignment.center,
                                on_hover=hover_button,
                                on_click=smena_password_2,
                                content=ft.Text("Отправить код", font_family="Bold", size=30, color=color_3)
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(
                            height=98
                        )
                    ])
                ),
                ft.Container(
                    width=page.window_width, height=95, bgcolor=color_1,
                    padding=ft.padding.all(0), margin=ft.margin.all(0),
                    content=
                    ft.Row([
                        ft.Container(width=40),
                        ft.Container(
                            width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                            on_click=main_menu, on_hover=hover_button,
                            content=ft.Icon(name="ARROW_BACK", size=50, color=color_3)
                        ),
                        ft.Container(width=804),
                        ft.Container(
                            width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                            on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                            content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                        ),
                    ])
                )

            )

        async def smena_email(e):
            async def hover_button(e):
                e.control.bgcolor = color_3 if e.data == "true" else color_2
                e.control.content.color = color_2 if e.data == "true" else color_3
                e.control.update()

            async def smena_email_2(e):
                if int(user_code.value) == int(code_verify):
                    user_code.value = ""
                    user_code.hint_text = "Новая почта"

                    await page.clean_async()
                    await page.add_async(
                        ft.Container(height=130),
                        ft.Container(
                            width=page.window_width,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text('Смена почты', font_family="SemiBold", size=50, color=color_1),
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Container(height=50),
                                ft.Row([
                                    user_code
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.Container(
                                        width=400, height=80, border_radius=50, border=ft.border.all(5, color_3),
                                        bgcolor=color_2, alignment=ft.alignment.center,
                                        on_hover=hover_button,
                                        on_click=smena_email_3,
                                        content=ft.Text("Получить код", font_family="Bold", size=30, color=color_3)
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Container(
                                    height=98
                                )
                            ])
                        ),
                        ft.Container(
                            width=page.window_width, height=95, bgcolor=color_1,
                            padding=ft.padding.all(0), margin=ft.margin.all(0),
                            content=
                            ft.Row([
                                ft.Container(width=40),
                                ft.Container(
                                    width=80, height=80, bgcolor=color_2, border_radius=20,
                                    border=ft.border.all(5, color_3),
                                    on_click=main_menu, on_hover=hover_button,
                                    content=ft.Icon(name="ARROW_BACK", size=50, color=color_3)
                                ),
                                ft.Container(width=804),
                                ft.Container(
                                    width=80, height=80, bgcolor=color_2, border_radius=20,
                                    border=ft.border.all(5, color_3),
                                    on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                                    content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                                ),
                            ])
                        )

                    )
                else:
                    page.snack_bar = ft.SnackBar(width=1100, bgcolor=color_1,
                                                 content=ft.Container(width=1110, height=67, bgcolor=color_1,
                                                                      content=ft.Text('Неправильный код',
                                                                                      color=color_3, size=30)))
                    page.snack_bar.open = True
                    await page.update_async()

            async def smena_email_3(e):
                global code_verify, new_email

                pattern = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
                new_email = user_code.value

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM users WHERE email = %s", (new_email,))
                    reg_email = cursor.fetchone()

                if re.match(pattern, new_email) and not reg_email:
                    code_verify = ''.join(random.choices('123456789', k=6))
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE users SET code_verify = %s WHERE login = %s", (code_verify, login))
                        connection.commit()
                    await more.create_email(new_email, code_verify, login, [background_color, color_1, color_2, color_3])

                    user_code.value = ""
                    user_code.hint_text = "Код подтверждения"

                    await page.clean_async()
                    await page.add_async(
                        ft.Container(height=130),
                        ft.Container(
                            width=page.window_width,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text('Смена почты', font_family="SemiBold", size=50, color=color_1),
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Container(height=50),
                                ft.Row([
                                    user_code
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.Container(
                                        width=400, height=80, border_radius=50, border=ft.border.all(5, color_3),
                                        bgcolor=color_2, alignment=ft.alignment.center,
                                        on_hover=hover_button,
                                        on_click=smena_email_4,
                                        content=ft.Text("Отправить код", font_family="Bold", size=30, color=color_3)
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Container(
                                    height=98
                                )
                            ])
                        ),
                        ft.Container(
                            width=page.window_width, height=95, bgcolor=color_1,
                            padding=ft.padding.all(0), margin=ft.margin.all(0),
                            content=
                            ft.Row([
                                ft.Container(width=40),
                                ft.Container(
                                    width=80, height=80, bgcolor=color_2, border_radius=20,
                                    border=ft.border.all(5, color_3),
                                    on_click=main_menu, on_hover=hover_button,
                                    content=ft.Icon(name="ARROW_BACK", size=50, color=color_3)
                                ),
                                ft.Container(width=804),
                                ft.Container(
                                    width=80, height=80, bgcolor=color_2, border_radius=20,
                                    border=ft.border.all(5, color_3),
                                    on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                                    content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                                ),
                            ])
                        )

                    )
                else:
                    page.snack_bar = ft.SnackBar(width=1100, bgcolor=color_1,
                                                 content=ft.Container(width=1110, height=67, bgcolor=color_1,
                                                                      content=ft.Text('Неккоректный email',
                                                                                      color=color_3, size=30)))
                    page.snack_bar.open = True
                    await page.update_async()

            async def smena_email_4(e):
                global code_verify, new_email

                if int(code_verify) == int(user_code.value):
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE users SET email = %s WHERE login = %s", (new_email, login))
                        connection.commit()
                    page.snack_bar = ft.SnackBar(width=1100, bgcolor=color_1,
                                                 content=ft.Container(width=1110, height=67, bgcolor=color_1,
                                                                      content=ft.Text('Почта успешно изменена',
                                                                                      color=color_3, size=30)))
                    page.snack_bar.open = True
                    await page.update_async()
                    await user_profile(page)
                else:
                    page.snack_bar = ft.SnackBar(width=1100, bgcolor=color_1,
                                                 content=ft.Container(width=1110, height=67, bgcolor=color_1,
                                                                      content=ft.Text('Неправильный код',
                                                                                      color=color_3, size=30)))
                    page.snack_bar.open = True
                    await page.update_async()

            data = USER_DATA["email"]
            code_verify = ''.join(random.choices('123456789', k=6))
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET code_verify = %s WHERE login = %s", (code_verify, login))
                connection.commit()
            await more.create_email(data, code_verify, login, [background_color, color_1, color_2, color_3])

            user_code = ft.TextField(hint_text="Код подтверждения", width=500, height=100, border_color=color_3,
                                     border_width=5, text_size=30, text_align=ft.TextAlign.CENTER,
                                     border_radius=30, color=color_1, focused_border_color=color_1)

            await page.clean_async()
            await page.add_async(
                ft.Container(height=130),
                ft.Container(
                    width=page.window_width,
                    content=ft.Column([
                        ft.Row([
                            ft.Text('Смена почты', font_family="SemiBold", size=50, color=color_1),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=50),
                        ft.Row([
                            user_code
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            ft.Container(
                                width=400, height=80, border_radius=50, border=ft.border.all(5, color_3),
                                bgcolor=color_2, alignment=ft.alignment.center,
                                on_hover=hover_button,
                                on_click=smena_email_2,
                                content=ft.Text("Отправить код", font_family="Bold", size=30, color=color_3)
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(
                            height=98
                        )
                    ])
                ),
                ft.Container(
                    width=page.window_width, height=95, bgcolor=color_1,
                    padding=ft.padding.all(0), margin=ft.margin.all(0),
                    content=
                    ft.Row([
                        ft.Container(width=40),
                        ft.Container(
                            width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                            on_click=main_menu, on_hover=hover_button,
                            content=ft.Icon(name="ARROW_BACK", size=50, color=color_3)
                        ),
                        ft.Container(width=804),
                        ft.Container(
                            width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                            on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                            content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                        ),
                    ])
                )

            )

        async def pick_logo(e):
            async def pick_logo_result(e):
                path = ", ".join(map(lambda f: f.path, e.files)) if e.files else "Cancelled!"
                user_images_dialog.src = path
                await user_images_dialog.update_async()
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE users SET logo = %s WHERE id = %s", (path, identificator))
                        connection.commit()
                except:
                    pass

            pick_files_dialog.on_result = pick_logo_result
            await pick_files_dialog.pick_files_async(file_type=ft.FilePickerFileType.CUSTOM,
                                                     allow_multiple=False,
                                                     allowed_extensions=["png", "jpg", "jpeg"],
                                                     initial_directory=os.path.join(os.getenv('USERPROFILE'), 'Pictures'))

        global color_1, color_2, color_3, error_color_1, error_color_2
        global user_images_dialog

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT date, presset, output FROM history WHERE id = %s", (identificator,))
                history_data = cursor.fetchall()
                history_text = ""
                for item in history_data:
                    history_text += f">>>{item['date']}: {item['presset']} to\n '{item['output']}'\n"
                if history_text == "":
                    history_text = "Вы еще ни разу не воспользовались архиватором"
        except:
            history_text = "Ошибка при получении данных"

        await page.clean_async()
        await page.add_async(
            ft.Container(height=30),
            ft.Row([
                ft.Container(width=42.75),
                ft.Container(width=120, height=120, bgcolor=color_1, border_radius=60,
                             on_click=pick_logo,
                             border=ft.border.all(5, color_3),
                             content=user_images_dialog),
                ft.Container(height=120, width=860, bgcolor=color_2, border_radius=60,
                             border=ft.border.all(5, color_3),alignment=ft.alignment.center,
                             content=ft.Text(USER_DATA["login"], color=color_3, size=60, font_family="Bold")),
            ]),
            ft.Container(height=10),
            ft.Row([
                ft.Container(width=42.75),
                ft.Container(width=470, height=360, content=
                                ft.Column([
                                    ft.Container(width=470, height=75, bgcolor=color_2, border_radius=40,
                                                 border=ft.border.all(5, color_3), alignment=ft.alignment.center,
                                                 on_hover=hover_button, on_click=smena_password,
                                                 content=ft.Text("Сменить пароль", color=color_3, size=30,
                                                                 font_family="SemiBold")),
                                    ft.Container(width=470, height=75, bgcolor=color_2, border_radius=40,
                                                 border=ft.border.all(5, color_3), alignment=ft.alignment.center,
                                                 on_hover=hover_button, on_click=smena_email,
                                                 margin=ft.margin.only(0, 10, 0, 0),
                                                 content=ft.Text("Сменить почту", color=color_3, size=30,
                                                                 font_family="SemiBold")),
                                    ft.Container(width=470, height=75, bgcolor=color_2, border_radius=40,
                                                 border=ft.border.all(5, color_3), alignment=ft.alignment.center,
                                                 on_hover=hover_button, on_click=reset_account,
                                                 margin=ft.margin.only(0, 10, 0, 0),
                                                 content=ft.Text("Сбросить данные", color=color_3, size=30,
                                                                 font_family="SemiBold")),
                                    ft.Container(width=470, height=75, alignment=ft.alignment.center,
                                                 margin=ft.margin.only(0, 10, 0, 0),
                                                 content=ft.Row([
                                                     ft.Container(width=385, height=75, bgcolor=color_2,
                                                                  border_radius=40,
                                                                  border=ft.border.all(5, color_3),
                                                                  alignment=ft.alignment.center,
                                                                  on_hover=hover_button,
                                                                  on_click=exit_app,
                                                                  content=ft.Text("Выйти", color=color_3, size=30,
                                                                                  font_family="SemiBold")),
                                                     ft.Container(width=75, height=75, bgcolor=error_color_1,
                                                                  border_radius=40,
                                                                  border=ft.border.all(5, error_color_2),
                                                                  alignment=ft.alignment.center,
                                                                  on_hover=hover_button_error,
                                                                  on_click=delete_account,
                                                                  content=ft.Icon('DELETE_OUTLINED', color=error_color_2,
                                                                                  size=45))

                                                 ])),

                                ], alignment=ft.MainAxisAlignment.START)),
                ft.Container(width=42.75),
                ft.Container(width=450, height=360, bgcolor=color_1, border_radius=30,
                             border=ft.border.all(5, color_3),
                             content=ft.Column([
                                 ft.Container(
                                     width=450, height=65, bgcolor=color_2, alignment=ft.alignment.center,
                                     border_radius=ft.border_radius.only(26, 26, 0, 0),
                                     content=ft.Text("История", color=color_3, size=40, font_family="Bold")),
                                 ft.Container(
                                     width=450, height=280,
                                     content=
                                     ft.Column([
                                         ft.Container(
                                             padding=ft.padding.only(10, 0, 5, 0),
                                             content=
                                             ft.Text(history_text, color=color_3, size=20, font_family="SemiBold")
                                         )
                                     ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.AUTO),
                                 )

                             ])
                             )
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=20),
            ft.Container(
                width=1110, height=95, bgcolor=color_1,
                content=ft.Row([
                    ft.Container(width=40),
                    ft.Container(
                        width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                        on_click=main_menu, on_hover=hover_button,
                        content=ft.Icon(name="ARROW_BACK", size=50, color=color_3)
                    ),
                    ft.Container(width=804),
                    ft.Container(
                        width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                        on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                        content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                    ),
                ])
            )
        )

    async def instruction(e):
        global color_1, color_2, color_3

        async def hover_button(e):
            e.control.bgcolor = color_3 if e.data == "true" else color_2
            e.control.content.color = color_2 if e.data == "true" else color_3
            e.control.update()

        try:
            with open("misc\\data\\instruction.json", "r", encoding="utf-8") as file:
                TEXT = json.load(file)
        except:
            TEXT["text1"] = "Произошла ошибка при загрузке данных, возможно вы случайно удалили один или " \
                            "несколько системных файлов."
            TEXT["text2"] = ""
            TEXT["text3"] = ""
            TEXT["text4"] = ""
            TEXT["text5"] = ""
            TEXT["text6"] = ""
            TEXT["text7"] = ""
            TEXT["text8"] = ""
            TEXT["text9"] = ""
            TEXT["text10"] = ""
            TEXT["text11"] = ""
            TEXT["text12"] = ""
            TEXT["text13"] = ""
            TEXT["text14"] = ""
            TEXT["text15"] = ""

        await page.clean_async()
        await page.add_async(
            ft.Container(height=30),
            ft.Row([
                ft.Container(width=42.75),
                ft.Container(
                    width=985, height=520, bgcolor=color_1, border_radius=50, border=ft.border.all(5, color_3),
                    padding=ft.padding.all(0),
                    content=ft.Column([
                        ft.Container(bgcolor=color_2, width=985, height=80,
                                     border_radius=ft.border_radius.only(46, 46, 0, 0),
                                     alignment=ft.alignment.center,
                                     content=ft.Text("Инструкция", color=color_3, size=50, font_family="Bold")),
                        ft.Container(width=985, height=420, padding=ft.padding.only(10, 0, 10, 0),
                                     border_radius=ft.border_radius.only(0, 0, 46, 46),
                                     content=
                                     ft.Column([
                                         ft.Container(width=975, margin=ft.margin.all(0), height=40,
                                                      content=ft.Text(TEXT["text1"], color=color_3, size=20,
                                                                      font_family="SemiBold"),
                                                      ),
                                         ft.Row([
                                             ft.Image(src="misc\\image\\instruction\\image-1.png", width=400,
                                                      height=250),
                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text2"], color=color_3, size=20,
                                                              font_family="SemiBold")
                                                          )

                                         ]),
                                         ft.Row([
                                             ft.Container(width=540, height=290, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text3"], color=color_3, size=20,
                                                              font_family="SemiBold")
                                                          ),
                                             ft.Image(src="misc\\image\\instruction\\image-2.png", width=400,
                                                      height=250)


                                         ]),
                                         ft.Row([
                                             ft.Image(src="misc\\image\\instruction\\image-3.png", width=400,
                                                      height=250),
                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text4"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          )
                                         ]),
                                         ft.Row([
                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text5"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          ),
                                             ft.Image(src="misc\\image\\instruction\\image-4.png", width=380,
                                                      height=250)
                                         ]),
                                         ft.Row([
                                             ft.Image(src="misc\\image\\instruction\\image-5.png", width=380,
                                                      height=250),
                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text6"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          )

                                         ]),
                                         ft.Row([

                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text8"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          ),
                                             ft.Image(src="misc\\image\\instruction\\image-7.png", width=380,
                                                      height=250)

                                         ]),
                                         ft.Row([
                                             ft.Image(src="misc\\image\\instruction\\image-8.png", width=380,
                                                      height=250),
                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text9"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          )
                                         ]),
                                         ft.Row([
                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text10"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          ),
                                             ft.Image(src="misc\\image\\instruction\\image-9.png", width=380,
                                                      height=250)
                                         ]),
                                         ft.Row([
                                             ft.Image(src="misc\\image\\instruction\\image-10.png", width=380,
                                                      height=250),
                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text11"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          )

                                         ]),
                                         ft.Row([
                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text12"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          ),
                                             ft.Image(src="misc\\image\\instruction\\image-11.png", width=380,
                                                      height=250)
                                         ]),
                                         ft.Row([
                                             ft.Image(src="misc\\image\\instruction\\image-12.png", width=380,
                                                      height=250),
                                             ft.Container(width=540, height=280, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text13"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          )

                                         ]),
                                         ft.Row([
                                             ft.Container(width=540, height=250, padding=ft.padding.all(0),
                                                          alignment=ft.alignment.center_left,
                                                          content=
                                                          ft.Text(TEXT["text14"], color=color_3, size=20,
                                                                  font_family="SemiBold")
                                                          ),
                                             ft.Image(src="misc\\image\\instruction\\image-13.png", width=380,
                                                      height=250)
                                         ]),
                                         ft.Container(width=975, margin=ft.margin.all(0), height=200,
                                                      content=ft.Text(TEXT["text15"], color=error_color_1, size=20,
                                                                      font_family="SemiBold"),
                                                      ),

                                     ], scroll=ft.ScrollMode.AUTO)
                                     )
                    ])

                )
            ]),

            ft.Container(height=10),
            ft.Container(
                width=1110, height=95, bgcolor=color_1,
                content=ft.Row([
                    ft.Container(width=40),
                    ft.Container(
                        width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                        on_click=main_menu, on_hover=hover_button,
                        content=ft.Icon(name="ARROW_BACK", size=50, color=color_3)
                    ),
                    ft.Container(width=804),
                    ft.Container(
                        width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                        on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                        content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                    ),
                ])
            )
        )

    async def settings(e):
        global color_1, color_2, color_3, background_color

        async def hover_button(e):
            e.control.bgcolor = color_3 if e.data == "true" else color_2
            e.control.content.color = color_2 if e.data == "true" else color_3
            e.control.update()

        async def change_theme(e):
            global background_color, color_1, color_2, color_3

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM style WHERE name = %s", (e.data,))
                palete = cursor.fetchall()[0]

            background_color = palete["background"]
            color_1 = palete["color1"]
            color_2 = palete["color2"]
            color_3 = palete["color3"]

            page.bgcolor = background_color

            with open("misc\\data\\style.json", "r", encoding='utf-8') as f:
                data = json.load(f)

            data["colors"]["background"] = palete["background"]
            data["colors"]["color-1"] = palete["color1"]
            data["colors"]["color-2"] = palete["color2"]
            data["colors"]["color-3"] = palete["color3"]

            with open("misc\\data\\style.json", "w", encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            theme_lst = []

            for theme in theme_style:
                txt = ft.Container(width=430, height=50, padding=ft.padding.only(20, 0, 20, 0),
                                   content=ft.Row([
                                       ft.Container(
                                           ft.Row([
                                               ft.Radio(value=theme["name"], active_color=palete["color3"],
                                                        fill_color={
                                                            ft.MaterialState.DEFAULT: palete["color2"],
                                                            ft.MaterialState.SELECTED: palete["color3"],
                                                        }),
                                               ft.Text(theme["name"], color=palete["color3"], size=30, font_family="SemiBold"),
                                           ])
                                       ),
                                       ft.Container(
                                           bgcolor=palete["color2"], border_radius=20,
                                           padding=ft.padding.only(10, 10, 10, 10),
                                           content=
                                           ft.Row([
                                               ft.Container(width=20, height=20, border_radius=20,
                                                            bgcolor=theme["background"]),
                                               ft.Container(width=20, height=20, border_radius=20,
                                                            bgcolor=theme["color1"]),
                                               ft.Container(width=20, height=20, border_radius=20,
                                                            bgcolor=theme["color2"]),
                                               ft.Container(width=20, height=20, border_radius=20,
                                                            bgcolor=theme["color3"]),
                                           ])
                                       )


                                   ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                                   )
                theme_lst.append(txt)

            theme_module = ft.RadioGroup(content=ft.Column(controls=theme_lst, scroll=ft.ScrollMode.ALWAYS),
                                         on_change=change_theme)
            theme_module.value = e.data

            await page.clean_async()
            await page.add_async(
                ft.Container(height=30),
                ft.Row([
                    ft.Container(width=42.75),
                    ft.Container(
                        width=450, height=520, bgcolor=color_1, border_radius=50, border=ft.border.all(5, color_3),
                        padding=ft.padding.all(0),
                        content=ft.Column([
                            ft.Container(bgcolor=color_2, width=450, height=80,
                                         border_radius=ft.border_radius.only(46, 46, 0, 0),
                                         alignment=ft.alignment.center,
                                         content=ft.Text("Темы", color=color_3, size=50, font_family="Bold")),
                            ft.Container(bgcolor=color_1, width=450, height=420,
                                         border_radius=ft.border_radius.only(0, 0, 46, 46),
                                         content=
                                         theme_module
                                         )
                        ])

                    )
                ]),
                ft.Container(height=10),
                ft.Container(
                    width=1110, height=95, bgcolor=color_1,
                    content=ft.Row([
                        ft.Container(width=40),
                        ft.Container(
                            width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                            on_click=main_menu, on_hover=hover_button,
                            content=ft.Icon(name="ARROW_BACK", size=50, color=color_3)
                        ),
                        ft.Container(width=804),
                        ft.Container(
                            width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                            on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                            content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                        ),
                    ])
                )
            )

        theme_lst = []

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM style")
            theme_style = cursor.fetchall()
            active_colors = [background_color, color_1, color_2, color_3]

            for theme in theme_style:
                native_colors = [theme["background"], theme["color1"], theme["color2"], theme["color3"]]
                if active_colors == native_colors:
                    activate_theme = theme["name"]

                txt = ft.Container(width=430, height=50, padding=ft.padding.only(20, 0, 20, 0),
                                   content=ft.Row([
                                       ft.Container(
                                           ft.Row([
                                               ft.Radio(value=theme["name"], active_color=color_3,
                                                        fill_color={
                                                            ft.MaterialState.DEFAULT: color_2,
                                                            ft.MaterialState.SELECTED: color_3,
                                                        }),
                                               ft.Text(theme["name"], color=color_3, size=30, font_family="SemiBold"),
                                           ])
                                       ),
                                       ft.Container(
                                           bgcolor=color_2, border_radius=20,
                                           padding=ft.padding.only(10, 10, 10, 10),
                                           content=
                                           ft.Row([
                                               ft.Container(width=20, height=20, border_radius=20,
                                                            bgcolor=theme["background"]),
                                               ft.Container(width=20, height=20, border_radius=20,
                                                            bgcolor=theme["color1"]),
                                               ft.Container(width=20, height=20, border_radius=20,
                                                            bgcolor=theme["color2"]),
                                               ft.Container(width=20, height=20, border_radius=20,
                                                            bgcolor=theme["color3"]),
                                           ])
                                       )


                                   ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                                   )
                theme_lst.append(txt)

        theme_module = ft.RadioGroup(content=ft.Column(controls=theme_lst, scroll=ft.ScrollMode.ALWAYS),
                                     on_change=change_theme)
        theme_module.value = activate_theme

        await page.clean_async()
        await page.add_async(
            ft.Container(height=30),
            ft.Row([
                ft.Container(width=42.75),
                ft.Container(
                    width=450, height=520, bgcolor=color_1, border_radius=50, border=ft.border.all(5, color_3),
                    padding=ft.padding.all(0),
                    content=ft.Column([
                        ft.Container(bgcolor=color_2, width=450, height=80,
                                     border_radius=ft.border_radius.only(46, 46, 0, 0),
                                     alignment=ft.alignment.center,
                                     content=ft.Text("Темы", color=color_3, size=50, font_family="Bold")),
                        ft.Container(bgcolor=color_1, width=450, height=420,
                                     border_radius=ft.border_radius.only(0, 0, 46, 46),
                                     content=
                                     theme_module
                                     )
                    ])

                )
            ]),
            ft.Container(height=10),
            ft.Container(
                width=1110, height=95, bgcolor=color_1,
                content=ft.Row([
                    ft.Container(width=40),
                    ft.Container(
                        width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                        on_click=main_menu, on_hover=hover_button,
                        content=ft.Icon(name="ARROW_BACK", size=50, color=color_3)
                    ),
                    ft.Container(width=804),
                    ft.Container(
                        width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                        on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                        content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                    ),
                ])
            )
        )

    async def main_menu(e):
        async def hover_button(e):
            e.control.bgcolor = color_3 if e.data == "true" else color_2
            e.control.content.color = color_2 if e.data == "true" else color_3
            e.control.update()

        global DATA, USER_DATA
        global directory_output, type_archive_text, save_context
        global value_slider_text, profiles_module, status_password_check
        global bs
        global color_1, color_2, color_3, error_color_1, error_color_2
        global user_images_dialog

        with open("misc\\data\\style.json", "r", encoding='utf-8') as f:
            style = json.load(f)

        color_1 = style["colors"]["color-1"]
        color_2 = style["colors"]["color-2"]
        color_3 = style["colors"]["color-3"]
        error_color_1 = "#CA5555"
        error_color_2 = "#943939"

        page.bgcolor = style["colors"]["background"]

        with connection.cursor() as cursor:
            query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(query, (identificator,))
            USER_DATA = cursor.fetchone()

        user_images_dialog = ft.Image(src=f"{USER_DATA['logo']}", width=120, height=120, border_radius=60,
                                      fit=ft.ImageFit.COVER,
                                      error_content=ft.Container(width=120, height=120, bgcolor=color_2, content=
                                      ft.Icon('ACCOUNT_CIRCLE', color=color_3, size=100)))
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT dirs FROM data WHERE id = %s", (identificator,))
                DATA = cursor.fetchone()
        except:
            with open("misc\\data\\data.json", "r", encoding='utf-8') as f:
                DATA = json.load(f)
        try:
            DATA = json.loads(DATA['dirs'])
            all_presets = DATA["pressets"]
        except:
            DATA = {
                "pressets": []
            }
            all_presets = []

        pressets_lst = []
        index = 0
        profiles_module = ft.RadioGroup(content=ft.Column(controls=pressets_lst, scroll=ft.ScrollMode.ALWAYS))

        for item in all_presets:
            try:
                if index == 0:
                    profiles_module.value = item
                index += 1
                files_lst = DATA[item]['files']
                if files_lst:
                    txt = ft.Container(width=400, height=50, padding=ft.padding.only(20, 0, 0, 0),
                                       content=
                                       ft.Row([
                                           ft.Radio(value=item, active_color=color_3,
                                                    fill_color={
                                                        ft.MaterialState.DEFAULT: color_3,
                                                        ft.MaterialState.SELECTED: color_1,
                                                    }),
                                           ft.Text(item, size=30, color=color_3, font_family="SemiBold")
                                       ]))
                    pressets_lst.append(txt)
            except:
                continue

        value_slider_text = ft.Text("0", size=40, color=color_3, font_family="SemiBold")
        status_password_check = ft.Checkbox(width=30, height=30, active_color=color_3)
        directory_output = ft.Text("Directory", size=30, color=color_3, font_family="SemiBold")
        type_archive_text = ft.Text("Type Archive", size=30, color=color_3, font_family="SemiBold")
        save_context = ft.FilePicker()

        bs = ft.SnackBar(
            width=1100, bgcolor=color_1,
            content=ft.Container(width=1110, height=67, bgcolor=color_1,
                         content=ft.Text('Данная функция будет добавленна позже', color=color_3, size=30))
        )

        await page.clean_async()
        page.overlay.extend([save_context])
        page.overlay.append(bs)

        await page.add_async(
            ft.Container(height=30),
            ft.Row([
                ft.Container(width=42.75),
                ft.Container(
                    width=450, height=500, bgcolor=color_2,
                    border_radius=30,
                    content=ft.Column([
                        ft.Container(
                            bgcolor=color_3, height=64.5,
                            content=ft.Row([
                                ft.Text('Прессеты', size=40, color=color_1, font_family="SemiBold"),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                        ),
                        ft.Container(
                            width=450, height=420,
                            content=
                            ft.Column([
                                profiles_module
                            ], scroll=ft.ScrollMode.AUTO)
                        )


                    ]),
                ),
                ft.Container(width=60),
                ft.Container(
                    width=450, height=500,
                    content=ft.Column([
                        ft.Row([
                            ft.Container(width=80, height=80, border_radius=20,
                                         on_click=settings, on_hover=hover_button,
                                         bgcolor=color_2, border=ft.border.all(5, color_3),
                                         content=ft.Icon(name='SETTINGS', color=color_3, size=45)),
                            ft.Container(width=80, height=80, border_radius=20,
                                         on_click=main_menu, on_hover=hover_button,
                                         bgcolor=color_2, border=ft.border.all(5, color_3),
                                         content=ft.Icon(name='REFRESH', color=color_3, size=45)),
                            ft.Container(width=80, height=80, border_radius=20,
                                         on_click=instruction, on_hover=hover_button,
                                         bgcolor=color_2, border=ft.border.all(5, color_3),
                                         content=ft.Icon(name='INFO_OUTLINED', color=color_3, size=45)),
                            ft.Container(width=80, height=80, border_radius=20,
                                         on_click=refactor.start,
                                         on_hover=hover_button,
                                         bgcolor=color_2, border=ft.border.all(5, color_3),
                                         content=ft.Icon(name='EDIT', color=color_3, size=45)),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(
                            width=450, height=80, bgcolor=color_1, border_radius=20, margin=ft.margin.only(0, 14, 0, 0),
                            padding=ft.padding.only(20, 0, 0, 0),
                            content=ft.Row([
                                type_archive_text,
                                ft.Container(
                                    width=80, height=80, border_radius=20, bgcolor=color_2,
                                    border=ft.border.all(5, color_3),
                                    content=ft.Icon("ATTACH_FILE_SHARP", color=color_3, size=45)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ),
                        ft.Container(
                            width=450, height=80, bgcolor=color_1, border_radius=20, margin=ft.margin.only(0, 14, 0, 0),
                            padding=ft.padding.only(20, 0, 0, 0),
                            content=ft.Row([
                                ft.Container(
                                    width=350,
                                    content=ft.Row([
                                        directory_output
                                    ], scroll=ft.ScrollMode.AUTO)
                                ),
                                ft.Container(
                                    width=80, height=80, border_radius=20, bgcolor=color_2,
                                    border=ft.border.all(5, color_3), on_click=directory_save,
                                    on_hover=hover_button,
                                    content=ft.Icon(name="MORE_HORIZ", color=color_3,
                                                          size=45)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ),
                        ft.Container(
                            width=450, height=80, bgcolor=color_1, border_radius=20, margin=ft.margin.only(0, 14, 0, 0),
                            content=ft.Row([
                                ft.Slider(min=0, max=10, divisions=10, width=360,
                                          inactive_color=color_2, active_color=color_3,
                                          on_change=slider_change, value=0),
                                ft.Container(
                                    width=80, height=80, border_radius=20, bgcolor=color_2,
                                    border=ft.border.all(5, color_3),
                                    alignment=ft.alignment.Alignment(0, 0),
                                    content=value_slider_text
                                )

                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ),
                        ft.Container(
                            width=450, height=80, bgcolor=color_1, border_radius=20, margin=ft.margin.only(0, 14, 0, 0),
                            padding=ft.padding.only(20, 0, 0, 0),
                            content=ft.Row([
                                ft.Text("Add Password", size=30, color=color_3, font_family="SemiBold"),
                                ft.Container(
                                    width=80, height=80, border_radius=20, bgcolor=color_2,
                                    border=ft.border.all(5, color_3),
                                    content=ft.Container(
                                        width=80, height=80, border_radius=20,
                                        content=status_password_check
                                    )

                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ),
                    ])

                )
            ]),
            ft.Container(height=30),
            ft.Container(
                width=1110, height=95, bgcolor=color_1,
                content=ft.Row([
                    ft.Container(width=40),
                    ft.Container(
                        width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                        on_click=user_profile,  on_hover=hover_button,
                        content=ft.Icon(name="MANAGE_ACCOUNTS", size=50, color=color_3)
                    ),
                    ft.Container(width=292),
                    ft.Container(
                        width=200, height=80, bgcolor=color_2, border_radius=25, border=ft.border.all(5, color_3),
                        alignment=ft.alignment.Alignment(0, 0), on_click=start_backup,  on_hover=hover_button,
                        content=ft.Text("START", size=45, color=color_3, font_family="SemiBold")
                    ),
                    ft.Container(width=292),
                    ft.Container(
                        width=80, height=80, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                        on_click=exiting, alignment=ft.alignment.Alignment(0, 0), on_hover=hover_button,
                        content=ft.Icon(name="EXIT_TO_APP", size=50, color=color_3)
                    ),
                ])
            )
        )
        await page.update_async()

    global background_color

    page.fonts = {
        "SemiBold": "misc\\font\\OpenSans-SemiBold.ttf",
        "Bold": "misc\\font\\OpenSans-Bold.ttf"
    }

    with open("misc\\data\\style.json", "r", encoding='utf-8') as f:
        style = json.load(f)

    color_1 = style["colors"]["color-1"]
    color_2 = style["colors"]["color-2"]
    color_3 = style["colors"]["color-3"]
    background_color = style["colors"]["background"]
    error_color_1 = "#CA5555"
    error_color_2 = "#943939"

    page.theme = ft.theme.Theme(color_scheme=ft.ColorScheme(primary=color_2, secondary=color_3))
    page.bgcolor = background_color

    page.window_width = 1110
    page.window_height = 720
    page.padding = 0
    page.window_resizable = False
    await page.window_center_async()

    pick_files_dialog = ft.FilePicker()
    page.overlay.append(pick_files_dialog)

    connection = await more.connect_to_db()

    with connection.cursor() as cursor:
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (identificator,))
        USER_DATA = cursor.fetchone()

    try:
        user_images_dialog = ft.Image(src=f"{USER_DATA['logo']}", width=120, height=120, border_radius=60,
                                      fit=ft.ImageFit.COVER,
                                      error_content=ft.Container(width=120, height=120, bgcolor=color_2, content=
                                      ft.Icon('ACCOUNT_CIRCLE', color=color_3, size=100)))
        if await check_user(page):
            await main_menu(page)
            await check_version(page)

        else:
            await page.window_destroy_async()
    except:
        user_images_dialog = ft.Image(src="None", width=120, height=120, border_radius=60,
                                      fit=ft.ImageFit.COVER,
                                      error_content=ft.Container(width=120, height=120, bgcolor=color_2, content=
                                      ft.Icon('ACCOUNT_CIRCLE', color=color_3, size=100)))
        if await check_user(page):
            await main_menu(page)
        else:
            await page.window_destroy_async()


async def start(log=False):
    import logging
    if log:
        logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    await ft.app_async(main_app)

if __name__ == '__main__':
    asyncio.run(start())
