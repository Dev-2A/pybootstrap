# 🐍 PyBootstrap

한 줄 명령어로 Python 프로젝트 스캐폴딩을 자동화는 CLI 도구입니다.

토이 프로젝트를 만들며 매번 반복했던 초기 세팅을 자동화하는 메타 도구.  
`git-commit-gen` → `kr-code-reviewer` → `pybootstrap`으로 이어지는 **Python CLI 도구 시리즈 3부작** 완성.

## 주요 기능

- ⚡ `bootstrap create my-project --template fastapi` 한 줄로 프로젝트 생성
- 📁 템플릿별 디렉토리 구조, `.gitignore`, `requirements.txt`, `README.md`, `Dockerfile` 자동 생성
- 🎨 사전 정의 템플릿 3종: `fastapi`, `cli`, `fullstack` (React + FastAPI)
- 🔧 커스텀 템플릿 생성 및 재사용 지원
- 🎄 Rich 기반 트리 구조 미리보기
- 🐳 Docker 지원 (Dockerfile, docker-compose.yml 자동 생성)
- 🔀 `git init` 자동 실행

## 기술 스택

- **Language:** Python 3.11+
- **CLI:** Click
- **Template Engine:** Jinja2
- **Console UI:** Rich

## 설치

```bash
git clone https://github.com/Dev-2A/pybootstrap.git
cd pybootstrap
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## 사용법

### 프로젝트 생성

```bash
# FastAPI 프로젝트
bootstrap create my-api --template fastapi

# Click CLI 도구
bootstrap create my-tool --template cli -d "나만의 CLI 도구" -a "Dev-2A"

# React + FastAPI 풀스택
bootstrap create my-app --template fullstack

# Docker 없이 생성
bootstrap create my-api --template fastapi --no-docker

# 특정 디렉토리에 생성
bootstrap create my-api --template fastapi -o ~/projects
```

### 템플릿 목록 조회

```bash
bootstrap list
bootstrap list --builtin
bootstrap list --custom
```

### 템플릿 상세 정보

```bash
bootstrap info fastapi
bootstrap info cli
bootstrap info fullstack
```

### 커스텀 템플릿

```bash
# 빈 커스텀 템플릿 생성
bootstrap init-template flask -d "Flask 웹 프로젝트"

# 기존 프로젝트를 템플릿으로 변환
bootstrap import ./my-existing-project my-template

# 커스텀 템플릿으로 프로젝트 생성
bootstrap create new-project -t flask

# 커스텀 템플릿 삭제
bootstrap remove-template flask --yes
```

## 내장 템플릿

### ⚡ FastAPI

- FastAPI + Pydantic + uvicorn
- `src/` 레이아웃, 라우터 패턴, 헬스체크 엔드포인트
- CORS 미들웨어, pydantic-settings 설정 관리

### 🖥️ CLI (Click)

- Click 기반 커맨드라인 도구
- `src/` 레이아웃, CLI/Core 분리 패턴
- `pyproject.toml` entry point 자동 설정

### 🌐 Fullstack (React + FastAPI)

- `backend/` (FastAPI) + `frontend/` (React + Vite) 분리
- Vite 프록시 설정으로 개발 시 API 연동
- Docker Compose로 한 번에 실행

## 프로젝트 구조

pybootstrap/  
├── src/  
│   └── pybootstrap/  
│       ├── templates/          # Jinja2 템플릿 파일  
│       │   ├── base/           # 공통 (gitignore, README, Dockerfile 등)  
│       │   ├── fastapi/        # FastAPI 전용  
│       │   ├── cli/            # CLI 전용  
│       │   └── fullstack/      # React + FastAPI 전용  
│       ├── init.py  
│       ├── cli.py              # Click CLI 인터페이스  
│       ├── config.py           # 설정 관리  
│       ├── custom.py           # 커스텀 템플릿 관리  
│       ├── display.py          # Rich 콘솔 출력  
│       ├── models.py           # 데이터 모델  
│       ├── registry.py         # 템플릿 레지스트리  
│       └── scaffolder.py       # 스캐폴딩 엔진  
├── tests/                      # pytest 테스트  
├── pyproject.toml  
├── requirements.txt  
└── requirements-dev.txt

## 개발

```bash
# 개발 환경 설정
git clone https://github.com/Dev-2A/pybootstrap.git
cd pybootstrap
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install -r requirements-dev.txt

# 테스트 실행
pytest tests/ -v
```

## 라이선스

MIT License
