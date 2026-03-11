# 📤 Инструкция по загрузке на GitHub

## Вариант 1: Через GitHub CLI (рекомендуется)

### Установка gh

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install gh

# Проверка
gh --version
```

### Авторизация

```bash
gh auth login
```

Следуйте инструкциям:
1. Выберите GitHub.com
2. Выберите HTTPS
3. Нажмите "Login with a browser"
4. Авторизуйтесь в браузере

### Создание репозитория

```bash
cd /home/sa/projects/rkllm-tools-fork

# Создание публичного репозитория
gh repo create rkllm-tools-fork --public --source=. --remote=origin --push

# Или приватного
gh repo create rkllm-tools-fork --private --source=. --remote=origin --push
```

---

## Вариант 2: Вручную через браузер

### Шаг 1: Создание репозитория на GitHub

1. Откройте https://github.com/new
2. Введите имя репозитория: `rkllm-tools-fork`
3. Описание: "Инструменты для конвертации LLM моделей в формат RKLLM"
4. Выберите видимость: Public или Private
5. **НЕ** ставьте галочки "Initialize with README"
6. Нажмите "Create repository"

### Шаг 2: Привязка удаленного репозитория

```bash
cd /home/sa/projects/rkllm-tools-fork

# Замените YOUR_USERNAME на ваш логин GitHub
git remote add origin https://github.com/YOUR_USERNAME/rkllm-tools-fork.git

# Проверка
git remote -v
```

### Шаг 3: Отправка кода

```bash
# Отправка основной ветки
git push -u origin main

# Отправка всех веток (если есть)
git push -u origin --all

# Отправка тегов (если есть)
git push --tags
```

---

## Вариант 3: Через SSH (если настроен SSH ключ)

### Генерация SSH ключа (если нет)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
```

Добавьте ключ в настройках GitHub: https://github.com/settings/keys

### Создание и отправка

```bash
cd /home/sa/projects/rkllm-tools-fork

# Создание репозитория через CLI
gh repo create rkllm-tools-fork --private --source=. --remote=origin --push

# Или вручную добавить remote и push
git remote add origin git@github.com:YOUR_USERNAME/rkllm-tools-fork.git
git push -u origin main
```

---

## ✅ Проверка после загрузки

```bash
# Проверка статуса
git status

# Проверка удаленного репозитория
git remote -v

# Проверка последней версии
git log --oneline -5
```

---

## 🔧 Дополнительные команды

### Обновление после изменений

```bash
cd /home/sa/projects/rkllm-tools-fork

# Добавление изменений
git add .

# Коммит
git commit -m "Описание изменений"

# Отправка
git push origin main
```

### Клонирование на другом устройстве

```bash
git clone https://github.com/YOUR_USERNAME/rkllm-tools-fork.git
cd rkllm-tools-fork
```

---

## 📊 Статистика репозитория

```bash
# Размер репозитория
du -sh /home/sa/projects/rkllm-tools-fork

# Количество файлов
find . -type f | wc -l

# Статистика по файлам
git ls-files | xargs ls -lh | awk '{ total += $5 } END { print "Total: " total/1024/1024 " MB" }'
```

---

## ⚠️ Важно

Перед загрузкой убедитесь:
- [x] Нет чувствительных данных в коде
- [x] `.gitignore` настроен правильно
- [x] Рабочие файлы (модели) исключены из репозитория
- [x] Тесты проходят успешно

---

*Инструкция актуальна для GitHub 2026*
