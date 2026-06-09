# Лаунчер «Ночной смены»: запускает Claude Code headless на разработку игры.
# Вызывается Планировщиком заданий Windows ежедневно в 00:05 (лимит 5 ч → до 05:05 KRAT).
$ErrorActionPreference = 'Continue'

$game = 'C:\Users\user\Desktop\Разработка на питоне\game'
Set-Location $game

# Окружение: UTF-8 (кириллица) + прокси для Claude Code из РФ (иначе 403).
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:HTTPS_PROXY = 'http://127.0.0.1:10808'
$env:HTTP_PROXY = 'http://127.0.0.1:10808'

$today = Get-Date -Format 'yyyy-MM-dd'
$logdir = Join-Path $game '.night\logs'
if (-not (Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
$log = Join-Path $logdir "$today-runner.log"

"=== Ночная смена СТАРТ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $log -Append -Encoding utf8

$prompt = 'Сегодня ночная смена. Прочитай файл .night/night_prompt.md в текущей папке и выполни его СТРОГО по шагам (0-6). Работай только в git-ветке night/auto. Коммить только при полностью зелёных тестах. В main НЕ коммить и НЕ пушить. Перед этапом и после этапа созывай команду субагентов на обсуждение, как описано в промпте.'

$claude = 'C:\Users\user\AppData\Roaming\npm\claude.cmd'
& $claude -p $prompt --dangerously-skip-permissions *>> $log

"=== Ночная смена КОНЕЦ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $log -Append -Encoding utf8
