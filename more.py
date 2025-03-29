import asyncio
import pymysql
import os
from dotenv import load_dotenv, find_dotenv
import time
import subprocess


async def start_backup(input_files, name, type, compression, password, ignore_files):
    try:
        if type.upper() != 'RAR':  # Работа программы 7zip
            if not input_files or not name:
                return False
            command = ['misc\\back\\7-zip\\7z.exe', 'a']
            command.append('-mx0') if not compression else command.append(f'-mx{compression}')
            command.append(f'-p{password}') if password != "" else None
            command.append(f'-t{type}') if type else command.append(f'-tzip')
            command.append(f'{name}')
            command.extend(input_files)
            with open('ignored_files_list.txt', 'w', encoding='utf-8') as f:
                for file in ignore_files:
                    if file[-1] == '\\' or file[-2] == '\\':
                        ignore = file.split('\\')
                        no_file = ignore[len(ignore) - 2]
                        f.write(f'{no_file}\n')
                    else:
                        ignore = file.split('\\')
                        no_file = ignore[len(ignore) - 1]
                        f.write(f'{no_file}\n')
            command.append(f'-xr@ignored_files_list.txt')
        else:  # Работа программы WinRar
            if not input_files or not name:
                return False
            command = ['misc\\back\\WinRar\\Rar.exe', 'a']
            command.append('-m0') if not compression else command.append(f'-m{compression}')
            command.append(f'-p{password}') if password != "" else None
            command.append(f'{name}')
            command.extend(input_files)
            with open('ignored_files_list.txt', 'w', encoding='utf-8') as f:
                for file in ignore_files:
                    if file[-1] == '\\' or file[-2] == '\\':
                        ignore = file.split('\\')
                        no_file = ignore[len(ignore) - 2]
                        f.write(f'{no_file}\n')
                    else:
                        ignore = file.split('\\')
                        no_file = ignore[len(ignore) - 1]
                        f.write(f'{no_file}\n')
            command.append(f'-x@ignored_files_list.txt')
        subprocess.run(command, shell=False)
        os.remove('ignored_files_list.txt')
        return True
    except Exception as ex:
        return False


def delete_user(user=-1, host=None, user_db=None, password=None, name=None):
    if user != -1:
        try:
            connection = pymysql.connect(
                host=host,
                port=3306,
                user=user_db,
                password=password,
                database=name,
                cursorclass=pymysql.cursors.DictCursor
            )
            try:
                with connection.cursor() as cursor:
                    try:
                        id = int(user)
                        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
                        error1 = f'User id={user} deleted\n'
                        connection.commit()
                    except Exception as ex:
                        cursor.execute("DELETE FROM users WHERE login = %s", (user,))
                        error1 = f'User name={user} deleted\n'
                        connection.commit()
            except Exception as ex:
                error1 = ""
            finally:
                connection.close()
            error2 = ""
        except Exception as ex:
            error2 = f"Error - {ex}\n"
        error3 = ""
    else:
        error3 = "Некорректная команда\n"
    result = f"{error3}{error2}{error1}"
    return result


def delete_table(table='None', host=None, user=None, password=None, name=None):
    if table!= 'None' and host!= 'None' and user!= 'None' and password!= 'None' and name!= 'None':
        try:
            connection = pymysql.connect(
                host=host,
                port=3306,
                user=user,
                password=password,
                database=name,
                cursorclass=pymysql.cursors.DictCursor
            )
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE {table}")
                    connection.commit()

                print('Operation OK')
            finally:
                connection.close()
        except Exception as ex:
            print(f'Error - {ex}')
    else:
        print('Cancel operation MySQL')


def reset_data(code_1=None, code_2=None, verify=True, connection=False):
    if verify:
        a = input('Введите первый пароль - ')
        b = input('Введите второй пароль - ')

        if a != code_1 or b != code_2:
            return 'Отмена операции, напрвильный пароль'

        for i in range(0, 15):
            print(f'Операция сброса начнется через {15 - i}')
            time.sleep(1)

    if connection:
        try:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"DROP TABLE users")
                    connection.commit()
                    error1 = ""
                except Exception as ex:
                    error1 = f'Error DELETE TABLE users - {ex}\n'

                try:
                    query = "CREATE TABLE users (id INT, login TEXT, email TEXT, password TEXT, code_verify INT, logo TEXT)"
                    cursor.execute(query)
                    connection.commit()

                    data = [0, 'Kkleytt', 'fedoskin01022005@gmail.com', 'Fedoskin010220053666!']
                    cursor.execute("INSERT INTO users (id, login, email, password) VALUES (%s, %s, %s, %s)",
                                   (data[0], data[1], data[2], data[3]))
                    connection.commit()
                except:
                    pass
            error2 = "ALL USER DATA HAS BEEN RESET\n"
        except Exception as ex:
            error2 = f'Error in working with database - {ex}\n'
        finally:
            error3 = ""
    else:
        error3 = f'Error in connection to database\n'

    result = f'{error1}{error2}{error3}'
    return result


async def connect_to_db():
    load_dotenv(find_dotenv())

    HOST = os.getenv("DB_HOST")
    PORT = int(os.getenv("DB_PORT"))
    USER = os.getenv("DB_ADMIN_LOGIN")
    PASSWORD = os.getenv("DB_ADMIN_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    try:
        connection = pymysql.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as ex:
        return ex


async def create_email(mail, code, user, colors):
    from jinja2 import Template

    template_content = open('misc\\html\\index.html', 'r', encoding='utf-8').read()
    template = Template(template_content)
    numbers_code = [int(num) for num in code]
    html_content = template.render(User=user,
                                   Number_1=numbers_code[0],
                                   Number_2=numbers_code[1],
                                   Number_3=numbers_code[2],
                                   Number_4=numbers_code[3],
                                   Number_5=numbers_code[4],
                                   Number_6=numbers_code[5],
                                   Color_0=colors[0],
                                   Color_1=colors[1],
                                   Color_2=colors[2],
                                   Color_3=colors[3],)
    await send_email(mail, html_content)


async def send_email(mail, html_code):
    import smtplib
    from email.mime.text import MIMEText
    import os
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())

    sender = os.getenv("MAIL_LOGIN")
    password = os.getenv("MAIL_PASSWORD")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        server.login(sender, password)
        msg = MIMEText(html_code, "html")
        msg["From"] = 'Backup code'
        msg["To"] = mail
        msg["Subject"] = "Код подтверждения"
        server.sendmail(sender, mail, msg.as_string())
        server.quit()
        return "Message was sent sucsess"
    except Exception as _ex:
        return f"{_ex}\nCheck your data, please!"


def check_version():
    version = "1.0-alpha"
    date = "19-04-2024"
    new = ['data.py', 'app.py', 'admin.py', 'sign.py', 'more.py', 'refactor.py', 'instruction.json']
    info = [
        'Сделана программа для входа в систему',
        'Сделано основное окно программы',
        'Сделана программа дял администрирования БД',
        'Сделана программа для редактирования прессетов',
        'Была созданная инструкция'
    ]
    result = {
        "version": version,
        "date": date,
        "new": new,
        "info": info
    }
    return result


async def main():
    print("TEST")
    print(await connect_to_db())


if __name__ == '__main__':
    asyncio.run(main())
