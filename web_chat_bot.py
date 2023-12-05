import asyncio
import base64
import inspect
import pickle
from functools import wraps
from pathlib import Path
from time import sleep
from typing import Callable, Awaitable
from warnings import warn

import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, UnableToSetCookieException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.poolmanager import PoolManager

from config import Config
from tg_conversation import Question

# def _mpa(self, override):
#     if override is None:
#         override = {"timeout": 60.}
#     return _mpa_old(self, override)
#
#
# PoolManager._merge_pool_kwargs, _mpa_old = _mpa, PoolManager._merge_pool_kwargs

COOKIE_FILE = Path(__file__).parent / "cookies.pkl"

URL = base64.b64decode(b'aHR0cHM6Ly9jaGF0Lm9wZW5haS5jb20=').decode()

# def cookie_save(f):
#     if inspect.iscoroutinefunction(f):
#         @wraps(f)
#         async def real_f(*a, **kw):
#             res = await f(*a, **kw)
#             with open(COOKIE_FILE, "wb") as fn:
#                 pickle.dump(a[0].driver.get_cookies(), fn)
#             return res
#     else:
#         @wraps(f)
#         def real_f(*a, **kw):
#             res = f(*a, **kw)
#             with open(COOKIE_FILE, "wb") as fn:
#                 pickle.dump(a[0].driver.get_cookies(), fn)
#             return res
#
#     return real_f


KEYS_TO_PRESS = {
    "left": Keys.LEFT,
    "right": Keys.RIGHT,
    "tab": Keys.RIGHT,
    "enter": Keys.ENTER,
    "space": Keys.SPACE,
    "exit": None,
}


class WebChatBot:

    # def load_cookies(self):
    #     try:
    #         with open(COOKIE_FILE, "rb") as f:
    #             cookies = pickle.load(f)
    #     except FileNotFoundError:
    #         return
    #     for idx, cookie in enumerate(cookies):
    #         try:
    #             self.driver.add_cookie(cookie)
    #         except UnableToSetCookieException:
    #             warn(f"Failed to load some cookies: {idx}/{len(cookies)}: {cookie}")

    def __init__(self, ask_human: Callable[[bytes, str, list[str]], Awaitable[str]]):
        self.username = Config.web_login
        self.password = Config.web_pwd
        # options = Options()
        # options.add_argument("--auto-open-devtools-for-tabs")
        # options.add_argument("--headless")
        # self.driver = webdriver.Firefox(options=options)
        # self.driver = webdriver.PhantomJS(desired_capabilities={"browserName": "Chrome","version": "13.0.782.41","platform": "Linux x86_64","javascriptEnabled": True,},service_args=["--disk-cache=true", "--ignore-ssl-errors=true", "--ssl-protocol=ANY"],)
        options = Options()
        # options.add_argument("--auto-open-devtools-for-tabs")
        options.add_argument("--headless")
        options.add_argument("--user-data-dir=./chrome_driver")
        # self.driver = webdriver.Chrome(options=chrome_options)
        self.driver = uc.Chrome(options=options, use_subprocess=True)  # todo false
        # self.driver.get(URL)
        # self.load_cookies()
        self.ask_human = ask_human

    def wait_for(self, condition):
        WebDriverWait(self.driver, timeout=10).until(condition)

    async def init(self):
        self.driver.get(URL)
        await asyncio.sleep(1)
        if self.need_to_login():
            await self.login()

    def _get_login_button(self):
        login_buttons = self.driver.find_elements(By.XPATH, "//button[1]/div")
        return next((b for b in login_buttons if b.text == 'Log in'), None)

    def need_to_login(self) -> bool:
        self.wait_for(lambda d: d.find_elements(By.XPATH, '//button'))
        login_button = self._get_login_button()
        return login_button is not None

    async def human_press(self):
        while True:
            img = self.driver.get_screenshot_as_png()
            key = await self.ask_human(img, 'Which key?', list(KEYS_TO_PRESS))
            if key == "exit":
                break
            else:
                key_to_press = KEYS_TO_PRESS[key]
                self.driver.switch_to.active_element.send_keys(key_to_press)

    async def recapcha(self):
        begin_puzzle_btns = self.driver.find_elements(By.XPATH, "//button")
        begin_puzzle_btn = next((b for b in begin_puzzle_btns if b.text == 'Begin puzzle'), None)
        if begin_puzzle_btn is None:
            return
        begin_puzzle_btn.click()
        await self.human_press()

    # @cookie_save
    async def login(self):
        # input("Need Login")
        # return
        login_button = self._get_login_button()
        login_button.click()
        await asyncio.sleep(1)
        try:
            self.wait_for(lambda d: d.find_elements(By.ID, "username"))
        except TimeoutException:
            await self.human_press()
        username = self.driver.find_element(By.ID, "username")
        username.send_keys(self.username)
        username.send_keys(Keys.ENTER)
        self.wait_for(lambda d: d.find_elements(By.ID, "password"))
        password = self.driver.find_element(By.ID, "password")
        password.send_keys(self.password)
        password.send_keys(Keys.ENTER)
        try:
            self.wait_for(lambda d: 'auth' not in d.current_url)
        except TimeoutException:
            await self.recapcha()

    def change_url(self, url):
        if self.driver.current_url != url:
            self.driver.get(url)
            sleep(1)

    # @cookie_save
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
            sleep(3)
        if chat_id is None:
            chat_id = self.driver.current_url.split('/')[-1]
        return result, chat_id


def apply_grid(im, step_size=100):
    from PIL import ImageDraw
    draw = ImageDraw.Draw(im)
    for coord in range(0, im.width, step_size):
        line = ((coord, 0), (coord, im.height))
        draw.line(line, fill=128)
        line = ((0, coord), (im.width, coord))
        draw.line(line, fill=128)
    return im


async def ask_human(img, text, options):
    import io
    from PIL import Image
    q = Question(img, text, options)
    apply_grid(Image.open(io.BytesIO(img))).show()
    opts = '\n'.join(f'{i}: {o}' for i, o in enumerate(options))
    i = input(f"{text}\n{opts}\n").strip()
    if i.isdigit():
        q.set_answer(options[int(i)])
    else:
        q.set_answer(i)
    return await q.get_answer()


async def main():
    web = WebChatBot(ask_human)
    try:
        await web.init()
        # answer = web.ask("What's the most effective weather prediction?")
        answer = web.ask("Give me a list of his books (minimum 12).",
                         "6783dccd-ecfd-40cf-9f24-589ef581ed34")
        print(answer)
    finally:
        import io
        from PIL import Image
        Image.open(io.BytesIO(web.driver.get_screenshot_as_png())).show()


if __name__ == '__main__':
    asyncio.run(main())
