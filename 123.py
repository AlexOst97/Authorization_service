
import random
import string

def generate_invite_code(length=6):
    """Генерация случайного 6-значного кода (цифры + буквы)"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


x = generate_invite_code()
print(x)