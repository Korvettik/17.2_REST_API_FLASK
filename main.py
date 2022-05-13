
from flask import Flask
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
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))



# описываем классы-схемы marshmallow для обработки  (прегонки в JSON) результатов SQLAlchemy - объектов
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

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
@movies_ns.route('/')   # --- пока не ясно как сделать "паддинг"
class MovieView(Resource):
    def get(self):
        all_movies = db.session.query(Movie).all()
        return movies_schema.dump(all_movies), 200


@movies_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        movie = Movie.query.get(id)
        if not movie:
            return f"movie id={id} не найдено", 404
        movie = db.session.query(Movie).filter(Movie.id==id).one()
        return movie_schema.dump(movie), 200


@movies_ns.route('/<int:director_id>')
class MovieView(Resource):
    def get(self, director_id):
        pass

@movies_ns.route('/<int:genre_id>')
class MovieView(Resource):
    def get(self, genre_id):
        pass








# ===========================*====================================
@movies_ns.route('/<int:director_id>,<int:genre_id>')
class MovieView(Resource):
    def get(self, genre_id):
        pass


@director_ns.route('/<int:id>')
class DirectorSchema(Resource):
    def post(self, id):
        pass
    def put(self, id):
        pass
    def delete(self, id):
        pass


@genre_ns.route('/<int:id>')
class GenreSchema(Resource):
    def post(self, id):
        pass
    def put(self, id):
        pass
    def delete(self, id):
        pass

# ===========================*====================================


if __name__ == '__main__':
    app.run(debug=True)