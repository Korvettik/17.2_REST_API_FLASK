from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


# описываем классы-модели для работы с SQL бд (SQLAlchemy)
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    director_name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(255))


# описываем классы-схемы marshmallow для обработки  (прегонки в JSON) результатов SQLAlchemy - объектов
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    # genre_id = fields.Int()
    # director_id = fields.Int()
    genre_name = fields.Str()
    director_name = fields.Str()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


# готовим сериализацию для запросов
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()  # *
genre_schema = GenreSchema()  # *

# создаем объект приложения Flask(app)
api = Api(app)
movies_ns = api.namespace('movies')
director_ns = api.namespace('director')  # *
genre_ns = api.namespace('genre')  # *


# прописываем эндпоинты
@movies_ns.route('/')
class MovieView(Resource):
    def get(self):
        genre_id = request.args.get('genre_id')
        director_id = request.args.get('director_id')

        if genre_id and genre_id != '' and director_id and director_id != '':   # Доработайте представление так, чтобы оно возвращало только фильмы с определенным режиссером и жанром по запросу типа /movies/?director_id=2&genre_id=4.
            director_id = request.args.get('director_id')
            movies = db.session.query(Movie.title).filter(Movie.director_id == director_id and Movie.genre_id == genre_id).all()
            if not movies:
                return f"movie director_id={director_id} and genre_id={genre_id} not found", 404
            return movies_schema.dump(movies), 200

        if genre_id and genre_id != '':   # Доработайте представление так, чтобы оно возвращало только фильмы определенного жанра  по запросу типа /movies/?genre_id=1.
            movies = db.session.query(Movie.title).filter(Movie.genre_id == genre_id).order_by(Movie.year).all()
            if not movies:
                return f"movie genre_id={genre_id} not found", 404
            return movies_schema.dump(movies), 200

        if director_id and director_id != '':   # Доработайте представление так, чтобы оно возвращало только фильмы с определенным режиссером по запросу типа `/movies/?director_id=1`.
            director_id = request.args.get('director_id')
            movies = db.session.query(Movie.title).filter(Movie.director_id == director_id).order_by(Movie.year).all()
            if not movies:
                return f"movie director_id={director_id} not found", 404
            return movies_schema.dump(movies), 200



        else:   # /movies — возвращает список всех фильмов,
            all_movies = db.session.query(Movie.title).all()
            return movies_schema.dump(all_movies), 200





@movies_ns.route('/<int:id>')   # /movies/<id> — возвращает подробную информацию о фильме.
class MovieView(Resource):
    def get(self, id):
        movie = Movie.query.get(id)
        if not movie:
            return f"movie id={id} не найдено", 404
        # movie = db.session.query(Movie).filter(Movie.id == id).one()
        # return movie_schema.dump(movie), 200

        select = db.session.query(Movie.id, Movie.title, Movie.description, Movie.trailer, Movie.year, Movie.rating, Genre.genre_name, Director.director_name)
        # select = db.session.query(Movie.id, Movie.title, Movie.description, Movie.trailer, Movie.year, Movie.rating, Genre.name.label('genre_name'), Director.name.label('director_name'))
        join1 = select.join(Genre, Movie.genre_id == Genre.id)
        join2 = join1.join(Director, Movie.director_id == Director.id)
        where = join2.filter(Movie.id == id).one()
        return movie_schema.dump(where), 200



# ===========================*====================================


@director_ns.route('/<int:id>')   #  Добавьте реализацию методов POST/PUT/DELETE для режиссера.
class DirectorSchema(Resource):
    def post(self):  # добавление
        data = request.json()
        new_director = Director(**data)
        with db.session.begin():
            db.session.add(new_director)
        return "", 201

    def put(self, id):  # замена
        data = request.json()
        director = Director.query.get(id)
        director.director_name = data['director_name']
        with db.session.begin():
            db.session.add(director)
        return "", 204

    def delete(self, id:int):  # удаление
        director = db.session.query(Director).get(id)
        with db.session.begin():
            db.session.delete(director)
        return "", 204


@genre_ns.route('/<int:id>')   #  Добавьте реализацию методов POST/PUT/DELETE для жанра.
class GenreSchema(Resource):
    def post(self):   # добавление
        data = request.json()
        new_genre = Genre(**data)
        with db.session.begin():
            db.session.add(new_genre)
        return "", 201

    def put(self, id):   # замена
        data = request.json()
        genre = Genre.query.get(id)
        genre.genre_name = data['genre_name']
        with db.session.begin():
            db.session.add(genre)
        return "", 204

    def delete(self, id:int):   # удаление
        genre = db.session.query(Genre).get(id)
        with db.session.begin():
            db.session.delete(genre)
        return "", 204


# ===========================*====================================


if __name__ == '__main__':
    app.run(debug=True)
