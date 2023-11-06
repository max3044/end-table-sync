import os
import traceback
import pickle
import time
from bs4 import BeautifulSoup
import lxml
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys 
import json
import requests
from utils.events import split_next_date, get_current_state
from datetime import datetime
import pytz
class MySelenium:

    def __init__(self, headless=True, is_save_auth=False):
            
        service = Service(executable_path=ChromeDriverManager().install())

        self.base_url = "https://kad.arbitr.ru"
        self.options = Options()
        self.options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")      
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')  
        self.options.add_argument("--disable-extensions")
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--disable-dev-shm-usage')


        # обновление авторизации только в браузере!
        if headless and not is_save_auth:
            self.options.add_argument('--headless')



        self.driver = webdriver.Chrome(service=service, options=self.options)
        
        self.cookies_path = os.path.join(os.getcwd(), "data", "cookies.pickle")

        if is_save_auth:
            self.update_auth()


    def load_pickles(self):
        """
        just loads last pickles
        """
        with open(self.cookies_path, "rb") as file:
            pickles = pickle.load(file) 
        return pickles

    def get_last_authentication(self):
        """
        returns last auth data cookie
        """

        pickles = self.load_pickles()

        res = [i for i in pickles if i['name'] == ".ASPXAUTH"]

        if len(res) > 0:
            return res[0]


    def update_cookies(self):
        """
        updates cookies in general without auth data
        """
        try:
            # заходим на общую страницу, чтобы получить куки
            self.driver.get(self.base_url)
            time.sleep(5)
            self.cookies = self.driver.get_cookies()
            
            # добавляем последние записанные данные авторизации
            last_auth = self.get_last_authentication()

            if last_auth:
                self.cookies.append(last_auth)
            
            # обновляем консервы
            with open(self.cookies_path, "wb") as file:
                pickle.dump(self.cookies, file)
        
        except Exception:
            print(f"[ERROR]: \n\n{traceback.format_exc()}")
   
       
        print("[LOG]: успешно обновил куки")

    def set_cookies(self):
        """
        just sets cookies (only after loading page!)

        """
        self.cookies = self.load_pickles()
        for cookie in self.cookies:
            self.driver.add_cookie(cookie)

        self.driver.refresh()
        time.sleep(5)
        print("[LOG]: успешно загрузил куки")

    def update_auth(self):
        
        try:
            # только в режиме браузера!

            self.driver.get(self.base_url)
            time.sleep(60*2)
            self.cookies = self.driver.get_cookies()
            with open(self.cookies_path, "wb") as file:
                pickle.dump(self.cookies, file)
            print("[LOG]: успешно обновил айди авторизации и куки")
        except Exception:
            print(f"[ERROR]: \n\n{traceback.format_exc()}")
        finally:
            self.quit() 
            
    def quit(self):
        print("[LOG]: Заканчиваю")
        self.driver.close() # закрывает страницу
        self.driver.quit() # закрывает браузер

    def pars_doc(self,doc):
        """
        parses doc to usefull data
        """
        date = doc.find_element(By.CLASS_NAME, "l-col").find_element(By.CLASS_NAME, "case-date").text
        case_type = doc.find_element(By.CLASS_NAME, "l-col").find_element(By.CLASS_NAME, "case-type").text
        additional_info = doc.find_element(By.CLASS_NAME, "additional-info").text
        subject = doc.find_element(By.CLASS_NAME, "case-subject").text
        doc_result= doc.find_element(By.CLASS_NAME, "b-case-result").text
        
        next_date = split_next_date(additional_info) # добавляем следующую дату
        cur_state =get_current_state(doc_result) 
        return dict(
            date=date,
            case_type=case_type,
            additional_info=additional_info,
            subject=subject,
            doc_result=doc_result,
            next_date=next_date,
            cur_state=cur_state

        )
    
    def get_general_next_date(self,ndates):

        """
        gets last next date for case
        """
        # получаем основную последнюю дату
        general_next_date = None
        for nd in sorted(ndates, reverse=True):
            if nd > datetime.now(pytz.timezone("Europe/Samara")).date():
                general_next_date = nd
                break
        return general_next_date
    def get_pages(self):
        try:
            pages =self.driver.find_element(By.XPATH, '//*[@id="chrono_list_content"]/div[2]/div[2]/ul')
            pages = [int(i.text) for i in pages.find_elements(By.TAG_NAME, "li") if i.text.isdigit()]
        except Exception:
            pages = [1]
        return pages
    
    def search(self):
        try:
        
            # self.update_cookies()
            # self.set_cookies()
            results=[]
            for case in ["А73-19161/2020", "А55-5885/2023", "А75-19194/2020"]:
                
                uri = f"https://kad.arbitr.ru/Card?number={case}"
                self.driver.get(uri)
                time.sleep(5)

                self.driver.execute_script("document.getElementsByClassName('form-one-widget__root')[0].style.display = 'none';")
                # self.driver.execute_script("document.getElementsByClassName('gr-content')[0].style.display = 'none';")
        
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # блок со всеми инстанциями
                instances_block = self.driver.find_element(By.ID, "chrono_list_content")
                # первая инстанция идёт последней
                first_floor = instances_block.find_elements(By.CLASS_NAME, "b-chrono-item-header")[-1].find_element(By.CLASS_NAME, "container")
                
                # последний див - кнопка
                first_floor.find_element(By.CLASS_NAME, "b-collapse").click()
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                # получаем страницы
                
                info = []
                ndates = []
                states = []

                html = self.driver.find_element(By.TAG_NAME, 'html')
                html.send_keys(Keys.END)
                pages = self.get_pages()
                for p in pages:
                    if p >1:
                        field = self.driver.find_element(By.XPATH, '//*[@id="chrono_list_content"]/div[2]/div[2]/div[1]/div/input')
                        field.click()
                        time.sleep(2)
                        field.clear()
                        field.send_keys(p)
                        field.send_keys(Keys.ENTER)
                        html.send_keys(Keys.UP)

                        time.sleep(2)

                    #chrono_ed_content > div > ul
                    main_field=self.driver.find_element(By.CLASS_NAME, "b-chrono-items-container")
                   
                    # ищем все документы из карточки дела
                    docs =main_field.find_elements(By.CLASS_NAME, "b-chrono-item")

                    for doc in docs:
                        # получаем необработанный результат с данными
                        pure_res = self.pars_doc(doc)
                        info.append(pure_res)
                        # выделяем текущую стадию и следующую дату
                        if pure_res["cur_state"]:
                            states.append(pure_res["cur_state"]) # добавляем стадию
                        if pure_res["next_date"]:
                            ndates.append(pure_res["next_date"])
                   

                # от новых к старым: первая стадия - текущая
                current_state = states[0]
                general_next_date =self.get_general_next_date(ndates) 
                result = {
                    "info": info,
                    "next_date": datetime.strftime(general_next_date, "%d.%m.%Y") if general_next_date else "",
                    "current_state": current_state
                }
                results.append(result)
                time.sleep(5)
                    

        except Exception:
            print(f"[ERROR]: \n\n{traceback.format_exc()}")
        finally:
            self.quit() 

ms = MySelenium(headless=False, is_save_auth=False)

ms.search()