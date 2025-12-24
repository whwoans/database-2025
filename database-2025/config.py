import os
from dotenv import load_dotenv

load_dotenv()

# SECRET_KEY = 'my-super-secret-key'

def get_env_variable(name, default=None, allow_empty=False):
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"환경 변수 '{name}'가 설정되지 않았습니다.")
    if not allow_empty and value == '':
        # DB_PASSWORD가 비어있으면 DB_ROOT_PASSWD를 시도
        if name == 'DB_PASSWORD':
            root_passwd = os.getenv('DB_ROOT_PASSWD', '')
            if root_passwd:
                return root_passwd
        raise ValueError(f"환경 변수 '{name}'가 비어있습니다.")
    return value

DB_CONFIG = {
    'host': get_env_variable('DB_HOST'),
    'user': get_env_variable('DB_USER'),
    'password': get_env_variable('DB_PASSWORD', allow_empty=True),  # 비밀번호는 빈 문자열 허용, DB_ROOT_PASSWD로 대체 가능
    'database': get_env_variable('DB_NAME')
}