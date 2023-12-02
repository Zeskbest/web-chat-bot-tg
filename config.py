def from_file(fname: str):
    with open(f'./{fname}') as f:
        return f.read().strip()


class Config:
    gpt_org = from_file(".gpt.org")
    gpt_secret = from_file(".gpt.secret")
    tg_token = from_file(".tg.token")
