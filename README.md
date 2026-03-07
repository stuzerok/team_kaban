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

## Запуск (пошагово)

```bash

# 1. Установи зависимости
pip install -r requirements.txt

# 2. Распакуй черный ящик (НЕ открывать riscv_reg_block.py!)
python3 loader.py

# 3. Запусти тесты + coverage
python -m pytest tests/ --cov=riscv_reg_block --cov-report=html:coverage_report/

# 4. Проверка кодстайла YADRO
pylint -m *.py tests/ dashboard.py  # Цель: ≥8.0/10

# 5. Dashboard с live метриками
python -m streamlit run dashboard.py

