from fastapi import FastAPI, Request, Form, HTTPException, Response, redirect
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import database
import json
import secrets
import logging
import redis
import os
import hashlib
from dotenv import load_dotenv

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

# ===== Переводы =====
TRANSLATIONS = {
    'uz': {
        'home': 'Bosh sahifa',
        'movies': 'Filmlar',
        'tv': 'TV',
        'search': 'Qidiruv',
        'profile': 'Profil',
        'login': 'Kirish',
        'register': 'Ro\'yxatdan o\'tish',
        'logout': 'Chiqish',
        'navigation': 'Navigatsiya',
        'genres': 'Janrlar',
        'new_releases': 'Yangiliklar',
        'tv_shows': 'TV-shoular',
        'about': 'Biz haqimizda',
        'contact': 'Aloqa',
        'help': 'Yordam',
        'terms': 'Foydalanish shartlari',
        'privacy': 'Maxfiylik siyosati',
        'footer_description': 'Filmlar, TV-shoular va eksklyuziv originalarning asosiy manbai. Istalgan joyda, istalgan vaqtda tomosha qiling.',
        'all_rights_reserved': 'Barcha huquqlar himoyalangan',
        'trending': 'Trenddagi',
        'top10': 'Top 10',
        'continue_watching': 'Ko\'rishni davom ettirish',
        'popular': 'Ommabop',
        'recommended': 'Tavsiya etilgan',
        'watch_now': 'Hozir tomosha qiling',
        'more_info': 'Batafsil',
        'play': 'Ishga tushirish',
        'add_to_list': 'Ro\'yxatga qo\'shish',
        'rate': 'Baholash',
        'share': 'Ulashish',
        'season': 'Mavsum',
        'episode': 'Epizod',
        'year': 'Yil',
        'duration': 'Davomiyligi',
        'quality': 'Sifat',
        'director': 'Rejissyor',
        'cast': 'Aktyorlar',
        'storyline': 'Syujet',
        'reviews': 'Sharhlar',
        'similar': 'O\'xshash',
        'loading': 'Yuklanmoqda...',
        'no_results': 'Natijalar topilmadi',
        'try_again': 'Qayta urinib ko\'ring',
        'back': 'Orqaga',
        'next': 'Keyingi',
        'previous': 'Oldingi',
        'page': 'Sahifa',
        'of': 'dan',
        'showing': 'Ko\'rsatilmoqda',
        'results': 'natijalar',
        'filter': 'Filter',
        'sort_by': 'Saralash',
        'date_added': 'Qo\'shilgan sana',
        'rating': 'Reyting',
        'name': 'Nomi',
        'release_date': 'Chiqarilgan sana',
        'language': 'Til',
        'country': 'Mamlakat',
        'subscription': 'Obuna',
        'plans': 'Rejalar',
        'pricing': 'Narxlar',
        'buy': 'Sotib olish',
        'cancel': 'Bekor qilish',
        'confirm': 'Tasdiqlash',
        'save': 'Saqlash',
        'delete': 'O\'chirish',
        'edit': 'Tahrirlash',
        'settings': 'Sozlamalar',
        'account': 'Hisob',
        'password': 'Parol',
        'email': 'Email',
        'username': 'Foydalanuvchi nomi',
        'phone': 'Telefon',
        'address': 'Manzil',
        'city': 'Shahar',
        'zip': 'Indeks',
        'state': 'Viloyat',
        'birthday': 'Tug\'ilgan kun',
        'gender': 'Jins',
        'male': 'Erkak',
        'female': 'Ayol',
        'other': 'Boshqa',
        'select': 'Tanlang',
        'required': 'Majburiy',
        'optional': 'Ixtiyoriy',
        'error': 'Xato',
        'success': 'Muvaffaqiyatli',
        'warning': 'Ogohlantirish',
        'info': 'Ma\'lumot',
        'close': 'Yopish',
        'ok': 'OK',
        'yes': 'Ha',
        'no': 'Yo\'q',
        'all': 'Barchasi',
        'action': 'Jangari',
        'drama': 'Drama',
        'horror': 'Qo\'rqinchli',
        'scifi': 'Fantastika',
        'comedy': 'Komediya',
        'thriller': 'Triller',
        'romance': 'Melodrama',
        'fantasy': 'Fantaziya',
        'mystery': 'Detektiv',
        'animation': 'Multfilm',
        'documentary': 'Hujjatli',
        'crime': 'Jinoyat',
        # Top sections
        'top10_movies': 'Ko\'rish uchun top 10 film',
        'editor_pick': 'Tahririyat tomonidan tanlangan',
        'popular_movies': 'Ommabop filmlar',
        'coming_soon': 'Tez orada kinoteatrlarda',
        'soon_on_streamit': 'Tez orada Streamit\'da',
        'recommended_for_you': 'Sizga tavsiya etamiz',
        'based_on_history': 'Tomosha tarixingiz asosida',
        'movies_by_genre': 'Janrlar bo\'yicha filmlar',
        # Profil
        'profile_title': 'Profil',
        'profile_settings': 'Sozlamalar / Profil',
        'balance_label': 'Balans:',
        'nav_profile': 'Profil',
        'nav_balance': 'Balans',
        'nav_history': 'Tarix',
        'nav_subscriptions': 'Obunalar',
        'nav_settings': 'Sozlamalar',
        'logout_btn': 'Chiqish',
        'balance_title': 'Balans',
        'top_up': "To'ldirish",
        'quick_amounts': 'Tezkor summalar',
        'payment_history': "To'lovlar tarixi",
        'date': 'Sana',
        'amount': 'Summa',
        'status': 'Holat',
        'history_empty': 'Tarix bo\'sh',
        'payment_method': 'To\'lov usuli',
        'logout_all_devices': 'Barcha qurilmalardan chiqish',
        'confirm_logout_all': 'Barcha qurilmalardan chiqilsinmi? Joriy qurilma qoladi.',
        'profile_card_title': 'Shaxsiy ma\'lumotlar',
        'edit': 'Tahrirlash',
        'avatar_alt': 'Avatar',
        'name_label': 'Ism:',
        'email_label': 'Email:',
        'phone_label': 'Telefon:',
        'member_since': "Ro'yxatdan o'tgan sana:",
        'subscription_status': 'Obuna holati:',
        'active': 'Faol',
        'inactive': 'Faol emas',
        'create_new_profile': 'Yangi profil yaratish',
        'logout_account': 'Akkauntidan chiqish',
    },
    'ru': {
        'home': 'Главная',
        'movies': 'Фильмы',
        'tv': 'ТВ',
        'search': 'Поиск',
        'profile': 'Профиль',
        'login': 'Войти',
        'register': 'Регистрация',
        'logout': 'Выйти',
        'navigation': 'Навигация',
        'genres': 'Жанры',
        'new_releases': 'Новинки',
        'tv_shows': 'ТВ-шоу',
        'about': 'О нас',
        'contact': 'Контакты',
        'help': 'Помощь',
        'terms': 'Условия использования',
        'privacy': 'Политика конфиденциальности',
        'footer_description': 'Ваш главный источник фильмов, ТВ-шоу и эксклюзивных оригиналов. Смотрите в любом месте, в любое время.',
        'all_rights_reserved': 'Все права защищены',
        'trending': 'В тренде',
        'top10': 'Топ 10',
        'continue_watching': 'Продолжить просмотр',
        'popular': 'Популярные',
        'recommended': 'Рекомендуем',
        'watch_now': 'Смотреть сейчас',
        'more_info': 'Подробнее',
        'play': 'Воспроизвести',
        'add_to_list': 'Добавить в список',
        'rate': 'Оценить',
        'share': 'Поделиться',
        'season': 'Сезон',
        'episode': 'Эпизод',
        'year': 'Год',
        'duration': 'Продолжительность',
        'quality': 'Качество',
        'director': 'Режиссер',
        'cast': 'В ролях',
        'storyline': 'Сюжет',
        'reviews': 'Отзывы',
        'similar': 'Похожие',
        'loading': 'Загрузка...',
        'no_results': 'Ничего не найдено',
        'try_again': 'Попробуйте снова',
        'back': 'Назад',
        'next': 'Далее',
        'previous': 'Пред.',
        'page': 'Страница',
        'of': 'из',
        'showing': 'Показано',
        'results': 'результатов',
        'filter': 'Фильтр',
        'sort_by': 'Сортировать по',
        'date_added': 'Дата добавления',
        'rating': 'Рейтинг',
        'name': 'Название',
        'release_date': 'Дата выхода',
        'language': 'Язык',
        'country': 'Страна',
        'subscription': 'Подписка',
        'plans': 'Тарифы',
        'pricing': 'Цены',
        'buy': 'Купить',
        'cancel': 'Отмена',
        'confirm': 'Подтвердить',
        'save': 'Сохранить',
        'delete': 'Удалить',
        'edit': 'Редактировать',
        'settings': 'Настройки',
        'account': 'Аккаунт',
        'password': 'Пароль',
        'email': 'Email',
        'username': 'Имя пользователя',
        'phone': 'Телефон',
        'address': 'Адрес',
        'city': 'Город',
        'zip': 'Индекс',
        'state': 'Область',
        'birthday': 'День рождения',
        'gender': 'Пол',
        'male': 'Мужской',
        'female': 'Женский',
        'other': 'Другой',
        'select': 'Выбрать',
        'required': 'Обязательно',
        'optional': 'Необязательно',
        'error': 'Ошибка',
        'success': 'Успешно',
        'warning': 'Предупреждение',
        'info': 'Информация',
        'close': 'Закрыть',
        'ok': 'OK',
        'yes': 'Да',
        'no': 'Нет',
        'all': 'Все',
        'action': 'Боевик',
        'drama': 'Драма',
        'horror': 'Ужасы',
        'scifi': 'Фантастика',
        'comedy': 'Комедия',
        'thriller': 'Триллер',
        'romance': 'Мелодрама',
        'fantasy': 'Фэнтези',
        'mystery': 'Детектив',
        'animation': 'Мультфильм',
        'documentary': 'Документальный',
        'crime': 'Криминал',
        # Top sections
        'top10_movies': 'Топ 10 фильмов для просмотра',
        'editor_pick': 'Отобрано нашей редакцией',
        'popular_movies': 'Популярные фильмы',
        'coming_soon': 'Скоро в прокате',
        'soon_on_streamit': 'Скоро на Streamit',
        'recommended_for_you': 'Рекомендуем вам',
        'based_on_history': 'На основе вашей истории просмотров',
        'movies_by_genre': 'Фильмы по жанрам',
        # Профиль
        'profile_title': 'Профиль',
        'profile_settings': 'Настройки / Профиль',
        'balance_label': 'Баланс:',
        'nav_profile': 'Профиль',
        'nav_balance': 'Баланс',
        'nav_history': 'История',
        'nav_subscriptions': 'Подписки',
        'nav_settings': 'Настройки',
        'logout_btn': 'Выйти',
        'balance_title': 'Баланс',
        'top_up': 'Пополнить',
        'quick_amounts': 'Быстрые суммы',
        'payment_history': 'История пополнений',
        'date': 'Дата',
        'amount': 'Сумма',
        'status': 'Статус',
        'history_empty': 'История пуста',
        'payment_method': 'Способ оплаты',
        'logout_all_devices': 'Выйти со всех устройств',
        'confirm_logout_all': 'Выйти со всех устройств? Текущее устройство останется.',
        'profile_card_title': 'Личные данные',
        'edit': 'Редактировать',
        'avatar_alt': 'Аватар',
        'name_label': 'Имя:',
        'email_label': 'Email:',
        'phone_label': 'Телефон:',
        'member_since': 'Дата регистрации:',
        'subscription_status': 'Статус подписки:',
        'active': 'Активна',
        'inactive': 'Не активна',
        'create_new_profile': 'Создать новый профиль',
        'logout_account': 'Выйти из аккаунта',
    }
}

def get_translation(lang, key, default=None):
    """Получить перевод для ключа"""
    if lang not in TRANSLATIONS:
        lang = 'ru'
    return TRANSLATIONS[lang].get(key, default if default else key)

def t(request, key, default=None):
    """Хелпер для получения перевода из запроса"""
    # Получаем язык из cookies или сессии
    lang = request.cookies.get('lang', 'ru') if hasattr(request, 'cookies') else 'ru'
    return get_translation(lang, key, default)







# ===== ЗАМЕНИТЬ sessions = {} на: =====
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0,
    decode_responses=True  # возвращает строки, а не bytes
)

SESSION_TTL = 86400  # 24 часа

def clear_user_sessions(user_id):
    """Удалить все старые сессии пользователя, оставить только одну новую"""
    old_tokens_key = f"user_sessions:{user_id}"
    old_tokens = redis_client.smembers(old_tokens_key)
    for token in old_tokens:
        redis_client.delete(f"session:{token}")
    redis_client.delete(old_tokens_key)

load_dotenv()

# Теперь мы берем данные из переменных окружения
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY")
CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID")



class MovieCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    year: str = Field(..., pattern=r'^\d{4}$')
    duration: Optional[str] = ""
    rating: Optional[str] = Field(None, pattern=r'^\d+\.?\d*$')
    description: Optional[str] = ""
    poster: Optional[str] = Field(default="", max_length=2_000_000)
    stream_url: Optional[str] = ""
    trailer_url: Optional[str] = ""
    genres: List[str] = []
    actors: List[str] = []
    section: Optional[str] = "trending"
    is_subscription: Optional[bool] = False
    language: Optional[str] = ""

    @field_validator('poster')
    @classmethod
    def validate_poster(cls, v):
        if not v:
            return v
        if v.startswith(('http://', 'https://', 'data:image/')):
            return v
        raise ValueError('poster must be a valid URL or base64 data URI')

# Добавьте модель для каналов
class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = ""
    quality: Optional[str] = ""
    stream_url: Optional[str] = ""
    logo: Optional[str] = Field(default="", max_length=2_000_000)
    description: Optional[str] = ""
    is_subscription: Optional[bool] = False  # ← ДОБАВИТЬ

    @field_validator('logo')
    @classmethod
    def validate_logo(cls, v):
        if not v:
            return v
        if v.startswith(('http://', 'https://', 'data:image/')):
            return v
        raise ValueError('logo must be a valid URL or base64 data URI')


# Создаём Jinja2 окружение
env = Environment(loader=FileSystemLoader("templates"))
env.filters['tojson'] = json.dumps
env.globals['t'] = t  # Добавляем функцию перевода в глобальные переменные шаблона



# Инициализация планов подписок (если таблица пуста)
def init_subscription_plans():
    plans = database.get_subscription_plans()
    if not plans:
        database.add_subscription_plan("1 Месяц", 30, 29000, "HD", 1, 7, False, 0)
        database.add_subscription_plan("3 Месяца", 90, 74000, "Full HD", 2, 14, True, 15)
        database.add_subscription_plan("12 Месяцев", 365, 199000, "4K", 4, 30, False, 30)
        logging.info("Subscription plans initialized")


init_subscription_plans()

@app.on_event("startup")
def on_startup():
    database.init_db()
    logging.info("Database tables initialized on startup")


# ===== Маршрут для переключения языка =====
@app.post("/set_language")
async def set_language(request: Request):
    form_data = await request.form()
    lang = form_data.get('lang', 'ru')
    
    # Проверяем, что язык поддерживается
    if lang not in ['ru', 'uz']:
        lang = 'ru'
    
    # Получаем referer для редиректа обратно
    referer = request.headers.get('referer', '/')
    
    response = redirect(referer)
    response.set_cookie(key='lang', value=lang, max_age=31536000, httponly=False)  # 1 год
    return response

@app.get("/set_language/{lang}")
async def set_language_get(request: Request, lang: str):
    # Проверяем, что язык поддерживается
    if lang not in ['ru', 'uz']:
        lang = 'ru'
    
    # Получаем referer для редиректа обратно
    referer = request.headers.get('referer', '/')
    
    response = redirect(referer)
    response.set_cookie(key='lang', value=lang, max_age=31536000, httponly=False)  # 1 год
    return response


def check_sign(data, secret_key):
    raw = f"{data['click_trans_id']}{data['service_id']}{secret_key}{data['merchant_trans_id']}{data['amount']}{data['action']}{data['sign_time']}"
    expected_sign = hashlib.md5(raw.encode()).hexdigest()
    return expected_sign == data['sign_string']



async def handle_prepare(data: dict):
    # 1️⃣ Проверяем подпись (sign_string)
    if not check_sign(data, CLICK_SECRET_KEY):
        return {
            "click_trans_id": data["click_trans_id"],
            "merchant_trans_id": data["merchant_trans_id"],
            "merchant_prepare_id": 0,
            "error": -1,
            "error_note": "SIGN CHECK FAILED!"
        }

    # 2️⃣ Проверяем, что пользователь существует
    merchant_trans_id = data.get("merchant_trans_id")  # "5"
    
    # Преобразуем строку в число
    try:
        user_id = int(merchant_trans_id)
    except ValueError:
        # Если merchant_trans_id не число — возвращаем ошибку
        return {
            "click_trans_id": data["click_trans_id"],
            "merchant_trans_id": data["merchant_trans_id"],
            "merchant_prepare_id": 0,
            "error": -5,
            "error_note": "USER NOT FOUND"
        }
    
    # Ищем пользователя в БД
    user = database.get_user_by_id(user_id)
    
    if user is None:
        # ❌ Пользователь не найден — возвращаем ошибку -5
        return {
            "click_trans_id": data["click_trans_id"],
            "merchant_trans_id": data["merchant_trans_id"],
            "merchant_prepare_id": 0,
            "error": -5,
            "error_note": "USER NOT FOUND"
        }


    # После проверки подписи и пользователя:
    prepare_id = database.save_click_prepare(
        click_trans_id=data["click_trans_id"],
        click_paydoc_id=data.get("click_paydoc_id", 0),
        merchant_trans_id=str(user_id),
        amount=float(data["amount"]),
        sign_time=data.get("sign_time", "")
    )

    # ✅ Добавить успешный ответ с prepare_id
    return {
        "click_trans_id": data["click_trans_id"],
        "merchant_trans_id": data["merchant_trans_id"],
        "merchant_prepare_id": prepare_id,
        "error": 0,
        "error_note": "SUCCESS"
    }




async def handle_complete(data: dict):
    # 1️⃣ Проверяем подпись
    if not check_sign(data, CLICK_SECRET_KEY):
        return {
            "click_trans_id": data["click_trans_id"],
            "merchant_trans_id": data["merchant_trans_id"],
            "error": -1,
            "error_note": "SIGN CHECK FAILED!"
        }

    # 2️⃣ Находим пользователя по merchant_trans_id (это ID пользователя)
    try:
        user_id = int(data["merchant_trans_id"])
    except ValueError:
        return {
            "click_trans_id": data["click_trans_id"],
            "merchant_trans_id": data["merchant_trans_id"],
            "error": -5,
            "error_note": "USER NOT FOUND"
        }

    user = database.get_user_by_id(user_id)
    if user is None:
        return {
            "click_trans_id": data["click_trans_id"],
            "merchant_trans_id": data["merchant_trans_id"],
            "error": -5,
            "error_note": "USER NOT FOUND"
        }


    # Сохраняем статус "confirmed" в БД
    database.update_click_status(data["click_trans_id"], "confirmed")
    
    # Активируем подписку
    success = database.activate_user_subscription(user_id, "premium", 30)
    
    if success:

        # ✅ НАЧИСЛЯЕМ РЕФЕРАЛЬНЫЙ БОНУС
        database.process_referral_bonus(user_id, data["amount"])


        return {
            "click_trans_id": data["click_trans_id"],
            "merchant_trans_id": data["merchant_trans_id"],
            "error": 0,
            "error_note": "SUCCESS"
        }
    else:
        return {
            "click_trans_id": data["click_trans_id"],
            "merchant_trans_id": data["merchant_trans_id"],
            "error": -9,
            "error_note": "TRANSACTION FAILED"
        }





@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    trending = database.get_movies_by_section("trending")
    top10 = database.get_movies_by_section("top10")
    continue_watching = database.get_movies_by_section("continue_watching")
    popular = database.get_movies_by_section("popular")
    recommended = database.get_movies_by_section("recommended")
    new_releases = database.get_movies_by_section("new_releases")
    template = env.get_template("index.html")
    hero_movies = database.get_hero_movies(5)  # Получаем 5 топ фильмов


    return HTMLResponse(template.render(
        request=request,
        trending=trending,
        top10=top10,
        continue_watching=continue_watching,
        popular=popular,
        recommended=recommended,
        new_releases=new_releases,
        hero_movies=hero_movies,
        active_page='home'
    ), media_type="text/html")


@app.get("/home_backup", response_class=HTMLResponse)
def home_backup(request: Request):
    trending = database.get_movies_by_section("trending")
    top10 = database.get_movies_by_section("top10")
    continue_watching = database.get_movies_by_section("continue_watching")
    popular = database.get_movies_by_section("popular")
    recommended = database.get_movies_by_section("recommended")
    new_releases = database.get_movies_by_section("new_releases")
    template = env.get_template("index.backup.html")
    hero_movies = database.get_hero_movies(5)  # Получаем 5 топ фильмов

    return HTMLResponse(template.render(
        request=request,
        trending=trending,
        top10=top10,
        continue_watching=continue_watching,
        popular=popular,
        recommended=recommended,
        new_releases=new_releases,
        hero_movies=hero_movies,
        active_page='home'
    ), media_type="text/html")






@app.get("/api/movies")
def get_movies(
    genre: Optional[str] = None,
    year: Optional[str] = None,
    min_rating: Optional[float] = None,
    duration: Optional[str] = None,
    language: Optional[str] = None,
    section: Optional[str] = None
):
    if section:
        return database.get_movies_by_section(section)
    return database.get_filtered_movies(
        genre=genre,
        year=year,
        min_rating=min_rating,
        duration=duration,
        language=language
    )


@app.post("/api/movies")
async def add_movie(movie: MovieCreate):
    movie_id = database.add_movie(
        name=movie.name,
        year=movie.year,
        duration=movie.duration,
        rating=movie.rating,
        description=movie.description,
        poster=movie.poster,
        stream_url=movie.stream_url,
        trailer_url=movie.trailer_url,
        genres=movie.genres,
        actors=movie.actors,
        section=movie.section,
        is_subscription=movie.is_subscription,
        language=movie.language,
    )
    return {"id": movie_id, "status": "added"}    


@app.delete("/api/movies/{movie_id}")
def delete_movie(movie_id: int):
    database.delete_movie(movie_id)
    return {"status": "deleted"}

# API для ТВ-каналов
@app.get("/api/channels")
def get_channels():
    return database.get_all_channels()


# API для пользователей
@app.get("/api/users")
def get_users():
    return database.get_all_users()


@app.post("/api/channels")
async def add_channel(channel: ChannelCreate):
    channel_id = database.add_channel(
        name=channel.name,
        category=channel.category,
        quality=channel.quality,
        stream_url=channel.stream_url,
        logo=channel.logo,
        description=channel.description,
        is_subscription=channel.is_subscription  # ← ДОБАВИТЬ
    )
    return {"id": channel_id, "status": "added"}


@app.get("/api/auth/status")
def get_auth_status(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token:
        # Проверяем в Redis
        user_id = redis_client.get(f"session:{session_token}")
        if user_id:
            user = database.get_user_by_id(int(user_id))
            if user:
                return {"authenticated": True, "user_id": int(user_id), "username": user["username"]}
    return {"authenticated": False}


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    template = env.get_template("registrate.html")  # нужно создать
    return HTMLResponse(template.render(request=request))

@app.get("/register", response_class=HTMLResponse) 
def register_page(request: Request):
    template = env.get_template("registrate.html")  # уже существует
    return HTMLResponse(template.render(request=request))


@app.delete("/api/channels/{channel_id}")
def delete_channel(channel_id: int):
    database.delete_channel(channel_id)
    return {"status": "deleted"}

# Админка
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    template = env.get_template("admin/index.html")
    return HTMLResponse(template.render(request=request), media_type="text/html")



@app.get("/movies", response_class=HTMLResponse)
def movies_page(request: Request):
    movies = database.get_all_movies()
    top10 = database.get_movies_by_section("top10")
    popular = database.get_movies_by_section("popular")
    upcoming = database.get_movies_by_section("upcoming")
    recommended = database.get_movies_by_section("recommended")
    
    template = env.get_template("movies.html")
    return HTMLResponse(template.render(
        request=request,
        movies=movies,
        top10=top10,
        popular=popular,
        upcoming=upcoming,
        recommended=recommended,
        active_page='movies'
    ), media_type="text/html")






@app.get("/movies/{movie_id}", response_class=HTMLResponse)
def movie_watch_page(movie_id: str, request: Request):
    try:
        movie_id = int(movie_id)
    except ValueError:
        return HTMLResponse("<h1>Страница не найдена</h1>", status_code=404)
    
    # Увеличить счётчик просмотров
    database.increment_views(movie_id)
    
    # Загрузить данные фильма
    movie = database.get_movie_by_id(movie_id)
    if not movie:
        return HTMLResponse("<h1>Фильм не найден</h1>", status_code=404)
    
    # Проверяем аутентификацию пользователя
    session_token = request.cookies.get("session_token")
    user = None
    user_subscription = None
    
    if session_token:
        user_id = redis_client.get(f"session:{session_token}")
        if user_id:
            user = database.get_user_by_id_with_subscription(int(user_id))
            if user:
                user_subscription = user["subscription"]
    
    # Загрузить похожие фильмы (только с ID)
    recommended = [m for m in database.get_movies_by_section("recommended")[:8] if m and m.get("id")]
    
    template = env.get_template("movies_watch.html")
    return HTMLResponse(template.render(
        request=request,
        movie=movie,
        recommended=recommended,
        user=user,
        user_subscription=user_subscription
    ), media_type="text/html")


@app.get("/livetv", response_class=HTMLResponse)
def livetv_page(request: Request):
    channels = database.get_all_channels()
    
    # Получить уникальные категории
    categories = sorted(set(ch.get('category') for ch in channels if ch.get('category')))
    
    template = env.get_template("livetv.html")
    return HTMLResponse(template.render(
        request=request, 
        channels=channels,
        categories=categories, # передать категории
        active_page='livetv'  
    ), media_type="text/html")



@app.get("/livetv_backup", response_class=HTMLResponse)
def livetv_backup_page(request: Request):
    channels = database.get_all_channels()
    
    # Получить уникальные категории
    categories = sorted(set(ch.get('category') for ch in channels if ch.get('category')))
    
    template = env.get_template("livetv_backup.html")
    return HTMLResponse(template.render(
        request=request, 
        channels=channels,
        categories=categories  # передать категории
    ), media_type="text/html")



@app.get("/livetv/{channel_id}", response_class=HTMLResponse)
def livetv_player_page(channel_id: str, request: Request):
    try:
        channel_id = int(channel_id)
    except ValueError:
        return HTMLResponse("<h1>Страница не найдена</h1>", status_code=404)
    
    channel = database.get_channel_by_id(channel_id)
    if not channel:
        return HTMLResponse("<h1>Канал не найден</h1>", status_code=404)
    
    template = env.get_template("livetv_player.html")
    return HTMLResponse(template.render(
        request=request,
        channel=channel
    ), media_type="text/html")




@app.get("/api/movies/search")
def search_movies_api(q: str):
    return database.search_movies(q)





@app.post("/api/auth/register")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    referral_code: str = Form(default="")  # ← добавить
):
    logging.info(f"Registration attempt: username={username}, email={email}")
    
    try:
        if database.get_user_by_username(username):
            logging.warning(f"Username already exists: {username}")
            raise HTTPException(status_code=400, detail="Username already exists")
        
        if database.get_user_by_email(email):
            logging.warning(f"Email already exists: {email}")
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user_id = database.create_user(username, email, password)

        # ✅ ОБРАБОТКА РЕФЕРАЛЬНОГО КОДА
        if referral_code:
            database.apply_referral(user_id, referral_code)
    
        # Автологин + Redis сессия
        session_token = secrets.token_urlsafe(32)
        redis_client.setex(f"session:{session_token}", SESSION_TTL, str(user_id))
        
        response = JSONResponse({"status": "success", "user_id": user_id})
        response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=SESSION_TTL)
        return response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Registration failed for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")


# API: Получить все планы подписок
@app.get("/api/admin/subscription-plans")
def get_subscription_plans():
    return database.get_subscription_plans()

# API: Сохранить изменения плана подписки
@app.put("/api/admin/subscription-plans/{plan_id}")
async def update_subscription_plan(plan_id: int, plan_data: dict):
    database.update_subscription_plan(plan_id, plan_data)
    return {"status": "updated"}

# API: Получить общие настройки
@app.get("/api/admin/settings")
def get_settings():
    return database.get_settings()

# API: Сохранить общие настройки
@app.put("/api/admin/settings")
async def update_settings(settings: dict):
    database.update_settings(settings)
    return {"status": "updated"}




@app.post("/api/auth/login")
async def login_user(email_or_phone: str = Form(...), password: str = Form(...)):
    user = database.verify_user(email_or_phone, password)
    if user:
        # Шаг 1: Удалить все старые сессии
        clear_user_sessions(user["id"])
        
        # Шаг 2: Создать новую
        session_token = secrets.token_urlsafe(32)
        redis_client.setex(f"session:{session_token}", SESSION_TTL, str(user["id"]))
        redis_client.sadd(f"user_sessions:{user['id']}", session_token)
        
        response = JSONResponse({"status": "success", "user_id": user["id"]})
        response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=SESSION_TTL)
        return response
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/api/auth/logout")
async def logout_user(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token:
        redis_client.delete(f"session:{session_token}")
    
    response = JSONResponse({"status": "success"})
    response.delete_cookie("session_token")
    return response


# API для работы с подписками
@app.get("/api/subscription/status")
def get_subscription_status(request: Request):
    """Получить статус подписки текущего пользователя"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        return {"authenticated": False, "subscription": None}
    
    user_id = redis_client.get(f"session:{session_token}")
    if not user_id:
        return {"authenticated": False, "subscription": None}
    
    subscription = database.check_user_subscription(int(user_id))
    return {"authenticated": True, "subscription": subscription}


@app.post("/api/subscription/activate")
async def activate_subscription(request: Request, subscription_type: str = Form(default="premium")):
    """Активировать подписку для пользователя"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = redis_client.get(f"session:{session_token}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Определяем длительность в зависимости от типа подписки
    duration_days = 30 if subscription_type == "premium" else 7
    
    success = database.activate_user_subscription(int(user_id), subscription_type, duration_days)
    if success:
        subscription = database.check_user_subscription(int(user_id))
        return {"status": "success", "subscription": subscription}
    else:
        raise HTTPException(status_code=500, detail="Failed to activate subscription")


@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    session_token = request.cookies.get("session_token")
    user = None
    
    if session_token:
        user_id = redis_client.get(f"session:{session_token}")
        if user_id:
            user = database.get_user_by_id(int(user_id))
    
    if not user:
        return HTMLResponse("<script>window.location.href='/login'</script>", status_code=302)
    
    # Получаем планы подписок из БД
    subscription_plans = database.get_subscription_plans()

    # После получения планов подписок:
    click_transactions = database.get_user_click_transactions(user["id"])
        
    template = env.get_template("profile.html")

    # И передать в шаблон:
    return HTMLResponse(template.render(
        request={},
        user=user,
        subscription_plans=subscription_plans,
        click_transactions=click_transactions,  # ← добавить
        tab=request.query_params.get("tab", "profile")
    ))







@app.post("/api/click/webhook")
async def click_webhook(request: Request):
    data = await request.json()
    # data будет содержать все параметры, которые Click отправляет:
    # click_trans_id, service_id, click_paydoc_id, merchant_trans_id,
    # amount, action, error, error_note, sign_time, sign_string
    
    action = data.get("action")  # 0 = Prepare, 1 = Complete
    
    if action == 0:
        return await handle_prepare(data)
    elif action == 1:
        return await handle_complete(data)
    else:
        return {"error": -3, "error_note": "Action not found"}


@app.get("/api/admin/referral-settings")
def get_referral_settings():
    settings = database.get_settings()
    return {
        "referral_percent": settings.get("referral_percent", 10) if settings else 10
    }

@app.put("/api/admin/referral-settings")
async def update_referral_settings(data: dict):
    referral_percent = data.get("referral_percent", 10)
    # Сохраняем в AppSettings
    current = database.get_settings()
    if current:
        database.update_settings({"referral_percent": referral_percent})
    return {"status": "updated"}


@app.get("/api/referral/check/{code}")
def check_referral_code(code: str):
    """Проверяет, существует ли реферальный код"""
    user = database.get_user_by_referral_code(code)
    if user:
        return {"valid": True, "username": user["username"]}
    return {"valid": False}


if __name__ == "__main__":
    database.init_db()  # Вызывается только если файл запущен напрямую
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)