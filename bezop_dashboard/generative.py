import os
import random
import time
import pandas as pd
import matplotlib.pyplot as plt

def run_validation(N=1500, invalid_rate=0.08):
    """Запускает симуляцию валидации транзакций и возвращает статистику."""
    valid_count = 0
    invalid_count = 0
    processing_times = []

    for i in range(N):
        start = time.perf_counter() * 1000
        is_valid = random.random() >= invalid_rate
        time.sleep(random.uniform(0.0005, 0.0025))
        elapsed = time.perf_counter() * 1000 - start
        processing_times.append(elapsed)
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1

    avg_time = sum(processing_times) / N
    detection_rate = (invalid_count / N) * 100 if N else 0


    # Вернуть все нужные данные в виде словаря
    return {
        'total': N,
        'valid': valid_count,
        'invalid': invalid_count,
        'avg_time_ms': avg_time,
        'detection_rate': detection_rate,
        'processing_times': processing_times,
    }