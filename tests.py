import sqlite3
import random
import time
import pytest
import main

TEST_DB = "test_arrays.db"


@pytest.fixture(scope="function")
def setup_test_db():
    # Сохраняем оригинальный DB_NAME
    original_db = main.DB_NAME
    main.DB_NAME = TEST_DB

    # Инициализация тестовой БД
    main.init_db()

    # Создаём тестового пользователя
    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (id, login, password) VALUES (?, ?, ?)", (1, "testuser", "pass"))
    conn.commit()
    conn.close()

    yield

    # Очистка после теста
    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS user_arrays")
    cur.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    conn.close()

    # Восстанавливаем оригинальный DB_NAME
    main.DB_NAME = original_db


@pytest.mark.parametrize("num_arrays", [100, 1000, 10000])
def test_add_arrays(setup_test_db, num_arrays):
    user_id = 1  # тестовый пользователь

    start_time = time.time()
    success = True
    try:
        for _ in range(num_arrays):
            arr = [random.randint(-1000, 1000) for _ in range(random.randint(5, 20))]
            main.save_array(user_id, arr, False)
    except Exception as e:
        print("Ошибка при добавлении массивов:", e)
        success = False
    elapsed = time.time() - start_time

    print(
        f"Добавление {num_arrays} массивов прошло: {'Успешно' if success else 'Не успешно'}; Время: {elapsed:.2f} сек")

    # Проверяем количество записей
    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM user_arrays")
    count = cur.fetchall()[0][0]
    conn.close()
    print(count, num_arrays)

    assert success and count == num_arrays


@pytest.mark.parametrize("num_arrays", [100, 1000, 10000])
def test_load_and_sort_100_arrays(setup_test_db, num_arrays):
    test_add_arrays(setup_test_db, num_arrays)
    user_id = 1  # тестовый пользователь

    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()

    # Получаем все массивы пользователя
    cur.execute("SELECT arr FROM user_arrays WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()

    if len(rows) < 100:
        raise ValueError("В базе меньше 100 массивов для теста")

    # Выбираем 100 случайных массивов
    selected_rows = random.sample(rows, 100)

    success = True
    start_time = time.time()
    total_sort_time = 0.0

    try:
        for row in selected_rows:
            arr = list(map(int, row[0].split(',')))
            t0 = time.time()
            sorted_arr = main.insertion_sort(arr)
            t1 = time.time()
            total_sort_time += (t1 - t0)
    except Exception as e:
        print("Ошибка при выгрузке или сортировке:", e)
        success = False

    elapsed = time.time() - start_time
    avg_time = total_sort_time / len(selected_rows) if success else None

    print(f"Тест выгрузки и сортировки 100 массивов: {'Успешно' if success else 'Не успешно'}")
    print(f"Общее время выполнения теста: {elapsed:.2f} сек")
    print(f"Среднее время сортировки 1 массива: {avg_time:.4f} сек" if avg_time else "")

    assert success


def test_clear_user_arrays(setup_test_db):
    user_id = 1  # тестовый пользователь

    start_time = time.time()
    success = True

    try:
        main.clear_array(user_id)
    except Exception as e:
        print("Ошибка при очистке базы данных:", e)
        success = False

    elapsed = time.time() - start_time

    # Проверка, что база действительно очищена
    conn = sqlite3.connect(main.DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM user_arrays WHERE user_id=?", (user_id,))
    count = cur.fetchone()[0]
    conn.close()

    if count != 0:
        success = False

    print(f"Тест очистки базы данных: {'Успешно' if success else 'Не успешно'}")
    print(f"Общее время выполнения теста: {elapsed:.2f} сек")

    assert success
