## Проверка работоспособности и обработка ошибок

### Обработанные ошибки:

1. **Ошибки ввода данных:**
   - Если пользователь оставляет поля пустыми, отображается сообщение:
     "Both start and end points are required."
   - Если введенный город не поддерживается, отображается сообщение:
     "City not found or unsupported."

2. **Ошибки API:**
   - При недоступности API отображается сообщение:
     "API connection failed: <текст ошибки>"
   - Если API возвращает ошибочный ответ, отображается сообщение:
     "API error: <код ошибки> - <текст ошибки>."

3. **Общие ошибки:**
   - При непредвиденных ошибках (например, сбой на сервере) отображается сообщение:
     "Unexpected error: <текст ошибки>."

### Тестовые сценарии:
1. Корректные города: `moscow` и `sochi`.
2. Неизвестный город: `unknown`.
3. Пустые поля.
4. Отключение интернета.