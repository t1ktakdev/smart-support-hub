# GitHub и публикация: фактический статус

Проверено: 03.11.2026 (Бишкек).

- GitHub: https://github.com/t1ktakdev/smart-support-hub
- Владелец учётной записи подтверждён: `t1ktakdev`.
- Репозиторий **создан**, видимость публичная. Исходные файлы **не отправлены**.
- Git-ветка `main` и история из пяти локальных коммитов находятся в `D:\smart-support-hub`.
- Теги `v1.0.0` и `v1.1.0` созданы локально, в удалённый репозиторий не отправлены.
- GitHub Issues: [№1](https://github.com/t1ktakdev/smart-support-hub/issues/1) и [№2](https://github.com/t1ktakdev/smart-support-hub/issues/2), закрыты после исправлений, проверенных локально.
- GitHub Pages **не опубликован**, публичная ссылка на веб-приложение отсутствует. Нельзя использовать предполагаемый URL как действующий сайт.

## Причина

Подключённый ForgeBridge отклонил операцию `git.push` для `D:\smart-support-hub`:

```
permission_denied
scope-deny: Capability git.push is outside its configured scope
next_action: report_denial_do_not_bypass
```

Обходить ограничение другим инструментом нельзя. Для завершения онлайн-этапа нужно официально расширить область разрешений `git.push` для этой папки через настройки ForgeBridge, затем повторить штатную публикацию и проверить открытие GitHub Pages.

## Проверка локальной версии

- URL: http://127.0.0.1:8765/
- Chrome: 26 PASS / 0 FAIL.
- Node.js: 11 PASS / 0 FAIL.
- ZIP: `dist/Smart_Support_Hub_Abitalipov_Final.zip` (собран на ноутбуке).
