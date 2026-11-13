# Гайд по лабе 5: что делать по шагам и что значит каждая команда

## Общая идея
Мы делаем маленькое Flask-приложение и вокруг него «конвейер» (CI/CD) на GitHub Actions.
При каждом `push` или pull request GitHub сам запускает тесты и 5 сканеров безопасности и сохраняет их отчёты.
Зачем: чтобы уязвимости находились автоматически, до выхода в продакшен.

Код и файлы я уже написал. От тебя: создать репозиторий, залить код, дождаться запуска, заполнить отчёт, сделать скриншоты.

## Шаг 1. Пустой репозиторий на GitHub
New repository, имя `vulnfinbot-secure-pipeline`. Не ставь галочки README, .gitignore, license.

## Шаг 2. Залить код

```bash
cd vulnfinbot-secure-pipeline
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<твой-логин>/vulnfinbot-secure-pipeline.git
git push -u origin main
```

- `git init`: превращает папку в git-репозиторий.
- `git add .`: добавляет все файлы в следующий коммит (точка = всё в папке; лишнее отсекает `.gitignore`).
- `git commit -m "..."`: сохраняет снимок файлов; `-m` задаёт сообщение.
- `git branch -M main`: переименовывает текущую ветку в `main` (`-M` = переименовать принудительно).
- `git remote add origin <url>`: запоминает адрес репозитория на GitHub под именем `origin`.
- `git push -u origin main`: отправляет ветку `main` на GitHub; `-u` запоминает связку, дальше хватит `git push`.

## Шаг 3. Запустить локально

```bash
python -m venv venv
venv\Scripts\activate        # Windows (у тебя Windows)
pip install -r requirements.txt
python run.py
```

- `python -m venv venv`: `-m venv` запускает модуль создания виртуального окружения, второе `venv` это имя папки. Окружение изолирует пакеты проекта.
- `venv\Scripts\activate`: включает окружение (в Mac/Linux: `source venv/bin/activate`).
- `pip install -r requirements.txt`: ставит пакеты из списка; `-r` = читать из файла.
- `python run.py`: запускает приложение на `http://127.0.0.1:5000`.

Проверка (в другом терминале; в PowerShell лучше `curl.exe`):

```bash
curl http://127.0.0.1:5000/health
curl -X POST http://127.0.0.1:5000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"How can I manage my monthly budget?\"}"
```

- `-X POST`: метод запроса. `-H "..."`: заголовок (говорим, что шлём JSON). `-d "..."`: тело запроса.

## Шаг 4. Тесты

```bash
pytest -v
```

`pytest` находит и запускает тесты в папке `tests/`; `-v` (verbose) печатает каждый тест отдельной строкой.
Должно быть `29 passed`. Заодно создаётся `reports/ai-security-report.md`.

## Шаг 5. Что делает workflow (`.github/workflows/security-pipeline.yml`)
Он запускается сам после `git push`. Смотри вкладку Actions в репозитории.

Ключевые части файла:
- `on: push / pull_request`: когда запускаться.
- `runs-on: ubuntu-latest`: на каком виртуальном компьютере GitHub это выполнять.
- `uses: actions/checkout@v4`: готовое действие, скачивает код репозитория.
- `uses: actions/setup-python@v5`: ставит Python 3.12.
- `run:`: обычная команда в терминале.
- `continue-on-error: true`: если шаг упал, конвейер продолжается (нужно, чтобы отчёты не терялись).
- `if: always()`: шаг выполнится даже после ошибок раньше.
- `actions/upload-artifact@v4`: сохраняет папку `reports/` как скачиваемый архив.

Команды сканеров:

```bash
bandit -r app/ -f json -o reports/bandit-report.json
```
`-r app/` проверять папку рекурсивно, `-f json` формат вывода, `-o` куда записать.

```bash
semgrep scan --config security/semgrep/rules.yml --metrics off --json --output reports/semgrep-report.json app/
```
`--config` файл с нашими правилами, `--metrics off` не отправлять статистику, `--json --output` отчёт в JSON, последним идёт что сканировать.

```bash
pip-audit -r requirements.txt -f json -o reports/dependency-report.json
```
Сверяет пакеты из файла с базой известных уязвимостей. `-r` файл зависимостей, `-f json` формат, `-o` файл отчёта.

```bash
docker build -t vulnfinbot:latest .
```
Собирает образ по `Dockerfile`; `-t` задаёт имя:тег; точка = брать файлы из текущей папки.

Trivy (в workflow через готовое действие `aquasecurity/trivy-action`) сканирует собранный образ на уязвимости ОС и пакетов; эквивалент в терминале: `trivy image --format json --output reports/trivy-report.json vulnfinbot:latest`.

```bash
docker run -d --name vulnfinbot -p 5000:5000 vulnfinbot:latest
```
`-d` запуск в фоне, `--name` имя контейнера, `-p 5000:5000` пробросить порт 5000 контейнера на порт 5000 компьютера.

```bash
docker run --rm --network host -v "$(pwd)/reports:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://localhost:5000 -J zap-report.json
```
Запускает OWASP ZAP как «внешнего атакующего-наблюдателя»: `--rm` удалить контейнер после работы, `--network host` ZAP видит `localhost` runner'а, `-v папка:папка` подключить `reports/` внутрь контейнера (так отчёт попадает к нам), `-t` адрес цели, `-J` имя JSON-отчёта.

## Шаг 6. Скачать отчёты и заполнить итоги
Actions, выбираешь запуск, внизу Artifacts, скачиваешь `vulnfinbot-security-reports`.
Таблица находок есть на странице запуска (Summary). Локально:

```bash
python scripts/summarize_reports.py reports
```
Скрипт читает JSON-отчёты и считает находки по уровням опасности.

## Шаг 7. Контролируемая уязвимая ветка (шаг 11 лабы)

```bash
bash scripts/make_vuln_branch.sh
git push -u origin test/vulnerable-demo
```
Скрипт создаёт отдельную ветку и кладёт туда специально плохой код (`eval`, пароль в коде, MD5, `shell=True`). На GitHub открой pull request в `main` (не мержи!), сканеры должны это найти. Сделай скриншот находок, потом исправь (удали файл), запушь снова и сравни результаты «до и после». На Windows запускай скрипт через Git Bash.

## Шаг 8. Что сдать
1. Ссылка на репозиторий. 2. Код. 3. Workflow. 4. SAST-конфиги и отчёты. 5. Отчёты по зависимостям и контейнеру. 6. Отчёт ZAP. 7. AI-тесты и отчёт. 8. README. 9. Технический отчёт (шаблон: `reports/technical-report.md`, поля автора пустые, впиши сам). 10. Скриншоты успешного запуска пайплайна.

## Честные оговорки
- Ассистент в проекте мок, поэтому AI-тесты проверяют защиту на уровне приложения, а не поведение настоящей LLM. Это указано в README и AI-отчёте. Если хочешь максимум баллов за prompt injection, подключи реальную модель и прогони те же сценарии.
- Версии действий (например `trivy-action@0.28.0`) могут устареть; если шаг не находит версию, замени на актуальную с страницы действия на GitHub.
- Я не мог запустить Bandit, Semgrep, pip-audit, Docker и ZAP у себя (нет сети и демона Docker), поэтому они проверятся только при первом запуске в GitHub Actions. Тесты pytest я прогнал: 29 прошли.
