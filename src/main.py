def command(a):
    b = a.split()
    if len(b) == 0:
        return "Введите команду"
    elif b[0] == "cd":
        return b
    elif b[0] == "ls":
        return b
    elif a == "exit":
        exit()
    else:
        return "Неизвестная команда"


if __name__ == "__main__":
    while True:
        a = input("VFS % ")
        print(f"VFS $ {command(a)}")