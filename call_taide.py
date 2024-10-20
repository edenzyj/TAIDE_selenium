from selenium import webdriver
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys

import os
import time

class wait_for_text_to_stabilize:
    def __init__(self, locator, timeout=10):
        self.locator = locator
        self.timeout = timeout  # Time (in seconds) to wait for text to stabilize

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        current_text = element.text
        
        # Wait for the text to stop changing
        WebDriverWait(driver, self.timeout).until(
            lambda d: element.text == current_text and len(element.text) > 0
        )
        
        # After text stabilizes, return the element
        return element


class taideParser:
    def __init__(self,
                 driver,
                 gpt_url: str = 'https://demetergptv2.nlpnchu.org/'):
       
        # Start a webdriver instance and open Shennong TAIDE
        self.driver = driver
        self.driver.get(gpt_url)

    @staticmethod
    def get_driver():
        # options = uc.ChromeOptions()
        # options.add_argument("--incognito")
        # driver = uc.Chrome()
        
        driver = webdriver.Chrome()
        
        return driver

    def __call__(self, msg: str):
        # Find the input field and send a question
        input_field = self.driver.find_element(By.ID, 'search_input')
        input_field.send_keys(msg)
        time.sleep(5)
        
        button = self.driver.find_element(By.ID, 'just_load_please')
        button.click()

    def read_respond(self):
        try:
            answer = WebDriverWait(self.driver, 100).until(
                wait_for_text_to_stabilize((By.ID, 'myElement'))
            )
            response = answer.text
            print(response)
            print("++++++++++")
            return response
        except:
            return None

    def close(self):
        self.driver.quit()


class translateParser:
    def __init__(self,
                 driver,
                 gpt_url: str = 'https://translate.google.com/?sl=zh-TW&tl=en&op=translate'):
       
        # Start a webdriver instance and open Google translation
        self.driver = driver
        self.driver.get(gpt_url)

    @staticmethod
    def get_driver():
        # options = uc.ChromeOptions()
        # options.add_argument("--incognito")
        # driver = uc.Chrome()
        
        driver = webdriver.Chrome()
        
        return driver

    def __call__(self, msg: str):
        # Find the input field and send a question
        input_field = self.driver.find_elements(By.CSS_SELECTOR, 'textarea[aria-label="原文"]')[0]
        input_field.send_keys(msg)

    def read_respond(self):
        try:
            answer = WebDriverWait(self.driver, 10).until(
                wait_for_text_to_stabilize((By.CSS_SELECTOR, 'span.ryNqvb[jsname="W297wb"]'))
            )
            response = answer.text
            print(response)
            print("==========")
            return response
        except:
            return None

    def close(self):
        self.driver.quit()

        
def ask_taide_for_answer(question, num, fw):
    print(question)
    print("----------")
    
    driver = taideParser.get_driver()
    taide_parser = taideParser(driver)

    time.sleep(5)
    taide_parser(question)
    
    time.sleep(5)
    response = taide_parser.read_respond()
    
    driver.close()
    
    if response is None:
        fw.write("Answwer {} :\n".format(num))
        fw.write("No answer is geneerated.")
        fw.write("\n\n")
        return
    
    response = response.replace("\n", " ")
    response = response.replace("。", "，")
    
    driver = translateParser.get_driver()
    trans_parser = translateParser(driver)
    
    time.sleep(5)
    trans_parser(response)
    
    time.sleep(5)
    answer = trans_parser.read_respond()
    
    driver.close()
    
    if answer is None:
        fw.write("Answwer {} :\n".format(num))
        fw.write("No answer is geneerated.")
        fw.write("\n\n")
        return
        
    fw.write("Answwer {} :\n".format(num))
    fw.write(answer)
    fw.write("\n\n")

    return


input_dir = "input_file/"
output_dir = "output_file/"

if __name__ == "__main__":
    question_file = input_dir + "questions_100.txt"
    
    question_list = []
    
    with open(question_file, 'r') as qfr:
        for quest in qfr.read().split('\n'):
            question_list.append(quest)
        qfr.close()
    
    output_dir = output_dir + "1st_answers/"
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    
    file_out = output_dir + "taide_100Q_1st_Ans.txt"
    
    with open(file_out, 'w') as fw:
        for i in range(len(question_list)):
            ask_taide_for_answer(question_list[i], i, fw)
            time.sleep(1)
