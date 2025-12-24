from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Определяем базовую директорию проекта (корень проекта)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

# Настраиваем шаблоны (templates находятся в корне проекта)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница - Landing"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/verify", response_class=HTMLResponse)
async def verify_page(request: Request):
    """Страница верификации email"""
    return templates.TemplateResponse("verify.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Главная страница приложения после входа"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    """Страница анализа почвы"""
    return templates.TemplateResponse("analyze.html", {"request": request})


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Страница истории анализов"""
    return templates.TemplateResponse("history.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Страница профиля пользователя"""
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """Страница О системе"""
    return templates.TemplateResponse("about.html", {"request": request})
