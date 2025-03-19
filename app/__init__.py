with open("op_password.txt") as f:
    op_password = f.read().strip()
    print(f'op_password:{op_password}')

from routes import app



