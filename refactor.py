import flet as ft
import asyncio
import json

import more


async def main(page: ft.Page):
    global PRESETS, PRESETS_ITEMS, DATA

    async def hover_button_save(e):
        e.control.bgcolor = color_3 if e.data == "true" else color_2
        e.control.content.color = color_2 if e.data == "true" else color_3
        e.control.update()

    async def hover_button_exit(e):
        e.control.bgcolor = error_color_2 if e.data == "true" else error_color_1
        e.control.content.color = error_color_1 if e.data == "true" else error_color_2
        e.control.update()

    async def exiting(e):
        async def exiting_yes(e):
            page.window_destroy()

        async def exiting_no(e):
            confirm_exit_dialog.open = False
            await page.update_async()

        confirm_exit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Подтвердите выход", size=30),
            content=ft.Text("Вы действительно хотите выйти?", size=22),
            actions=[
                ft.ElevatedButton(on_click=exiting_no, bgcolor=color_2,
                                  content=ft.Text("Остаться", color=color_3, size=22)),
                ft.ElevatedButton(on_click=exiting_yes, bgcolor=error_color_1,
                                  content=ft.Text("Выйти", color=error_color_2, size=22))
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        page.dialog = confirm_exit_dialog
        confirm_exit_dialog.open = True
        await page.update_async()

    async def save_main_menu(e):
        with connection.cursor() as cursor:
            cursor.execute("UPDATE data SET dirs=%s WHERE id=%s", (json.dumps(DATA), identificator))
            connection.commit()
        with open("misc\\data\\data.json", "w", encoding="utf-8") as file:
            json.dump(DATA, file, indent=4, ensure_ascii=False)
        try:

            text = 'Удачное сохранение'
        except Exception as ex:
            text = 'Неудачное сохранение'
        confirm_save = ft.AlertDialog(
            modal=True,
            title=ft.Text(text),
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.dialog = confirm_save
        confirm_save.open = True
        await page.update_async()
        await asyncio.sleep(2)
        confirm_save.open = False
        await page.update_async()

    async def delete_presset(e, item):
        global DATA, PRESETS, PRESETS_ITEMS
        try:
            DATA['pressets'].remove(item)
            del DATA[item]
        except:
            pass
        finally:
            await main_menu(page)

    async def add_presset(e):
        async def add_presset_yes(e):
            global PRESETS, PRESETS_ITEMS

            name = add_presset_dialog.content.value
            add_presset_dialog.open = False
            try:
                DATA["pressets"].append(name)
                DATA[name] = {"files": [], "ignore": []}
                PRESETS_ITEMS.append(
                    ft.Container(
                        width=720, height=80, bgcolor=color_2, border_radius=20,
                        border=ft.border.all(5, color_3),
                        padding=ft.padding.only(30, 0, 20, 0),
                        content=ft.Row([
                            ft.Container(
                                width=550,
                                content=ft.Text(name[:30], size=30, color=color_3, font_family="SemiBold")
                            ),
                            ft.Container(
                                height=80,
                                content=ft.Row([
                                    ft.IconButton(icon="EDIT", icon_size=35, icon_color=color_3,
                                                  on_click=lambda e, a=name: asyncio.run(edit_presset(e, a))),
                                    ft.IconButton(icon="DELETE", icon_size=35, icon_color=color_3,
                                                  on_click=lambda e, a=name: asyncio.run(delete_presset(e, a)))
                                ]))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)))
                PRESETS.controls = PRESETS_ITEMS
                await PRESETS.update_async()
            except Exception as ex:
                print(ex)
            await page.update_async()

        async def add_presset_no(e):
            add_presset_dialog.open = False
            await page.update_async()

        add_presset_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Создание нового прессета"),
            content=ft.TextField(label="Имя прессета"),
            actions=[
                ft.ElevatedButton("Создать", on_click=add_presset_yes),
                ft.ElevatedButton(on_click=add_presset_no, bgcolor=ft.colors.RED,
                                  content=ft.Text("Отмена", color=ft.colors.RED_900))
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.dialog = add_presset_dialog
        add_presset_dialog.open = True
        add_presset_dialog.content.value = ''
        await page.update_async()

    async def edit_presset(e, item):
        async def delete_file(e, index_file, item, type):
            if type == "files":
                DATA[item]["files"].remove(index_file)
                files_add_lst = []
                for index, file in enumerate(files_lst):
                    files_add_lst.append(
                        ft.Container(
                            width=720,
                            content=ft.Row([
                                ft.Row([
                                    ft.Container(width=1),
                                    ft.Container(
                                        width=640,
                                        content=ft.Text(file)
                                    )
                                ]),
                                ft.Row([
                                    ft.IconButton(icon="REMOVE_CIRCLE_OUTLINE", icon_size=30, icon_color=color_3,
                                                  on_click=lambda e, a=file, t="files": asyncio.run(
                                                      delete_file(e, a, item, t))),
                                    ft.Container(width=1),
                                ])

                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        )
                    )
                table_data_files.controls = files_add_lst
                await table_data_files.update_async()
            else:
                DATA[item]["ignore"].remove(index_file)
                ignor_add_lst = []
                for index, file in enumerate(ignor_lst):
                    ignor_add_lst.append(
                        ft.Container(
                            width=720,
                            content=ft.Row([
                                ft.Row([
                                    ft.Container(width=1),
                                    ft.Container(
                                        width=640,
                                        content=ft.Text(file)
                                    )
                                ]),
                                ft.Row([
                                    ft.IconButton(icon="REMOVE_CIRCLE_OUTLINE", icon_size=30, icon_color=color_3,
                                                  on_click=lambda e, a=file, t='ignore': asyncio.run(
                                                      delete_file(e, a, item, t))),
                                    ft.Container(width=1),
                                ])

                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        )
                    )
                table_data_ignor.controls = ignor_add_lst
                await table_data_ignor.update_async()

        async def add_files(e, item, type):
            async def add_files_yes(e):
                directory = dialog.content.value
                if directory != "":
                    if type == 'files':
                        DATA[item]["files"].append(directory)
                        files_add_lst = []
                        for index, file in enumerate(files_lst):
                            files_add_lst.append(
                                ft.Container(
                                    width=720,
                                    content=ft.Row([
                                        ft.Row([
                                            ft.Container(width=1),
                                            ft.Container(
                                                width=640,
                                                content=ft.Text(file)
                                            )
                                        ]),
                                        ft.Row([
                                            ft.IconButton(icon="REMOVE_CIRCLE_OUTLINE", icon_size=30,
                                                          icon_color=color_3,
                                                          on_click=lambda e, a=file, t="files": asyncio.run(
                                                              delete_file(e, a, item, t))),
                                            ft.Container(width=1),
                                        ])

                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                                )
                            )
                        table_data_files.controls = files_add_lst
                        await table_data_files.update_async()
                    else:
                        DATA[item]["ignore"].append(directory)
                        ignor_add_lst = []
                        for index, file in enumerate(ignor_lst):
                            ignor_add_lst.append(
                                ft.Container(
                                    width=720,
                                    content=ft.Row([
                                        ft.Row([
                                            ft.Container(width=1),
                                            ft.Container(
                                                width=640,
                                                content=ft.Text(file)
                                            )
                                        ]),
                                        ft.Row([
                                            ft.IconButton(icon="REMOVE_CIRCLE_OUTLINE", icon_size=30,
                                                          icon_color=color_3,
                                                          on_click=lambda e, a=file, t='ignore': asyncio.run(
                                                              delete_file(e, a, item, t))),
                                            ft.Container(width=1),
                                        ])

                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                                )
                            )
                        table_data_ignor.controls = ignor_add_lst
                        await table_data_ignor.update_async()
                dialog.open = False
                await page.update_async()

            async def add_files_no(e):
                dialog.open = False
                await page.update_async()

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Добавьте путь до файла или директории"),
                content=ft.TextField(label="Путь"),
                actions=[
                    ft.ElevatedButton(on_click=add_files_yes, bgcolor=color_2,
                                      content=ft.Text("Добавить", size=22, color=color_3)),
                    ft.ElevatedButton(on_click=add_files_no, bgcolor=error_color_1,
                                      content=ft.Text("Отмена", color=error_color_2, size=22))
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )

            page.dialog = dialog
            dialog.open = True
            await page.update_async()

        global DATA

        try:
            files_lst = DATA[item]["files"]
        except:
            files_lst = []
        try:
            ignor_lst = DATA[item]["ignore"]
        except:
            ignor_lst = []

        files_add_lst = []
        ignor_add_lst = []
        for index, file in enumerate(files_lst):
            files_add_lst.append(
                ft.Container(
                    width=720,
                    content=ft.Row([
                        ft.Row([
                            ft.Container(width=1),
                            ft.Container(
                                width=640,
                                content=ft.Text(file)
                            )
                        ]),
                        ft.Row([
                            ft.IconButton(icon="REMOVE_CIRCLE_OUTLINE", icon_size=30, icon_color=color_3,
                                          on_click=lambda e, a=file, t="files": asyncio.run(delete_file(e, a, item, t))),
                            ft.Container(width=1),
                        ])

                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            )
        for index, file in enumerate(ignor_lst):
            ignor_add_lst.append(
                ft.Container(
                    width=720,
                    content=ft.Row([
                        ft.Row([
                            ft.Container(width=1),
                            ft.Container(
                                width=640,
                                content=ft.Text(file)
                            )
                        ]),
                        ft.Row([
                            ft.IconButton(icon="REMOVE_CIRCLE_OUTLINE", icon_size=30, icon_color=color_3,
                                          on_click=lambda e, a=file, t='ignore': asyncio.run(delete_file(e, a, item, t))),
                            ft.Container(width=1),
                        ])

                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            )

        table_data_files = ft.Column(controls=files_add_lst, scroll=ft.ScrollMode.ALWAYS)
        table_data_ignor = ft.Column(controls=ignor_add_lst, scroll=ft.ScrollMode.ALWAYS)

        await page.clean_async()
        await page.add_async(
            ft.Container(height=10),
            ft.Row([
                ft.Container(width=20),
                ft.Container(
                    width=180, height=60, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                    alignment=ft.alignment.center, on_hover=hover_button_save,
                    on_click=lambda e: asyncio.run(main_menu(e)),
                    content=ft.Text("Назад", size=30, color=color_3, font_family="SemiBold")
                ),
                ft.Container(
                    width=530, height=60, bgcolor=color_2, border_radius=20, border=ft.border.all(5, color_3),
                    content=ft.Row([
                        ft.Text(f"Профиль {item[:24]}", size=30, color=color_3, font_family="SemiBold")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                )
            ]),
            ft.Row([
                ft.Container(
                    width=720, height=300, bgcolor=color_2, border_radius=20,
                    content=ft.Column([
                        ft.Container(
                            bgcolor=color_3,
                            content=ft.Row([
                                ft.Container(width=5),
                                ft.Text("Директории и файлы для архивации", color=color_1, size=22),
                                ft.Container(width=250),
                                ft.IconButton(icon="ADD_CIRCLE_OUTLINE", icon_size=30, icon_color=color_1,
                                              on_click=lambda e, t="files": asyncio.run(add_files(e, item, t)))])),
                        ft.Container(
                            width=720, height=240,
                            content=
                            ft.Column([
                                table_data_files,
                            ], scroll=ft.ScrollMode.ALWAYS))]))
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Container(
                    width=720, height=240, bgcolor=color_2, border_radius=20,
                    content=ft.Column([
                        ft.Container(
                            bgcolor=color_3,
                            content=ft.Row([
                                ft.Container(width=5),
                                ft.Text("Директории и файлы для игнорирования", size=22, color=color_1),
                                ft.Container(width=198),
                                ft.IconButton(icon="ADD_CIRCLE_OUTLINE", icon_size=30, icon_color=color_1,
                                              on_click=lambda e, t="ignore": asyncio.run(add_files(e, item, t)))])),
                        ft.Container(
                            width=720, height=180,
                            content=
                            ft.Column([
                                table_data_ignor,
                            ], scroll=ft.ScrollMode.ALWAYS))]))
            ], alignment=ft.MainAxisAlignment.CENTER)
        )

    async def main_menu(e):
        global PRESETS_ITEMS, PRESETS, DATA

        all_pressets = DATA['pressets']
        PRESETS_ITEMS = []
        for item in all_pressets:
            PRESETS_ITEMS.append(
                ft.Container(
                    width=720, height=80, bgcolor=color_2, border_radius=20,
                    border=ft.border.all(5, color_3),
                    padding=ft.padding.only(30, 0, 20, 0),
                    content=ft.Row([
                        ft.Container(
                            width=550,
                            content=ft.Text(item[:30], size=30, color=color_3, font_family="SemiBold")
                        ),
                        ft.Container(
                            height=80,
                            content=ft.Row([
                                ft.IconButton(icon="EDIT", icon_size=35, icon_color=color_3,
                                              on_click=lambda e, a=item: asyncio.run(edit_presset(e, a))),
                                ft.IconButton(icon="DELETE", icon_size=35, icon_color=color_3,
                                              on_click=lambda e, a=item: asyncio.run(delete_presset(e, a)))
                            ]))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)))
        PRESETS = ft.Column(controls=PRESETS_ITEMS, scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.START)
        await page.clean_async()
        await page.add_async(
            ft.Column([
                ft.Container(
                    width=770,
                    content=ft.Row([
                        PRESETS,
                    ], alignment=ft.MainAxisAlignment.CENTER), height=580),
                ft.Container(height=5),
                ft.Container(
                    height=80, bgcolor=color_1,
                    content=ft.Row([
                            ft.IconButton(icon="ADD_TO_PHOTOS", icon_size=35, on_click=add_presset),
                            ft.Container(
                                width=200, height=60, on_click=save_main_menu, bgcolor=color_2,
                                border_radius=50, border=ft.border.all(5, color_3), alignment=ft.alignment.top_center,
                                content=ft.Text("Save", size=34, color=color_3, font_family="Bold"),
                                on_hover=hover_button_save
                            ),
                            ft.Container(
                                width=200, height=60, on_click=exiting, bgcolor=error_color_1, border_radius=50,
                                border=ft.border.all(5, error_color_2), alignment=ft.alignment.top_center,
                                content=ft.Text("Exit", size=34, color=error_color_2, font_family="Bold"),
                                on_hover=hover_button_exit
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
        await page.update_async()

    page.window_width = 800
    page.window_height = 700
    page.window_resizable = False
    await page.window_center_async()
    await page.window_to_front_async()
    page.window_prevent_close = True
    page.padding = ft.padding.all(0)

    with open("misc\\data\\style.json", "r") as f:
        STYLE = json.load(f)

    color_1 = STYLE["colors"]["color-1"]
    color_2 = STYLE["colors"]["color-2"]
    color_3 = STYLE["colors"]["color-3"]
    error_color_1 = "#CA5555"
    error_color_2 = "#943939"

    page.theme = ft.theme.Theme(color_scheme=ft.ColorScheme(primary=color_2, secondary=color_3))
    page.bgcolor = STYLE["colors"]["background"]
    page.fonts = {
        "SemiBold": "misc\\font\\OpenSans-SemiBold.ttf",
        "Bold": "misc\\font\\OpenSans-Bold.ttf",
    }

    with open("misc\\data\\session.json", "r") as f:
        USER = json.load(f)
    identificator = USER["id"]

    connection = await more.connect_to_db()
    try:
        with open("misc\\data\\data.json", "r", encoding="utf-8") as f:
            DATA = json.load(f)
    except:
        DATA = None
    if not DATA:
        with connection.cursor() as cursor:
            cursor.execute("SELECT dirs FROM data WHERE id=%s", (identificator,))
            DATA = cursor.fetchone()
        try:
            DATA = DATA['dirs']
            DATA = json.loads(DATA)
        except:
            DATA = {
                "pressets": []
            }

    await main_menu(page)


async def start(e):
    await ft.app_async(main)


if __name__ == '__main__':
    asyncio.run(start(0))
