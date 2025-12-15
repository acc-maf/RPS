from random import randint


def sort(arr):
    sort_arr = arr.copy()
    for i in range(1, len(sort_arr)):
        element = sort_arr[i]
        j = i - 1

        while j >= 0 and sort_arr[j] > element:
            sort_arr[j + 1] = sort_arr[j]
            j -= 1

        sort_arr[j + 1] = element
    return sort_arr


def save(str_save, filename):
    with open(filename, "w", encoding="utf-8") as f:
        str_save
        f.write(str_save)


def load(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read().strip()

    return [int(x) for x in data.split()] if data else []


if __name__ == "__main__":
    while True:
        menu = int(input("""
Выберите пункт меню:
1 - Ввод массива вручную
2 - Генерация массива случайных чисел
3 - Загрузка массива из файла
Другое число - Выход из программы
"""))
        arr = list()
        match menu:
            case 1:
                inp = input("Введите массив целых чисел через запятую -> ")
                arr = inp.split(',')
                flag = False
                for i in range(len(arr)):
                    try:
                        arr[i] = int(arr[i].strip())
                    except:
                        print("Вы ввели не целые числа!")
                        flag = True
                        break
                if flag:
                    continue
            case 2:
                n = randint(3, 30)
                arr = [randint(-100, 100) for i in range(n)]
            case 3:
                name = input("Введи"
                             "те имя файла: ")
                try:
                    arr = load(name)
                except:
                    print("Неверное имя файла")
                    continue
            case _:
                break

        print(arr)
        sorted_arr = sort(arr)
        print(sorted_arr)

        while True:
            menu = int(input("""Выберите пункт меню:
1 - Сохранить начальный массив в файл
2 - Сохранить отсортированный массив в файл
3 - Сохранить оба массива в файлы
Другое число - Не сохранять
"""))
            match menu:
                case 1:
                    name = input("Введите путь файла -> ")
                    try:
                        save(" ".join(str(x) for x in arr), name)
                        print("Успешно\n")
                        break
                    except:
                        print("Неверный путь файла")
                        continue
                case 2:
                    name = input("Введите путь файла -> ")
                    try:
                        save(" ".join(str(x) for x in sorted_arr), name)
                        print("Успешно\n")
                        break
                    except:
                        print("Неверный путь файла")
                        continue
                case 3:
                    name = input("Введите путь файла для сохранения массивов -> ")
                    save_str = 'Начальный массив: ' + " ".join(str(x) for x in arr) + '\nОтсортированный массив: '+ " ".join(str(x) for x in sorted_arr)
                    try:
                        save(save_str, name)
                        print("Успешно\n")
                        break
                    except:
                        print("Неверный путь файла")
                        continue
                case _:
                    break
