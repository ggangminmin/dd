#!/bin/bash
# Render 배포용 시작 스크립트

# 데이터베이스 초기화 (필요시)
python database.py

# Gunicorn으로 Flask 앱 실행
gunicorn --bind 0.0.0.0:$PORT app:app
