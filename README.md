# 🧠 PBH_Quiz - 퀴즈 응시 시스템

---

## 📦 기술 스택

- **Backend**: Django 5.2, Django REST Framework
- **Auth**: SimpleJWT (access/refresh 토큰)
- **Database**: PostgreSQL
- **Cache**: Redis + drf-extensions
- **Documentation**: Swagger (drf-yasg)
- **Test**: Django `APITestCase`
- **Dependency**: poetry

---

## 🚀 실행 방법

### 1. 의존성 설치
```bash
poetry install
```

### 2. `.env` 설정
```bash
cp .env.example .env
```

### 3. 마이그레이션 및 슈퍼유저 생성
```bash
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

### 4. 서버 실행
```bash
poetry run python manage.py runserver
```

### 5. Swagger API 문서 확인
```
http://localhost:8000/swagger/
```

---

## ✅ 주요 기능 및 경로

### [1] 퀴즈 생성/관리 (관리자 전용)
| 메서드 | URL | 설명 |
|--------|-----|------|
| POST   | `/api/quizzes/admin/quizzes/` | 퀴즈 생성 |
| GET    | `/api/quizzes/admin/quizzes/` | 퀴즈 목록 |
| GET    | `/api/quizzes/admin/quizzes/<id>/` | 퀴즈 상세 |
| PUT    | `/api/quizzes/admin/quizzes/<id>/` | 퀴즈 수정 |
| DELETE | `/api/quizzes/admin/quizzes/<id>/` | 퀴즈 삭제 |

### [2] 퀴즈 응시/제출
| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/api/sessions/<quiz_id>/start/` | 세션 시작 (랜덤 출제) |
| PATCH | `/api/sessions/sessions/<session_id>/answers/` | 답안 저장 |
| POST | `/api/sessions/sessions/<session_id>/submit/` | 제출 + 채점 |
| GET  | `/api/sessions/sessions/<session_id>/` | 세션 상세 (문제, 답안 포함) |
| GET  | `/api/sessions/sessions/<session_id>/questions/` | 문제 페이징 조회 |

### [3] 퀴즈 목록 조회
| 메서드 | URL | 설명 |
|--------|-----|------|
| GET | `/api/sessions/my_list/` | 사용자별 응시 여부 포함 퀴즈 목록 |
| GET | `/api/sessions/admin/<quiz_id>/sessions/` | 퀴즈별 전체 응시 세션 목록 (관리자) |

---

## 🔐 인증 방식 (JWT)

1. 회원가입 → `/api/users/register/`
2. 로그인 → `/api/users/login/` → access/refresh 토큰 발급
3. Authorization 헤더 사용:
   ```http
   Authorization: Bearer <access_token>
   ```

---

## 📚 테스트 실행
```bash
poetry run python manage.py test
```
테스트 항목:
- 관리자 퀴즈 CRUD
- 사용자 퀴즈 응시/답안 저장/제출
- 권한 체크 (403), 유효성 검사, 자동 채점

---

## 🧠 캐싱 적용

> 트래픽이 높은 조회 API에 `CacheResponseMixin` 사용:

- `/api/sessions/my_list/`
- `/api/sessions/admin/<quiz_id>/sessions/`

설정:
```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
```

Redis 설치 필요:
```bash
poetry add redis
```

---

## 🗂️ 폴더 구조 (중요 파일만)
```
PBH_Quiz/
├── quizzes/            # 퀴즈 생성/관리
├── quiz_sessions/      # 퀴즈 응시/답안/채점
├── users/              # 회원가입, 로그인
├── config/             # 프로젝트 설정
├── pyproject.toml
├── README.md
└── .env.example
```

---

## 🙋‍♂️ 제출자 정보

| 항목 | 내용                                         |
|------|--------------------------------------------|
| 이름 | 박병훈                                        |
| GitHub | https://github.com/byounghoonpark/PBH_Quiz |

---

감사합니다
