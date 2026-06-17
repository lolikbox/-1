# ЛР_6 Индивидуальная часть задания 
import os
import time
import random
import json
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


# Конфигурация из переменных окружения (имитация)

REGISTRY_USER = os.environ.get("REGISTRY_USER", "container_user")
REGISTRY_PASSWORD = os.environ.get("REGISTRY_PASSWORD", "secret")
SIGN_KEY = os.environ.get("SIGN_KEY", "key123")
DB_USER = os.environ.get("DB_USER", "db_user")
DB_PASS = os.environ.get("DB_PASS", "db_pass")
# Режим: "block" - блокировать некорректные, "audit" - только протоколировать
OPERATION_MODE = os.environ.get("OP_MODE", "block")


# Схема валидации (упрощённая JSON Schema)

VALIDATION_SCHEMA = {
    "type": "object",
    "required": ["id", "amount", "date"],
    "properties": {
        "id": {"type": "integer"},
        "amount": {"type": "number", "minimum": 0},
        "date": {"type": "string", "format": "date"}
    }
}


# Класс валидатора

class TransactionValidator:
    def __init__(self, schema):
        self.schema = schema

    def validate(self, transaction: dict) -> (bool, list):
        """
        Возвращает (is_valid, [список сообщений об ошибках])
        """
        errors = []
        # Проверка наличия обязательных полей
        for field in self.schema.get("required", []):
            if field not in transaction:
                errors.append(f"Missing required field: {field}")

        # Проверка типов и дополнительных ограничений
        props = self.schema.get("properties", {})
        for field, rules in props.items():
            if field not in transaction:
                continue  # отсутствие уже обработано выше
            value = transaction[field]
            expected_type = rules.get("type")
            if expected_type == "integer":
                if not isinstance(value, int) or isinstance(value, bool):
                    errors.append(f"Field '{field}' must be integer")
            elif expected_type == "number":
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    errors.append(f"Field '{field}' must be number")
            elif expected_type == "string":
                if not isinstance(value, str):
                    errors.append(f"Field '{field}' must be string")
                # Формат даты
                if rules.get("format") == "date":
                    try:
                        datetime.strptime(value, "%Y-%m-%d")
                    except (ValueError, TypeError):
                        errors.append(f"Field '{field}' has invalid date format (expected YYYY-MM-DD)")
            # Проверка минимума для чисел
            if "minimum" in rules and isinstance(value, (int, float)):
                if value < rules["minimum"]:
                    errors.append(f"Field '{field}' value {value} is less than minimum {rules['minimum']}")

        return len(errors) == 0, errors


# Генерация тестовых транзакций с известными дефектами

def generate_test_transactions(N=1500, invalid_ratio=0.08):
    """
    Генерирует список транзакций, часть из которых гарантированно некорректные.
    Возвращает список кортежей: (транзакция, true_label, expected_error_keywords)
    true_label: True - валидная, False - невалидная
    """
    transactions = []
    num_invalid = int(N * invalid_ratio)
    num_valid = N - num_invalid

    # Корректные транзакции
    for i in range(num_valid):
        trans = {
            "id": random.randint(1000, 9999),
            "amount": round(random.uniform(0.01, 10000.0), 2),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        transactions.append((trans, True, []))

    # ... (остальная часть генерации без изменений, но num_total → N)

    # Некорректные транзакции – разные типы ошибок
    error_types = [
        ("missing_id", {"amount": 50.0, "date": "2025-12-25"}, "Missing required field: id"),
        ("bad_type_amount", {"id": 101, "amount": "abc", "date": "2025-12-25"}, "Field 'amount' must be number"),
        ("bad_date_format", {"id": 102, "amount": 100.0, "date": "25-12-2025"}, "invalid date format"),
        ("missing_date", {"id": 103, "amount": 200.0}, "Missing required field: date"),
        ("negative_amount", {"id": 104, "amount": -50.0, "date": "2025-12-25"}, "less than minimum"),
        ("integer_as_bool", {"id": True, "amount": 50.0, "date": "2025-12-25"}, "Field 'id' must be integer"),
    ]
    for i in range(num_invalid):
        err = random.choice(error_types)
        trans = err[1].copy()
        transactions.append((trans, False, err[2]))

    random.shuffle(transactions)
    return transactions


# Основная логика обработки

def main():
    print("=== Контейнер валидации транзакций запущен ===")
    print(f"Режим: {OPERATION_MODE}")

    validator = TransactionValidator(VALIDATION_SCHEMA)
    transactions = generate_test_transactions(N=1500, invalid_ratio=0.08)

    valid_passed = 0
    valid_blocked = 0
    invalid_detected = 0
    invalid_passed = 0
    processing_times = []
    blocked_log = []  # журнал заблокированных

    start_time = time.time()
    for trans, true_label, _ in transactions:
        t_start = time.perf_counter()
        is_valid, errors = validator.validate(trans)
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        processing_times.append(elapsed_ms)

        if true_label and is_valid:
            valid_passed += 1
        elif true_label and not is_valid:
            valid_blocked += 1
            blocked_log.append((trans, "FALSE_POSITIVE", errors))
        elif not true_label and not is_valid:
            invalid_detected += 1
            blocked_log.append((trans, "TRUE_POSITIVE", errors))
        elif not true_label and is_valid:
            invalid_passed += 1
            # в режиме блокировки такая транзакция бы прошла, что плохо
            blocked_log.append((trans, "MISSED_DEFECT", ["Defect not detected"]))

        # В режиме аудита блокировка не выполняется, но журнал уже записан
    total_time = time.time() - start_time

    avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
    detection_rate = (invalid_detected / (invalid_detected + invalid_passed)) * 100 if (invalid_detected + invalid_passed) > 0 else 0
    false_positive_rate = (valid_blocked / (valid_passed + valid_blocked)) * 100 if (valid_passed + valid_blocked) > 0 else 0

    print(f"\nВсего транзакций: {len(transactions)}")
    print(f"Валидные (по факту): {valid_passed + valid_blocked}")
    print(f"  - пропущено: {valid_passed}")
    print(f"  - ложно заблокированы: {valid_blocked}")
    print(f"Невалидные (по факту): {invalid_detected + invalid_passed}")
    print(f"  - обнаружено и заблокировано: {invalid_detected}")
    print(f"  - пропущено ошибочно: {invalid_passed}")
    print(f"Среднее время обработки: {avg_time:.3f} мс")
    print(f"Процент обнаружения дефектов (recall): {detection_rate:.2f}%")
    print(f"Доля ложных срабатываний: {false_positive_rate:.2f}%")

    # Сохранение сводной таблицы
    df_summary = pd.DataFrame({
        "Показатель": [
            "Всего транзакций",
            "Валидные (факт)",
            "Пропущено корректных",
            "Ложно заблокировано",
            "Невалидные (факт)",
            "Обнаружено дефектов",
            "Пропущено дефектов",
            "Среднее время обработки (мс)",
            "Процент обнаружения",
            "Доля ложных срабатываний"
        ],
        "Значение": [
            len(transactions),
            valid_passed + valid_blocked,
            valid_passed,
            valid_blocked,
            invalid_detected + invalid_passed,
            invalid_detected,
            invalid_passed,
            f"{avg_time:.3f}",
            f"{detection_rate:.2f}%",
            f"{false_positive_rate:.2f}%"
        ]
    })
    print("\nСводная таблица:")
    print(df_summary.to_string(index=False))
    df_summary.to_csv("summary_table.csv", index=False, encoding="utf-8-sig")

    # Сохранение журнала заблокированных (и пропущенных дефектов)
    if blocked_log:
        with open("blocked_log.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Transaction", "DetectionCategory", "Errors"])
            for trans, cat, errors in blocked_log:
                writer.writerow([json.dumps(trans), cat, "; ".join(errors)])
        print("Журнал заблокированных транзакций сохранён в blocked_log.csv")

    # Диаграмма результатов
    labels = ["Корректные пропущены", "Ложно заблокированы", "Дефекты обнаружены", "Дефекты пропущены"]
    sizes = [valid_passed, valid_blocked, invalid_detected, invalid_passed]
    explode = (0, 0.1, 0, 0.1)
    plt.figure()
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title("Результаты валидации транзакций")
    plt.savefig("pie_chart.png")
    plt.close()
    print("График сохранён в pie_chart.png")

if __name__ == "__main__":
    main()





# # ЛР_3 Индивидуальная часть задания
# import os
# import random
# import time
# from sympy import symbols
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np

# registry_user= os.environ.get("REGISTRY_USER")
# registry_password= os.environ.get("REGISTRY_PASSWORD")
# sign_key= os.environ.get("SIGN_KEY")
# db_user= os.environ.get("DB_USER")
# dp_pass= os.environ.get("DB_PASS")


# x,y = symbols('x y')

# N=1500
# invalid_rate=0.08
# valid_count=0
# invalid_count=0
# processing_times=[]

# for i in range (N):
#   start=time.perf_counter()*1000
#   is_valid = random.random() >= invalid_rate
#   time.sleep(random.uniform(0.0005, 0.0025))
#   elapsed = time.perf_counter() * 1000 - start
#   processing_times.append(elapsed)
#   if is_valid:
#     valid_count+=1
#   else:
#     invalid_count+=1

# avg_time= sum(processing_times)/N
# detection_rate=(invalid_count/N)*100 if N else 0

# print(f"Всего транзакций: {N}")
# print(f"Количество валидных транзакций: {valid_count}")
# print(f"Количество невалидных транзакций: {invalid_count}")
# print(f"Среднее время обработки транзакции: {avg_time:.2f} мс")
# print(f"Процент обнаружения невалидных транзакций: {detection_rate:.2f}%")

# df_summary= pd.DataFrame({
#   "Показатель": ["Всего транзакций", "Валидные транзакции", "Невалидные транзакции", "Среднее время обработки", "Процент обнаружения невалидных транзакций"], "Значение": [N, valid_count, invalid_count, f"{avg_time:.2f} мс", f"{detection_rate:.2f}%"]
# })
# print("\nСводная таблица:")
# print(df_summary.to_string(index=False))

# df_summary.to_csv("summary_table.csv", index=False, encoding="utf-8-sig")

# labels = ["Валидные","Невалидные"]
# sizes = [valid_count, invalid_count]
# explode=(0.05,0.1)
# plt.figure()
# plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
# plt.title("Распределение транзакций")
# plt.savefig("pie_chart.png")
# plt.close()




# print("График сохранен в файл pie_chart.png")


# # ЗАДАНИЕ ЛР_3 СЕКРЕТНЫЕ КЛЮЧИ 1 часть
# import os

# my_secret_1 = os.environ["MY_SECRET"]
# my_secret_2 = os.environ["MY_SECRET_2"]
# my_secret_3 = os.environ["TAZHIBAEV_1"]
# my_secret_4 = os.environ["TAZHIBAEV_2"]

# print(my_secret_1, my_secret_2, my_secret_3, my_secret_4)

# from sympy import *
# import pandas as pd
# import matplotlib.pyplot as plt

# # 2 часть задания (Проверяет Виктор)
# ##  ИНДИВИДУАЛЬНАЯ ЧАСТЬ ЗАДАНИЯ (3 Вариант)
# k, T, C, L = symbols("k T C L")
# C_ost = 50000
# Am_lst, C_ost_lst = [], []
# for i in range(9):
#     Am = (C - L) / T  # Что это означает?
#     # формула расчета платежа # Правильно
#     val = float(Am.subs({C: 50000, T: 9, L: 0}))
#     C_ost -= val
#     Am_lst.append(round(val, 2))
#     C_ost_lst.append(round(float(C_ost), 2))
# print("Am_lst=", Am_lst)
# print("C_ost_lst=", C_ost_lst)
# # Все правильно 5, изменилось C_ost = 20000 и T = 6

# # 2 способ
# Aj = 0
# C_ost = 50000
# Am_lst_2 = []
# C_ost_lst_2 = []
# for i in range(9):
#     Am = k * 1 / T * (C - Aj)
#     C_ost -= Am.subs({C: 50000, T: 9, k: 2})
#     Am_lst_2.append(round(Am.subs({C: 50000, T: 9, k: 2}), 2))
#     Aj += Am
#     C_ost_lst_2.append(round(C_ost, 2))
# print("Am_lst_2=", Am_lst_2)
# print("C_ost_lst_2=", C_ost_lst_2)
# # Все правильно 5, изменилось C_ost = 20000 и T = 6


# # Табличный вывод
# Y = range(1, 7)  # Что это означает?
# # цикл от 1 о 7  Правильно
# table1 = list(zip(Y, C_ost_lst, Am_lst))
# table2 = list(zip(Y, C_ost_lst_2, Am_lst_2))
# tfame = pd.DataFrame(table1, columns=["Y", "C_ost_lst", "Am_lst"])
# tfame2 = pd.DataFrame(table2, columns=["Y", "C_ost_lst_2", "Am_lst_2"])
# print(tfame)
# print(tfame2)

# # Контейнер визуализации
# plt.plot(tfame["Y"], tfame["C_ost_lst"], label="Am")
# plt.savefig("chart2_1.png")
# plt.figure()
# plt.plot(tfame2["Y"], tfame2["C_ost_lst_2"], label="Am2")
# plt.savefig("chart2_2.png")
# plt.figure()

# vals = Am_lst
# labels = [str(x) for x in range(1, 10)]
# # Все правильно str(x) for x in range(1, 7), 5
# explode = (
#     0.1,
#     0.1,
#     0.1,
#     0.1,
#     0.1,
#     0.1,
#     0.1,
#     0.1,
#     0.1,
# )  # Что это означает? #Список из чисел #Почти правильно
# fig, ax = plt.subplots()
# ax.pie(
#     vals,
#     labels=labels,
#     autopct="%1.1f%%",
#     shadow=True,
#     explode=explode,
#     wedgeprops={"lw": 1, "ls": "--", "edgecolor": "k"},
#     rotatelabels=True,
# )
# ax.axis("equal")
# plt.savefig("chart2_3.png")
# plt.figure()

# vals = Am_lst_2
# labels = [
#     str(x) for x in range(1, 10)
# ]  # Что это означает? #Список из чисел от одного до семи
# # Все правильно 5
# tt1 = 20
# ее2 = 40
# explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1)
# fig, ax = plt.subplots()
# ax.pie(
#     vals,
#     explode=explode,
#     labels=labels,
#     autopct="%1.1f%%",
#     shadow=True,
#     wedgeprops={"lw": 1, "ls": "--", "edgecolor": "k"},
#     rotatelabels=True,
# )
# ax.axis("equal")
# plt.savefig("chart2_4.png")
# plt.figure()

# plt.figure()
# table1 = list(zip(Y, Am_lst))
# table2 = list(zip(Y, Am_lst_2))
# tfame = pd.DataFrame(table1, columns=["Y", "Am_lst"])
# tfame2 = pd.DataFrame(table2, columns=["Y", "Am_lst_2"])
# plt.bar(tfame["Y"], tfame["Am_lst"])
# plt.savefig("chart2_5.png")
# plt.figure()
# plt.bar(tfame["Y"], tfame2["Am_lst_2"])
# plt.savefig("chart2_6.png")
# plt.figure()
