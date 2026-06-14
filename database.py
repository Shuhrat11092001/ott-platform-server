# database.py
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from sqlalchemy.types import JSON
import hashlib
from datetime import datetime
import logging
from sqlalchemy import text

DB_URL = "sqlite:///ott.db"

class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    year: Mapped[Optional[str]] = mapped_column(default=None)
    duration: Mapped[Optional[str]] = mapped_column(default=None)
    rating: Mapped[Optional[str]] = mapped_column(default=None)
    description: Mapped[Optional[str]] = mapped_column(default=None)
    poster: Mapped[Optional[str]] = mapped_column(default=None)
    genres: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    actors: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    stream_url: Mapped[Optional[str]] = mapped_column(default=None)  # <-- добавить
    trailer_url: Mapped[Optional[str]] = mapped_column(default=None)
    section: Mapped[Optional[str]] = mapped_column(default="trending")
    views: Mapped[int] = mapped_column(default=0)
    reviews: Mapped[int] = mapped_column(default=0)
    is_subscription: Mapped[bool] = mapped_column(default=False)  # ← новое
    language: Mapped[Optional[str]] = mapped_column(default=None)  # Русский, Узбекский, Английский

class TVChannel(Base):
    __tablename__ = "tv_channels"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[Optional[str]] = mapped_column(default=None)
    quality: Mapped[Optional[str]] = mapped_column(default=None)
    stream_url: Mapped[Optional[str]] = mapped_column(default=None)
    logo: Mapped[Optional[str]] = mapped_column(default=None)
    description: Mapped[Optional[str]] = mapped_column(default=None)
    is_subscription: Mapped[bool] = mapped_column(default=False)
    
    


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[str] = mapped_column(default=lambda: datetime.now().isoformat())
    is_active: Mapped[bool] = mapped_column(default=True)
    subscription_type: Mapped[Optional[str]] = mapped_column(default=None)  # 'basic', 'premium', etc.
    subscription_expires_at: Mapped[Optional[str]] = mapped_column(default=None)  # ISO datetime
    has_subscription: Mapped[bool] = mapped_column(default=False)

    referral_code: Mapped[Optional[str]] = mapped_column(unique=True, default=None)  # уникальный код пользователя
    referred_by: Mapped[Optional[int]] = mapped_column(default=None)  # ID пользователя, кто пригласил
    # Вместо referral_bonus_days или вместе с ним:
    referral_earnings: Mapped[int] = mapped_column(default=0)  # накоплено сум (в тийинах)
    referral_percent: Mapped[int] = mapped_column(default=10)   # % от подписки, который получает пригласивший

# database.py
class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)          # "1 Месяц", "3 Месяца", "12 Месяцев"
    duration_days: Mapped[int] = mapped_column(nullable=False) # 30, 90, 365
    price: Mapped[int] = mapped_column(nullable=False)         # 29000, 74000, 199000
    quality: Mapped[str] = mapped_column(default="HD")         # HD, FullHD, 4K
    devices: Mapped[int] = mapped_column(default=1)            # 1, 2, 4
    archive_days: Mapped[int] = mapped_column(default=7)       # 7, 14, 30
    is_popular: Mapped[bool] = mapped_column(default=False)    # popular badge
    discount_percent: Mapped[int] = mapped_column(default=0)   # 0%, 15%, 30%
    is_active: Mapped[bool] = mapped_column(default=True)



class AppSettings(Base):
    __tablename__ = "app_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    trial_days: Mapped[int] = mapped_column(default=7)
    currency: Mapped[str] = mapped_column(default="UZS")
    auto_renewal: Mapped[bool] = mapped_column(default=True)
    notifications_enabled: Mapped[bool] = mapped_column(default=True)
    referral_percent: Mapped[int] = mapped_column(default=10)  # % вознаграждения за реферала


class ClickTransaction(Base):
    __tablename__ = "click_transactions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    click_trans_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    click_paydoc_id: Mapped[int] = mapped_column(nullable=False)
    merchant_trans_id: Mapped[str] = mapped_column(nullable=False)  # user_id
    amount: Mapped[float] = mapped_column(nullable=False)
    action: Mapped[int] = mapped_column(nullable=False)  # 0=Prepare, 1=Complete
    status: Mapped[str] = mapped_column(default="pending")  # pending, confirmed, cancelled
    sign_time: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[str] = mapped_column(default=lambda: datetime.now().isoformat())


class ReferralTransaction(Base):
    __tablename__ = "referral_transactions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    referrer_id: Mapped[int] = mapped_column(nullable=False)  # кто пригласил (получает бонус)
    referred_user_id: Mapped[int] = mapped_column(nullable=False)  # кто купил
    amount: Mapped[int] = mapped_column(nullable=False)  # сумма в тийинах
    percent: Mapped[int] = mapped_column(nullable=False)  # какой % был применён
    created_at: Mapped[str] = mapped_column(default=lambda: datetime.now().isoformat())
    status: Mapped[str] = mapped_column(default="pending")  # pending, paid, withdrawn



engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)



def get_settings() -> Optional[Dict]:
    db = SessionLocal()
    try:
        setting = db.query(AppSettings).first()  # Получаем первую (единственную) запись
        if setting:
            return {
                "trial_days": setting.trial_days,
                "currency": setting.currency,
                "auto_renewal": setting.auto_renewal,
                "notifications_enabled": setting.notifications_enabled
            }
        return None
    finally:
        db.close()


def update_settings(settings: dict):
    db = SessionLocal()
    try:
        existing = db.query(AppSettings).first()
        if existing:
            existing.trial_days = settings.get("trial_days", existing.trial_days)
            existing.currency = settings.get("currency", existing.currency)
            existing.auto_renewal = settings.get("auto_renewal", existing.auto_renewal)
            existing.notifications_enabled = settings.get("notifications_enabled", existing.notifications_enabled)
        else:
            db.add(AppSettings(**settings))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()




# ─── Movies ─────────────────────────────────────────

def get_all_movies() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = db.query(Movie).order_by(Movie.id.desc()).all()
        return [_movie_to_dict(m) for m in rows]
    finally:
        db.close()


def get_filtered_movies(
    genre: Optional[str] = None,
    year: Optional[str] = None,
    min_rating: Optional[float] = None,
    duration: Optional[str] = None,
    language: Optional[str] = None
) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        query = db.query(Movie)
        
        # Фильтр по жанру (JSON массив)
        if genre and genre != 'all':
            query = query.filter(Movie.genres.contains([genre]))
        
        # Фильтр по году (фильмы с года и новее)
        if year:
            query = query.filter(Movie.year >= year)
        
        # Фильтр по минимальному рейтингу
        if min_rating:
            query = query.filter(Movie.rating >= str(min_rating))
        
        # Фильтр по длительности
        if duration and duration != 'all':
            if duration == 'short':
                query = query.filter(Movie.duration < '90')
            elif duration == 'medium':
                query = query.filter(Movie.duration >= '90', Movie.duration <= '120')
            elif duration == 'long':
                query = query.filter(Movie.duration > '120')
        
        # Сделать:
        if language and language != 'all':
            query = query.filter(Movie.language == language)


        return [_movie_to_dict(m) for m in query.order_by(Movie.id.desc()).all()]
    finally:
        db.close()


def get_channel_by_id(channel_id: int) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        channel = db.query(TVChannel).filter(TVChannel.id == channel_id).first()
        if not channel:
            return None
        return {
            "id": channel.id,
            "name": channel.name,
            "category": channel.category,
            "quality": channel.quality,
            "stream_url": channel.stream_url,
            "logo": channel.logo,
            "description": channel.description,
            "is_subscription": channel.is_subscription or False
        }
    finally:
        db.close()


def get_movies_by_section(section: str) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        query = db.query(Movie)
        if section in ("trending", "popular"):
            query = query.order_by(Movie.views.desc())
        elif section == "top10":
            query = query.order_by(Movie.rating.desc(), Movie.reviews.desc()).limit(10)
        elif section == "new_releases":
            query = query.order_by(Movie.year.desc())
        elif section == "recommended":
            query = query.order_by(Movie.rating.desc())
        else:
            query = query.order_by(Movie.id.desc())
        return [_movie_to_dict(m) for m in query.all()]
    finally:
        db.close()

def get_movie_by_id(movie_id: int) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            return _movie_to_dict(movie)
        return None
    finally:
        db.close()

def add_movie(name: str, year: str, duration: str, rating: str,
              description: str, poster: str, genres: List[str],
              actors: List[str], stream_url: str = "", trailer_url: str = "", section: str = "trending", is_subscription: bool = False, language="") -> int:
    db = SessionLocal()
    try:
        movie = Movie(
            name=name, year=year, duration=duration, rating=rating,
            description=description, poster=poster,
            genres=genres, actors=actors, stream_url=stream_url, trailer_url=trailer_url, section=section, is_subscription=is_subscription, language=language
        )
        db.add(movie)
        db.commit()
        return movie.id
    finally:
        db.close()


def search_movies(query: str) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        search = f"%{query}%"
        rows = db.query(Movie).filter(Movie.name.ilike(search)).all()
        return [_movie_to_dict(m) for m in rows]
    finally:
        db.close()



def delete_movie(movie_id: int):
    db = SessionLocal()
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            db.delete(movie)
            db.commit()
    finally:
        db.close()

def increment_views(movie_id: int):
    db = SessionLocal()
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            movie.views += 1
            db.commit()
    finally:
        db.close()

def add_review(movie_id: int):
    db = SessionLocal()
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            movie.reviews += 1
            db.commit()
    finally:
        db.close()

# ─── TV Channels ────────────────────────────────────

def get_all_channels() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = db.query(TVChannel).order_by(TVChannel.id.desc()).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "category": c.category,
                "quality": c.quality,
                "stream_url": c.stream_url,
                "logo": c.logo,
                "description": c.description,
                "is_subscription": c.is_subscription or False,  # ← ДОБАВИТЬ
            }
            for c in rows
        ]
    finally:
        db.close()

def add_channel(name, category, quality, stream_url, logo, description, is_subscription=False) -> int:
    db = SessionLocal()
    try:
        ch = TVChannel(
            name=name, category=category, quality=quality,
            stream_url=stream_url, logo=logo, description=description, is_subscription=is_subscription
        )
        db.add(ch)
        db.commit()
        return ch.id
    finally:
        db.close()

def delete_channel(channel_id: int):
    db = SessionLocal()
    try:
        ch = db.query(TVChannel).filter(TVChannel.id == channel_id).first()
        if ch:
            db.delete(ch)
            db.commit()
    finally:
        db.close()

# ─── Helpers ────────────────────────────────────────

def _movie_to_dict(m: Movie) -> Dict[str, Any]:
    return {
        "id": m.id,
        "name": m.name,
        "year": m.year,
        "duration": m.duration,
        "rating": m.rating,
        "description": m.description,
        "poster": m.poster,
        "genres": m.genres or [],
        "actors": m.actors or [],
        "stream_url": m.stream_url or "",
        "section": m.section or "trending",
        "views": m.views,
        "reviews": m.reviews,
        "is_subscription": m.is_subscription or False,  
        "language": m.language or "",
    }


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
 




def generate_referral_code(username: str) -> str:
    """Генерирует уникальный реферальный код на основе имени пользователя"""
    # Берём первые 4 буквы имени + 4 случайных символа
    prefix = username[:4].upper() if len(username) >= 4 else username.upper().ljust(4, 'X')
    suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"{prefix}{suffix}"

def create_user(username: str, email: str, password: str) -> int:
    db = SessionLocal()
    try:
        # Генерируем уникальный реферальный код
        referral_code = generate_referral_code(username)
        # Проверяем уникальность
        while db.query(User).filter(User.referral_code == referral_code).first():
            referral_code = generate_referral_code(username)
        
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            referral_code=referral_code  # ← ДОБАВИТЬ
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id
    except Exception as e:
        db.rollback()
        logging.error(f"Database error creating user: {str(e)}")
        raise
    finally:
        db.close()





def get_user_by_username(username: str) -> Optional[Dict]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password_hash
            }
        return None
    finally:
        db.close()


def get_user_by_email(email: str) -> Optional[Dict]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password_hash
            }
        return None
    finally:
        db.close()

 
def verify_user(username_or_email: str, password: str) -> Optional[Dict]:
    # Сначала ищем по email
    user = get_user_by_email(username_or_email)
    if not user:
        # Если не нашли, ищем по username
        user = get_user_by_username(username_or_email)
    if user and user["password_hash"] == hash_password(password):
        return user
    return None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        return None
    finally:
        db.close()


def get_all_users() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = db.query(User).order_by(User.id.desc()).all()
        return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "created_at": u.created_at,
                "is_active": u.is_active,
                "subscription_type": u.subscription_type,
                "subscription_expires_at": u.subscription_expires_at,
                "has_subscription": u.has_subscription
            }
            for u in rows
        ]
    finally:
        db.close()

# ─── Subscription Functions ─────────────────────────────




def check_user_subscription(user_id: int) -> Dict[str, Any]:
    """Проверяет статус подписки пользователя"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"has_subscription": False, "subscription_type": None, "is_expired": True}
        
        # Если нет подписки
        if not user.has_subscription or not user.subscription_expires_at:
            return {"has_subscription": False, "subscription_type": None, "is_expired": True}
        
        # Проверяем срок действия
        from datetime import datetime
        expiry_date = datetime.fromisoformat(user.subscription_expires_at)
        now = datetime.now()
        
        is_expired = now > expiry_date
        
        # Если подписка истекла, обновляем статус
        if is_expired:
            user.has_subscription = False
            db.commit()
        
        return {
            "has_subscription": user.has_subscription and not is_expired,
            "subscription_type": user.subscription_type,
            "is_expired": is_expired,
            "expires_at": user.subscription_expires_at
        }
    finally:
        db.close()

def activate_user_subscription(user_id: int, subscription_type: str = "premium", duration_days: int = 30) -> bool:
    """Активирует подписку для пользователя"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        from datetime import datetime, timedelta
        expiry_date = datetime.now() + timedelta(days=duration_days)
        
        user.has_subscription = True
        user.subscription_type = subscription_type
        user.subscription_expires_at = expiry_date.isoformat()
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logging.error(f"Error activating subscription for user {user_id}: {str(e)}")
        return False
    finally:
        db.close()


# database.py
def get_subscription_plans() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).order_by(SubscriptionPlan.price).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "duration_days": p.duration_days,
                "price": p.price,
                "quality": p.quality,
                "devices": p.devices,
                "archive_days": p.archive_days,
                "is_popular": p.is_popular,
                "discount_percent": p.discount_percent
            }
            for p in plans
        ]
    finally:
        db.close()




def add_subscription_plan(name, duration_days, price, quality="HD", devices=1, archive_days=7, is_popular=False, discount_percent=0) -> int:
    db = SessionLocal()
    try:
        plan = SubscriptionPlan(
            name=name, duration_days=duration_days, price=price,
            quality=quality, devices=devices, archive_days=archive_days,
            is_popular=is_popular, discount_percent=discount_percent
        )
        db.add(plan)
        db.commit()
        return plan.id
    finally:
        db.close()


def update_subscription_plan(plan_id: int, plan_data: dict) -> bool:
    db = SessionLocal()
    try:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        if not plan:
            return False
        for key, value in plan_data.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()



def get_user_by_id_with_subscription(user_id: int) -> Optional[Dict]:
    """Получает информацию о пользователе включая данные о подписке"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            subscription_info = check_user_subscription(user_id)
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "subscription": subscription_info
            }
        return None
    finally:
        db.close()


def get_hero_movies(limit: int = 5) -> List[Dict[str, Any]]:
    """Получить топ фильмы для hero секции по просмотрам и рейтингу"""
    db = SessionLocal()
    try:
        # Сортируем по просмотрам, затем по рейтингу
        movies = db.query(Movie).order_by(
            Movie.views.desc(), 
            Movie.rating.desc()
        ).limit(limit).all()
        return [_movie_to_dict(m) for m in movies]
    finally:
        db.close()



def save_click_prepare(
    click_trans_id: int,
    click_paydoc_id: int,
    merchant_trans_id: str,
    amount: float,
    sign_time: str
) -> int:
    """Сохраняет запрос Prepare от Click в БД.
    Возвращает id созданной записи (merchant_prepare_id)."""
    db = SessionLocal()
    try:
        # Создаем новую запись
        transaction = ClickTransaction(
            click_trans_id=click_trans_id,
            click_paydoc_id=click_paydoc_id,
            merchant_trans_id=merchant_trans_id,
            amount=amount,
            action=0,                  # Prepare
            status="pending",          # Статус: ожидает подтверждения
            sign_time=sign_time
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)  # получаем id
        return transaction.id    # ← это и будет merchant_prepare_id!
    except Exception as e:
        db.rollback()
        logging.error(f"Error saving click prepare: {str(e)}")
        raise
    finally:
        db.close()


def get_click_transaction(click_trans_id: int) -> Optional[Dict]:
    """Находит транзакцию Click по click_trans_id"""
    db = SessionLocal()
    try:
        t = db.query(ClickTransaction).filter(
            ClickTransaction.click_trans_id == click_trans_id
        ).first()
        
        if not t:
            return None
        
        return {
            "id": t.id,
            "click_trans_id": t.click_trans_id,
            "click_paydoc_id": t.click_paydoc_id,
            "merchant_trans_id": t.merchant_trans_id,
            "amount": t.amount,
            "action": t.action,
            "status": t.status,
            "sign_time": t.sign_time
        }
    finally:
        db.close()


def update_click_status(click_trans_id: int, status: str) -> bool:
    """Обновляет статус транзакции Click.
    status: 'confirmed' или 'cancelled'"""
    db = SessionLocal()
    try:
        t = db.query(ClickTransaction).filter(
            ClickTransaction.click_trans_id == click_trans_id
        ).first()
        
        if not t:
            return False
        
        t.status = status
        t.action = 1  # Complete
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating click transaction: {str(e)}")
        return False
    finally:
        db.close()








def init_db():
    """Инициализация БД: создаёт недостающие таблицы и добавляет недостающие колонки"""
    
    # === ШАГ 1: Создаём новые таблицы (если есть) ===
    Base.metadata.create_all(bind=engine)
    
    # === ШАГ 2: Добавляем недостающие колонки в существующие таблицы ===
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    
    for table_name, table in Base.metadata.tables.items():
        existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
        model_columns = set(table.columns.keys())
        missing_columns = model_columns - existing_columns
        
        if missing_columns:
            print(f"📦 Таблица '{table_name}': добавляются колонки {missing_columns}")
            
            with engine.connect() as conn:
                for col_name in missing_columns:
                    column = table.columns[col_name]
                    
                    # ✅ Получаем корректное SQL-представление типа
                    col_type_sql = column.type.compile(dialect=engine.dialect)
                    
                    nullable = "NULL" if column.nullable else "NOT NULL"
                    
                    default = ""
                    if column.default is not None:
                        default_value = column.default.arg
                        if isinstance(default_value, str):
                            default = f"DEFAULT '{default_value}'"
                        else:
                            default = f"DEFAULT {default_value}"
                    
                    # Формируем SQL запрос
                    sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type_sql} {nullable} {default}"
                    
                    try:
                        conn.execute(text(sql))
                        print(f"  ✅ Колонка '{col_name}' добавлена в '{table_name}'")
                    except Exception as e:
                        print(f"  ⚠️ Не удалось добавить колонку '{col_name}': {e}")
                
                conn.commit()
    
    print("✅ База данных инициализирована")




def get_user_click_transactions(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Получает историю транзакций пользователя из БД"""
    db = SessionLocal()
    try:
        transactions = db.query(ClickTransaction).filter(
            ClickTransaction.merchant_trans_id == str(user_id)
        ).order_by(ClickTransaction.created_at.desc()).limit(limit).all()
        
        return [
            {
                "amount": t.amount,
                "status": t.status,
                "created_at": t.created_at
            }
            for t in transactions
        ]
    finally:
        db.close()



def process_referral_bonus(buyer_user_id: int, payment_amount: float):
    """
    Когда пользователь покупает подписку — 
    начисляем процент тому, кто его пригласил.
    """
    db = SessionLocal()
    try:
        buyer = db.query(User).filter(User.id == buyer_user_id).first()
        if not buyer or not buyer.referred_by:
            return  # никто не приглашал
        
        referrer = db.query(User).filter(User.id == buyer.referred_by).first()
        if not referrer:
            return
        
        # Расчёт процента
        percent = referrer.referral_percent or 10  # по умолчанию 10%
        bonus_amount = int(payment_amount * percent / 100)
        
        # Накапливаем
        referrer.referral_earnings = (referrer.referral_earnings or 0) + bonus_amount
        
        # Сохраняем в историю
        transaction = ReferralTransaction(
            referrer_id=referrer.id,
            referred_user_id=buyer.id,
            amount=bonus_amount,
            percent=percent
        )
        db.add(transaction)
        
        # + бонусные дни (опционально)
        bonus_days = int(30 * percent / 100)  # например, 10% от 30 дней = 3 дня
        if bonus_days > 0:
            referrer.referral_bonus_days = (referrer.referral_bonus_days or 0) + bonus_days
        
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Error processing referral bonus: {str(e)}")
    finally:
        db.close()

 
        

def apply_referral(new_user_id: int, referral_code: str):
    """
    Применяет реферальный код при регистрации.
    Находит пользователя с таким referral_code и связывает его с новым пользователем.
    """
    db = SessionLocal()
    try:
        # Ищем пользователя с таким referral_code
        referrer = db.query(User).filter(User.referral_code == referral_code).first()
        if not referrer:
            logging.warning(f"Referral code not found: {referral_code}")
            return False
        
        # Обновляем нового пользователя: указываем, кто его пригласил
        new_user = db.query(User).filter(User.id == new_user_id).first()
        if new_user:
            new_user.referred_by = referrer.id
            db.commit()
            logging.info(f"User {new_user_id} referred by {referrer.id} (code: {referral_code})")
            return True
        
        return False
    except Exception as e:
        db.rollback()
        logging.error(f"Error applying referral: {str(e)}")
        return False
    finally:
        db.close()





def get_user_by_referral_code(code: str) -> Optional[Dict]:
    """Находит пользователя по реферальному коду"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.referral_code == code).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "referral_code": user.referral_code
            }
        return None
    finally:
        db.close()