#Importing packages
import os, sys
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

project_root               = os.path.dirname(os.path.abspath(__file__))
parliamentInfo_path        = project_root + '/ParliamentInfo.xlsx'
parliamentCompletInfo_path = project_root + '/ParliamentCompleteInfo.xlsx'

def save_excel (database=pd.DataFrame(), file_name=''):

    writer = pd.ExcelWriter(project_root+'/{0}.xlsx'.format(file_name))
    database.to_excel(writer, encoding='utf-8', index=False, header=True) 
    writer.save()
    writer.close()
    print ('File: {0}.xlsx saved on output folder'.format(file_name))

def scrating_deputies ():

    url = 'https://www.parlamento.pt/DeputadoGP/Paginas/DeputadosemFuncoes.aspx'
    #open an url in google chrome
    driver = webdriver.Chrome(
        executable_path=project_root + "/chromedriver.exe")

    driver.get(url)
    driver.maximize_window()
    time.sleep(3)
    driver.find_element(By.XPATH, './/*[@id="cconsent-bar"]/div/div[2]/div/div[3]/button').click() #cookies

    db_parliament = pd.DataFrame()

    page = 1
    while page > 0:

        ## find elements with div - class="row margin_h0 margin-Top-15"
        list_deputies = driver.find_elements(By.XPATH, '*//div[@class="row margin_h0 margin-Top-15"]')
        
        for deputy in list_deputies:

            list_components = deputy.find_elements(By.XPATH, './/div[@class="col-xs-12 col-lg-4 ar-no-padding"]')

            link     = ""
            name     = ""
            circelec = ""
            partido  = ""

            for component in list_components:

                label = component.find_element(By.XPATH, './/div[@class="TextoRegular-Titulo"]').text
                #print (label)

                if label == "Nome":
                    link = component.find_element(By.XPATH, './/a').get_attribute('href')
                    name = component.find_element(By.XPATH, './/a').text
                    #print (link)
                    #print (name)
                elif label == "Círculo Eleitoral":
                    circelec = component.find_element(By.XPATH, './/span').text
                    #print (circelec)
                elif label == "Grupo Parlamentar / Partido":
                    partido = component.find_element(By.XPATH, './/span').text
                    #print (partido)
                elif label == "Registo de Interesses":
                    break
                else:
                    continue

            parliament_obj = {
                'Name'                        : name,
                'Link'                        : link,
                'Círculo Eleitoral'           : circelec,
                'Grupo Parlamentar / Partido' : partido,
            }
            
            db_parliament = db_parliament.append(parliament_obj, ignore_index=True)
        
        save_excel(db_parliament, 'ParliamentInfo')
        page += 1
        print (page)
        pager_component = driver.find_element(By.XPATH, './/div[@class="pager"]')

        if page == 11:
            pager_component.find_element(By.XPATH, './/span/a[text()=">"]').click()
            time.sleep(3)
        else:
            page_str = pager_component.find_element(By.XPATH, './/span/a[text()="' + str(page) + '"]').text
            print (page_str)
            pager_component.find_element(By.XPATH, './/span/a[text()="' + str(page) + '"]').click()
            time.sleep(3)

    driver.quit()

    save_excel(db_parliament, 'ParliamentInfo')

def scrating_deputiesInfo ():

    db_parliament     = pd.DataFrame(pd.read_excel(parliamentInfo_path))
    db_parliamentInfo = pd.DataFrame()

    for deputy_index, deputy_row in db_parliament.iterrows():

        fullname = ""
        birthday = ""
        course   = ""
        job      = ""

        deputy_link = deputy_row['Link']

        driver = webdriver.Chrome(
        executable_path=project_root + "/chromedriver.exe")

        driver.get(deputy_link)
        driver.maximize_window()

        list_info = driver.find_elements(By.XPATH, '*//div[@class="TextoRegular-Titulo"]')
        
        for info in list_info:

            label = info.find_element(By.XPATH, './/div[@class="TitulosBio AlinhaL"]/span').text
            print (label)

            if label == "Nome completo":
                fullname = info.find_element(By.XPATH, './/div[@class="TextoRegular AlinhaL"]/span').text
                print (fullname)
            elif label == "Data de nascimento":
                birthday = info.find_element(By.XPATH, './/div[@class="TextoRegular AlinhaL"]/span').text
                print (birthday)
            elif label == "Habilitações literárias":
                coursestr = ""
                course = info.find_elements(By.XPATH, './/div[@class="TextoRegular AlinhaL"]/span')
                for level in course:
                    coursestr += ',' + level.text
                print(coursestr)
            elif label == "Profissão":
                job = info.find_element(By.XPATH, './/div[@class="TextoRegular AlinhaL"]/span').text
                print (job)
            elif label in ["Cargos que desempenha", "Cargos exercidos"]:
                break
            else:
                continue

        parliamentInfo_obj = {
            'Legislatura'                 : 2019,
            'Nome'                        : deputy_row['Name'],
            'Nome completo'               : fullname,
            'Data de nascimento'          : birthday,
            'Habilitações literárias': coursestr,
            'Profissão'                   : job,
            'Círculo Eleitoral'           : deputy_row['Círculo Eleitoral'],
            'Grupo Parlamentar / Partido' : deputy_row['Grupo Parlamentar / Partido'],
        }
        
        db_parliamentInfo = db_parliamentInfo.append(parliamentInfo_obj, ignore_index=True)

        save_excel(db_parliamentInfo, 'ParliamentCompleteInfo')
        
        driver.quit()

    save_excel(db_parliamentInfo, 'ParliamentCompleteInfo')
    
if __name__ == "__main__":

    scrating_deputies () #comment this after creating the first dataset and run again to create a new dataset 'ParliamentCompleteInfo' and full info
    scrating_deputiesInfo ()
