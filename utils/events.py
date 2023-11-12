from datetime import datetime
from enum import Enum
additional_info = "Дата и время судебного заседания 25.09.2023, 11:20, 506"





def split_next_date(additional_info):
    if "Дата и время судебного заседания" in additional_info:
        additional_info= additional_info.strip()
        additional_info= "".join(additional_info.split("Дата и время судебного заседания")[-1])
        additional_info=additional_info.replace("Дата и время судебного заседания", "")
        additional_info= additional_info.strip()
        additional_info = additional_info.split(",")
        next_date = additional_info[0]
        next_date = datetime.strptime(next_date, "%d.%m.%Y").date()
        return next_date




def get_current_state(_result):

    result = _result.lower()
    if "Освободить гражданина от исполнения обязательств".lower() in result or "Освобождении гражданина от исполнения обязательств".lower() in result:
        state = "<ЗАВЕРШЕНО>"
    elif "Ввести процедуру реструктуризации".lower() in result or "Введении процедуру реструктуризации".lower() in result:
        state = "<РЕСТРУКТУРИЗАЦИЯ>"
    elif "Ввести процедуру реализации".lower() in result or "Введении процедуры реализации".lower() in result:
        state = "<РЕАЛИЗАЦИЯ>"
    elif "Назначить судебное заседание по рассмотрению обоснованности".lower() in result or "Назначении судебного заседания по рассмотрению обоснованности".lower() in result: 
        state = "<ДОКУМЕНТЫ ОТПРАВЛЕНЫ>"
    elif "Прекратить производство".lower() in result or "Прекращении производства".lower() in result: 
        state = "<ПРОИЗВОДСТВО ПРЕКРАЩЕНО>"
    else: 
        state = ""
    return state
 