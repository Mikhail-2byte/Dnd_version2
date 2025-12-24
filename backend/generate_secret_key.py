#!/usr/bin/env python3
"""
Скрипт для генерации безопасного SECRET_KEY для JWT токенов
"""
import secrets

if __name__ == "__main__":
    secret_key = secrets.token_urlsafe(32)
    print(secret_key)

