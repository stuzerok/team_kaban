# Team Kaban | RISC-V Register Verifier
[Схема](env.jpg)
## Метрики YADRO (цель: 950/1000 → стажировка)

| Метрика | Цель | Текущий | Команда |
|---------|------|---------|---------|
| pytest coverage | ≥94% | 100% | pytest --cov |
| pylint | ≥8.0/10 | 8.47/10 | pylint *.py tests/ |
| Найденные баги | ≥3 | 6/3 | Авто в тестах |
| Dashboard | Live demo | Да | streamlit run dashboard.py |

Pylint источник: https://github.com/1irs/pylint_practice
## Баги
Баг №1: Значение LCR(3) по сбросу 0x00 вместо ожидаемого 0x01 
Для вопроизведения запустить bug0_test

Баг №2: Регистр IER(4) доступен для записи [31 : 4] хотя согласно спецификации доступны только [3:0]
Для вопроизведения запустить bug0_1_test

Баг №3: Регистр IIR(5) доступен для записи но согласно спецификации он read only
Для вопроизведения запустить bug0_2_test

Баг №4: Регистр LSR(7) доступен для записи но согласно спецификации он read only
Для вопроизведения запустить bug0_2_test

Баг №5: Регистр MSR(9) доступен для записи но согласно спецификации он read only
Для вопроизведения запустить bug0_2_test

Баг №6: Значение IIR(5) по сбросу 0x00 вместо ожидаемого 0x8C
Для вопроизведения запустить bug0_test

Баг №7: Значение LSR(7) по сбросу 0x00 вместо ожидаемого 0x60
Для вопроизведения запустить bug0_test

Баг №8: Запись в регистр LCR (3) блокирует чтение IER (4)
Для вопроизведения запустить bug1_test

Баг №9: Невозможность отправки данныз с значением data >= 0x00010000. Данные записываются не корректно
Для вопроизведения запустить bug2_test

Баг №10: Запись в регистр DLBR_DLL (2) любого значения с data[7 : 0] = 0x42 приводит к потере данных data [31 : 6]
Для вопроизведения запустить bug3_test

Баг №11: Биты регистра RBR_THR (0) [31 : 6] должны быть зарезервированы. Но они доступны для записи
Для вопроизведения запустить bug4_test

## Запуск (пошагово)

```bash

# 1. Установи зависимости
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install streamlit pytest-cov pylint pytest
python generate_results.py
# 2. Распакуй черный ящик (НЕ открывать riscv_reg_block.py!)
python -m pytest tests/ --cov=riscv_reg_block --cov-report=html:coverage_report/
python3 loader.py

# 3. Запусти тесты + coverage
python -m pytest tests/ --cov=riscv_reg_block --cov-report=html:coverage_report/

# 4. Проверка кодстайла YADRO
pylint -m *.py tests/ dashboard.py  # Цель: ≥8.0/10

# 5. Dashboard с live метриками
python -m streamlit run dashboard.py

