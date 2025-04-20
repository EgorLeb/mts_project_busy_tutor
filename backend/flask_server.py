# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
import sqlite3
import json
from flask import Flask, make_response, request, Response
from datetime import datetime


def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    # Вывод в консоль
    print(log_entry.strip())

    # Запись в файл
    with open("app.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)


def get_db():
    return sqlite3.connect('mydatabase.db')


def get_cursor():
    return get_db().cursor()


def init_db():
    log_message("Init database")
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS owners (
                mail TEXT PRIMARY KEY,
                password TEXT,
                fullname TEXT,
                freeSlots TEXT,
                busySlots TEXT,
                phone TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                mail TEXT PRIMARY KEY,
                password TEXT,
                fullname TEXT,
                ownerMail TEXT,
                phone TEXT
            )
        """)
        db.commit()


def cleaner():
    """
    clean the DB
    :return: None
    """
    log_message("Clean database")
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
                DROP TABLE owners;
                """)
    cursor.execute("""
                DROP TABLE visitors;
                """)
    connection.commit()

# cleaner()  # ------------очищение базы данных------------


def log(mail, password):
    """
    Function for check of user
    :param mail: email
    :param password: password of the email
    :return: dict with info
    """
    owner = checkInOwners(mail, password)
    if len(owner) != 0:
        log_message(f"Log owner {mail=}")
        return {
            "role": "owner",
            "mail": owner[0][0],
            "fullname": owner[0][2],
            "freeSlots": owner[0][3],
            "busySlots": owner[0][4],
            "phone": owner[0][5]
        }
    visitor = checkInVisitors(mail, password)
    if len(visitor) != 0:
        log_message(f"Log visitor {mail=}")
        return {
            "role": "visitor",
            "mail": visitor[0][0],
            "fullname": visitor[0][2],
            "ownerMail": visitor[0][3],
            "phone": visitor[0][4]
        }
    log_message(f"Log ERROR {mail=}")
    return {}


def reg(mail, password, role, fullname, phone):
    """
    check and create the user
    :param mail: email
    :param password: new password
    :param role: owner or visitor
    :param fullname: name of the user
    :param phone: phone number
    :return: code of response
    """
    log_message(f"Reg {role=} {mail=}")
    connection = get_db()
    cursor = connection.cursor()
    if role == 'owner' and len(checkInOwnersOnlyMail(mail)) == 0:
        cursor.execute(f"""
                        INSERT INTO owners VALUES ('{mail}', '{password}', '{fullname}', '[]', '[]', '{phone}')
                        """)
        connection.commit()
    elif role == "visitor" and len(checkInVisitorsOnlyMail(mail)) == 0:
        cursor.execute(f"""
                        INSERT INTO visitors VALUES ('{mail}', '{password}', '{fullname}', '-', '{phone}')
                        """)
        connection.commit()
    else:
        log_message(f"Reg ERROR {role=} {mail=}")
        return 405
    return 200


def checkInOwners(mail, password):
    """
    Checking of user in the DB (owners) by using email and password
    :param mail: email
    :param password: password
    :return: list with user
    """
    log_message(f"Check owner by pass {mail=}")
    cursor = get_cursor()
    cursor.execute(f"""
            SELECT * FROM owners
            WHERE mail = '{mail}' and password = '{password}'
            """)
    rows = cursor.fetchall()
    return rows


def checkInOwnersOnlyMail(mail):
    """
    Checking of user in the DB (owners) by using email
    :param mail: email
    :return: list with user
    """
    log_message(f"Check owner without pass {mail=}")
    cursor = get_cursor()
    cursor.execute(f"""
            SELECT * FROM owners
            WHERE mail = '{mail}'
            """)
    rows = cursor.fetchall()
    return rows


def checkInVisitors(mail, password):
    """
    Checking of user in the DB (visitors) by using email and password
    :param mail: email
    :param password: password
    :return: list with user
    """
    log_message(f"Check visitor by pass {mail=}")
    cursor = get_cursor()
    cursor.execute(f"""
            SELECT * FROM visitors
            WHERE mail = '{mail}' and password = '{password}'
            """)
    rows = cursor.fetchall()
    return rows


def checkInVisitorsOnlyMail(mail):
    """
    Checking of user in the DB (visitors) by using email
    :param mail: email
    :return: list with user
    """
    log_message(f"Check visitor without pass {mail=}")
    cursor = get_cursor()
    cursor.execute(f"""
            SELECT * FROM visitors
            WHERE mail = '{mail}'
            """)
    rows = cursor.fetchall()
    return rows


def getTime(mail):
    """
    Getting time by using the email
    :param mail: email
    :return: dict
    """
    cursor = get_cursor()
    cursor.execute(f"""
                SELECT * FROM owners
                WHERE mail = '{mail}'
                """)
    rows = cursor.fetchall()
    if len(rows) == 0:
        log_message(f"getTime ERROR {mail=}")
        return None
    log_message(f"getTime {mail=}")
    return {
        "freeSlots": rows[0][3],
        "busySlots": rows[0][4]
    }


def setFreeSlots(mail, data):
    """
    Setting free slots in DB for owner
    :param mail: email
    :param data: free slots (string)
    :return: None
    """
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(f"""UPDATE owners SET freeSlots = '{data}' where mail = '{mail}'""")
    connection.commit()
    log_message(f"setFreeSlots {mail=}")


def setBusySlots(mail, data):
    """
    Setting busy slots in DB for owner
    :param mail: email
    :param data: busy slots (string)
    :return: None
    """
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(f"""UPDATE owners SET busySlots = '{data}' where mail = '{mail}'""")
    connection.commit()
    log_message(f"setBusySlots {mail=}")


def getInfo(mail):
    """
    Get info about owner by mail
    :param mail: email
    :return: dict
    """
    owner = checkInOwnersOnlyMail(mail)
    if len(owner) != 0:
        log_message(f"getInfo {mail=}")
        return {
            "role": "owner",
            "mail": owner[0][0],
            "fullname": owner[0][2],
            "freeSlots": owner[0][3],
            "busySlots": owner[0][4]
        }
    # visitor = checkInVisitorsOnlyMail(mail)
    # if len(visitor) != 0:
    #     return {
    #         "role": "visitor",
    #         "mail": visitor[0][0],
    #         "fullname": visitor[0][2],
    #         "ownerMail": visitor[0][3]
    #     }
    log_message(f"getInfo ERROR {mail=}")
    return False


def setOwner(mail, password, ownerMail):
    """
    set owner for visitor
    :param mail: email of the visitor
    :param password: password
    :param ownerMail: mail of owner
    :return: code of response
    """
    connection = get_db()
    cursor = connection.cursor()
    f1 = checkInVisitors(mail, password)
    f2 = checkInOwnersOnlyMail(ownerMail)
    if len(f1) != 0 and len(f2) != 0:
        cursor.execute(f"""UPDATE visitors SET ownerMail = '{ownerMail}' where mail = '{mail}' and password = '{password}'""")
        connection.commit()
        log_message(f"setOwner {mail=}")
        return 200
    else:
        log_message(f"setOwner ERROR {mail=} {ownerMail=}")
        return 406



# def create_event(name="Event", location="Online",
#                  description="Description", start="2023-07-23T10:00:00+03:00",
#                  end="2023-07-23T13:00:00+03:00", frequency="DAILY", count=1, attendees=None):
#
#     SCOPES = ['https://www.googleapis.com/auth/calendar']
#     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     final_attendees = []
#     print(creds)
#     # for attendee in attendees:
#     #     if attendee != "":
#     #         final_attendees.append({'email': f'{attendee}'})
#     try:
#         service = build("calendar", "v3", credentials=creds)
#         event = {
#             "summary": name,
#             "location": location,
#             "description": description,
#             "colorId": 10,
#             "start": {
#                 "dateTime": start,
#                 "timeZone": "Europe/Moscow"
#             },
#             "end": {
#                 "dateTime": end,
#                 "timeZone": "Europe/Moscow"
#             },
#             "recurrence": [
#                 f"RRULE:FREQ={frequency};COUNT={count}"
#             ]
#         }
#         event = service.events().insert(calendarId="primary", sendNotifications=True, body=event).execute()
#         return {"link": event.get('htmlLink')}
#     except HttpError as error:
#         return 'An error occurred: %s' % error

# def create_event_old(name="Event", location="Online",
#                  description="Description", start="2023-08-23T10:00:00+03:00",
#                  end="2023-08-23T13:00:00+03:00", frequency="DAILY", count=1, attendees=None):
#     SCOPES = ['https://www.googleapis.com/auth/calendar']
#     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     final_attendees = []
#     for attendee in attendees:
#         if attendee != '':
#             final_attendees.append({'email': f'{attendee}'})
#     try:
#         service = build("calendar", "v3", credentials=creds)
#         event = {
#             "summary": name,
#             "location": location,
#             "description": description,
#             "colorId": 10,
#             "start": {
#                 "dateTime": start,
#                 "timeZone": "Europe/Moscow"
#             },
#             "end": {
#                 "dateTime": end,
#                 "timeZone": "Europe/Moscow"
#             },
#             "recurrence": [
#                 f"RRULE:FREQ={frequency};COUNT={count}"
#             ],
#             "attendees": final_attendees
#         }
#         event = service.events().insert(calendarId="primary", sendNotifications=True, body=event).execute()
#         return {"link": event.get('htmlLink')}
#     except HttpError as error:
#         return None


app = Flask(__name__)

app.debug = True
init_db()


@app.route('/', methods=["POST", "GET", "OPTIONS"])
def index():
    """
    main function of Flask
    :return: dict
    """
    log_message(f"REQUEST INFO {request.method=}")
    if request.method in ["GET", "OPTIONS"]:
        resp = make_response("Hello, I am Egor. Server do not available for you in this method(", 200)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Content-Type"] = "application/json; charset=utf-8"
        resp.headers["Access-Control-Allow-Headers"] = "*"
        log_message(f"REQUEST INFO {resp=}")
        return resp

    data_json = request.get_json()  # dict()
    log_message(f"REQUEST INFO {data_json=}")

    code_response = 200
    res = {}
    if data_json.get("type", "-") == "log" and "mail" in data_json and "password" in data_json:
        res = log(data_json["mail"], data_json["password"])
        if len(res) == 0:
            code_response = 405
    elif data_json.get("type", "-") == "reg" and "mail" in data_json and "password" in data_json \
            and "role" in data_json and "fullname" in data_json and "phone" in data_json:
        code_response = reg(data_json["mail"], data_json["password"], data_json["role"], data_json["fullname"],
                            data_json["phone"])
    elif data_json.get("type", "-") == "getTime" and "ownerMail" in data_json:
        res = getTime(data_json["ownerMail"])
        if res is None:
            res = {}
            code_response = 406
    elif data_json.get("type", "-") == "setTime" and "mail" in data_json \
            and "freeSlots" in data_json and "busySlots" in data_json:
        if len(checkInOwnersOnlyMail(data_json["mail"])) != 0:
            setFreeSlots(data_json["mail"], data_json["freeSlots"])
            setBusySlots(data_json["mail"], data_json["busySlots"])
        else:
            code_response = 406
    elif data_json.get("type", "-") == "createEvent" and "mail" in data_json and "password" in data_json and \
            "secondMail" in data_json and "nameOfEvent" in data_json and "description" in data_json and \
            "start" in data_json and "end" in data_json:
        if len(checkInOwners(data_json["mail"], data_json["password"])) != 0 or \
                len(checkInVisitors(data_json["mail"], data_json["password"])) != 0:
            # res = create_event()
            # if not res:
            #     code_response = 404
            code_response = 200
        else:
            code_response = 406
    elif data_json.get("type", "-") == "getInfo" and "mail" in data_json:
        res = getInfo(data_json["mail"])
        if not res:
            code_response = 406
    elif data_json.get("type", '-') == "setOwner" and "mail" in data_json and "password" in data_json and "ownerMail" in data_json:
        code_response = setOwner(data_json['mail'], data_json["password"], data_json["ownerMail"])
    else:
        code_response = 404
    # connection.commit()

    log_message(f"REQUEST INFO {res=} {code_response=}")
    resp = make_response(json.dumps(res), code_response)
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"

    return resp
app.run(host="0.0.0.0", port=5100)