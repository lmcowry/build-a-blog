import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

# a list of movies that nobody should be allowed to watch
terrible_movies = [
    "Gigli",
    "Star Wars Episode 1: Attack of the Clones",
    "Paul Blart: Mall Cop 2",
    "Nine Lives"
]


class Movie(db.Model):
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    watched = db.BooleanProperty(required = True, default = False)
    rating = db.StringProperty()


def getUnwatchedMovies():
    """ Returns the list of movies the user wants to watch (but hasnt yet) """

    return [ "Star Wars", "Minions", "Freaky Friday", "My Favorite Martian" ]


def getWatchedMovies():
    """ Returns the list of movies the user has already watched """

    return [ "The Matrix", "The Big Green", "Ping Ping Playa" ]


class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


class Index(Handler):
    """ Handles requests coming in to '/' (the root of our site)
        e.g. www.flicklist.com/
    """

    def get(self):
        unwatched_movies = db.GqlQuery("SELECT * FROM Movie where watched = False")
        t = jinja_env.get_template("frontpage.html")
        content = t.render(
                        movies = unwatched_movies,
                        error = self.request.get("error"))
        self.response.write(content)

class AddMovie(Handler):
    """ Handles requests coming in to '/add'
        e.g. www.flicklist.com/add
    """

    def post(self):
        new_movie_title = self.request.get("new-movie")

        # if the user typed nothing at all, redirect and yell at them
        if (not new_movie_title) or (new_movie_title.strip() == ""):
            error = "Please specify the movie you want to add."
            self.redirect("/?error=" + cgi.escape(error))

        # if the user wants to add a terrible movie, redirect and yell at them
        if new_movie_title in terrible_movies:
            error = "Trust me, you don't want to add '{0}' to your Watchlist.".format(new_movie_title)
            self.redirect("/?error=" + cgi.escape(error, quote=True))

        # 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
        new_movie_title_escaped = cgi.escape(new_movie_title, quote=True)

        # construct a movie object for the new movie
        movie = Movie(title = new_movie_title_escaped)
        movie.put()

        # render the confirmation message
        t = jinja_env.get_template("add-confirmation.html")
        content = t.render(movie = movie)
        self.response.write(content)

class DeleteMovie(Handler):

    def post(self):

        delete_movie_id = self.request.get("delete-this-movie")

        delete_movie = Movie.get_by_id( int(delete_movie_id) )
        if not delete_movie == None:
            delete_movie.delete()


        self.redirect("/")


class WatchedMovie(Handler):
    """ Handles requests coming in to '/watched-it'
        e.g. www.flicklist.com/watched-it
    """

    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


    def post(self):
        watched_movie_id = self.request.get("watched-movie")

        watched_movie = Movie.get_by_id( int(watched_movie_id) )

        # if we can't find the movie, reject.
        if not watched_movie:
            self.renderError(400)
            return

        # update the movie's ".watched" property to True
        watched_movie.watched = True
        watched_movie.put()

        # render confirmation page
        t = jinja_env.get_template("watched-it-confirmation.html")
        content = t.render(movie = watched_movie)
        self.response.write(content)


class MovieRatings(Handler):

    def get(self):
        # TODO 1
        # Make a GQL query for all the movies that have been watched
        # watched_movies = db.GqlQuery("SELECT * FROM Movie where watched = True") # type something else instead of an empty list
        watched_movies = db.GqlQuery("SELECT * FROM Movie where watched = True ORDER BY created DESC")
        # TODO (extra credit)
        # in the query above, add something so that the movies are sorted by creation date, most recent first

        t = jinja_env.get_template("ratings.html")
        content = t.render(movies = watched_movies)
        self.response.write(content)

    def post(self):
        rating = self.request.get("rating")
        movie_id = self.request.get("movie")

        # TODO 2
        # retreive the movie entity whose id is movie_id
        movie = Movie.get_by_id( int(movie_id) ) # type something else instead of None

        if movie and rating:
            # TODO 3
            # update the movie's rating property and save it to the database
            movie.rating = rating
            movie.put()


            # render confirmation
            t = jinja_env.get_template("rating-confirmation.html")
            content = t.render(movie = movie)
            self.response.write(content)
        else:
            self.renderError(400)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/add', AddMovie),
    ('/watched-it', WatchedMovie),
    ('/deleteit', DeleteMovie),
    ('/ratings', MovieRatings)
], debug=True)
