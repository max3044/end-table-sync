# Подключаем библиотеки
import httplib2 
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials	

""""
В каждом файле (spreadsheet) находятся листы-вкладки (sheet).
Каждый sheet имеет свой числовой код (sheetId). 
У первого созданного в документе листа этот Id равен 0.
Остальные листы имеют сильно отличные от нуля Id (т.е. они не нумеруются подряд).
"""


CREDENTIALS_FILE = 'my-law-project-1-36975dc6c026.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 


spreadsheet = service.spreadsheets().create(body = {
    'properties': {'title': 'Первый тестовый документ', 'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Лист номер один',
                               'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
}).execute()
spreadsheetId = spreadsheet['spreadsheetId'] # сохраняем идентификатор файла
print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)

def give_access(spreadsheetId):
    driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API
    access = driveService.permissions().create(
        fileId = spreadsheetId,
        body = {'type': 'user', 'role': 'writer', 'emailAddress': 'maximkovalunas@gmail.com'},  # Открываем доступ на редактирование
        fields = 'id'
    ).execute()

# Если все прошло без ошибок — на экран будет выведена ссылка на таблицу. 
email="service-account-me@my-law-project-1.iam.gserviceaccount.com"