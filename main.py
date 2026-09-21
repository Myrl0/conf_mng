def command(a): 
    b = a.split()
    if len(b) == 0:
        return "VFS % Напишите команду"
    elif b[0] == "cd":
        return b
    elif b[0] == "ls":
        return b
    elif a == "exit":
        exit()
    else:
        return "VFS % Неизвестная команда"

a = input("VFS % ")
while a != "exit":
    a = input("VFS % ")
    print(f"VFS $ {command(a)}")