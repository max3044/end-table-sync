# Подключаем библиотеки
import httplib2 
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials	
import json
from sel import runner
import pickle

""""
В каждом файле (spreadsheet) находятся листы-вкладки (sheet).
Каждый sheet имеет свой числовой код (sheetId). 
У первого созданного в документе листа этот Id равен 0.
Остальные листы имеют сильно отличные от нуля Id (т.е. они не нумеруются подряд).
"""
email="service-account-me@my-law-project-1.iam.gserviceaccount.com"

def give_access(spreadsheetId, email="maximkovalunas@gmail.com"):
    driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API
    access = driveService.permissions().create(
        fileId = spreadsheetId,
        body = {'type': 'user', 'role': 'writer', 'emailAddress': email},  # Открываем доступ на редактирование
        fields = 'id'
    ).execute()


CREDENTIALS_FILE = 'my-law-project-1-36975dc6c026.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE, 
    ['https://www.googleapis.com/auth/spreadsheets', 
     'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 
spreadsheet_id = "19CgdHIBxHCyb3MFGBFV7WMp352vj0uzpm_4LWD__l4U"

def read_values(spreadsheet_id):
    # Пример чтения файла
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Лист1!A:I',
        majorDimension='ROWS'
    ).execute()
    return values

def update_values(spreadsheet_id, values):
    results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheet_id, body = {
    "valueInputOption": "USER_ENTERED", # Данные воспринимаются, как вводимые пользователем (считается значение формул)
    "data": [
        {"range": "Лист1!A:I",
        "majorDimension": "ROWS",     # Сначала заполнять строки, затем столбцы
        "values": values}
    ]
    }).execute()
    return results
values = read_values(spreadsheet_id)


# with open("test_json_sheet.json", "w", encoding="utf-8") as file:

#     json.dump(values, file, ensure_ascii=False, indent=2)

# with open("test_json_sheet.json", "r", encoding="utf-8") as file:
#     dic = json.load(file)

dic = values
# datas = [i for i in dic['values'][1:]]
headers = [i for i in dic['values'][0]]
datas = [i for i in dic['values'][1:]]
datas = [i for i in datas if len(i) > 1]

# print(datas)
cases = [i[1] for i in datas]

# 
results = runner(headless=True, cases=cases)

# with open("data/results.pickle", "wb") as file:
#     pickle.dump(results, file)
# with open("data/results.pickle", "rb") as file:
#     results = pickle.load( file)

# print(results)
new_datas = []
new_datas.append(headers)
for i, d in enumerate(datas):
    data = d 
    if d[-1] != results[i]['current_state']:
        data[-1] = results[i]['current_state']
    new_datas.append(data)

print(new_datas)
update_values(spreadsheet_id, new_datas)

# ranges = ["Лист1!A2:H8"] # 

# # Если все прошло без ошибок — на экран будет выведена ссылка на таблицу. 

# give_access(spreadsheetId, email=email)

