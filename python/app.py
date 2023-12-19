import requests
from sqlalchemy import create_engine, Column, Integer, String, Date, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from Logging import setup_logger
from Config import user, password, host, db_name

Base = declarative_base()


# Определение модели для таблицы фильмов (Movies table model definition)
class Movie(Base):
    __tablename__ = "movies_table"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    release_date = Column(Date)
    overview = Column(Text)


# TMDb API key
tmdb_api_key = "417859de0f351192d3be63fffabf790e"

# Database connection setup
engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{db_name}", echo=False
)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Настройка логгера (Logger setup)
logger = setup_logger()

try:
    # Запрос к API TMDb для получения списка популярных фильмов (Request to TMDb API for popular movies)
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={tmdb_api_key}&sort_by=popularity.desc"
    response = requests.get(url)

    # Проверка кода ответа (Checking response status code)
    if response.status_code == 200:
        movies_data = response.json().get("results", [])

        # Итерация по полученным фильмам (Iteration through retrieved movies)
        for movie_data in movies_data:
            title = movie_data.get("title")  
            release_date_str = movie_data.get("release_date")

            # Проверяем, что дата выпуска присутствует
            if release_date_str:
                release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
            else:
                release_date = None

            overview = movie_data.get("overview")

            # Проверяем, существуют ли данные с таким же заголовком в базе данных
            # Checking if data with the same title already exists in the database
            existing_data = session.query(Movie).filter(Movie.title == title).first()

            if not existing_data:
                # Если данные не существуют, добавляем новый фильм в базу данных
                # If data doesn't exist, add a new movie to the database
                new_movie = Movie(
                    title=title,
                    release_date=release_date,
                    overview=overview,
                )
                session.add(new_movie)

        # Сохраняем изменения в базе данных (Committing changes to the database)
        session.commit()
        logger.info("Data inserted successfully")

except Exception as ex:
    # Обработка ошибок и запись ошибок в лог (Error handling and logging)
    logger.error("Error during processing")
    logger.error(ex)

finally:
    # Закрываем сессию базы данных (Closing the database session)
    session.close()
