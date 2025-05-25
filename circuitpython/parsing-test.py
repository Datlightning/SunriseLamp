colors = []
with open("python/led-colors.txt", "r") as file:
    for line in file.read().split("\n"):
        colors.append(eval(line[3:]))
print(colors)