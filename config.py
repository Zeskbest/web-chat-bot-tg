def from_file(fname: str):
    with open(f'./{fname}') as f:
        return f.read().strip()


class Config:
    web_login, web_pwd = from_file(".web.login.pwd").split()
    tg_token = from_file(".tg.token")
