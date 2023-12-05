import asyncio
import base64
from time import sleep

import undetected_chromedriver as uc
from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from config import Config

URL = base64.b64decode(b'aHR0cHM6Ly9jaGF0Lm9wZW5haS5jb20=').decode()


class WebChatBot:

    def __init__(self):
        self.username = Config.web_login
        self.password = Config.web_pwd
        options = Options()
        Display(visible=False, size=(800, 800)).start()  # instead of options.add_argument("--headless")
        options.add_argument("--user-data-dir=./chrome_driver")
        self.driver = uc.Chrome(options=options, use_subprocess=True)  # todo false
        try:
            self.driver.get(URL)
            sleep(1)
            if self.need_to_login():
                self.login()
        except Exception:
            with open('./driver.png', 'wb') as f:
                f.write(self.driver.get_screenshot_as_png())
            raise

    def wait_for(self, condition):
        WebDriverWait(self.driver, timeout=60).until(condition)

    def _get_login_button(self):
        login_buttons = self.driver.find_elements(By.XPATH, "//button[1]/div")
        return next((b for b in login_buttons if b.text == 'Log in'), None)

    def need_to_login(self) -> bool:
        self.wait_for(lambda d: d.find_elements(By.XPATH, '//button'))
        login_button = self._get_login_button()
        return login_button is not None

    def login(self):
        login_button = self._get_login_button()
        login_button.click()
        sleep(1)
        self.wait_for(lambda d: d.find_elements(By.ID, "username"))
        username = self.driver.find_element(By.ID, "username")
        username.send_keys(self.username)
        username.send_keys(Keys.ENTER)
        self.wait_for(lambda d: d.find_elements(By.ID, "password"))
        password = self.driver.find_element(By.ID, "password")
        password.send_keys(self.password)
        password.send_keys(Keys.ENTER)
        self.wait_for(lambda d: 'auth' not in d.current_url)

    def change_url(self, url):
        if self.driver.current_url != url:
            self.driver.get(url)
            sleep(1)

    def ask(self, text: str, chat_id: str = None) -> [str, str]:
        def get_answers():
            return self.driver.find_elements(By.XPATH, '//div[contains(@class, "agent-turn")]')

        if chat_id:
            self.change_url(f"{URL}/c/{chat_id}")
        else:
            self.change_url(URL)

        prompt = self.driver.find_element(By.ID, "prompt-textarea")
        prompt.send_keys(text)
        was_answers = len(get_answers())
        prompt.send_keys(Keys.ENTER)
        self.wait_for(lambda d: was_answers != len(get_answers()))
        if chat_id is None:
            sleep(1)

        answer = get_answers()[-1]
        self.wait_for(lambda d: answer.text.strip() not in ("", "ChatGPT"))
        result = ""
        while result != answer.text:
            result = answer.text
            sleep(5)
        if chat_id is None:
            chat_id = self.driver.current_url.split('/')[-1]
        return result, chat_id


async def main():
    web = WebChatBot()
    answer, chat = web.ask("What is the biggest dog in the world?")
    print(answer)
    answer = web.ask("Describe the species?", chat)
    assert 'dog' in answer
    print(answer)


if __name__ == '__main__':
    asyncio.run(main())
