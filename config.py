def from_file(fname: str):
    with open(f'./{fname}') as f:
        return f.read().strip()


class Config:
    gpt_login, gpt_pwd = from_file(".gpt.login.pwd").split()
    tg_token = from_file(".tg.token")
