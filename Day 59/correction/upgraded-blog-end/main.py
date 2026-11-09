from flask import Flask, render_template, abort
import requests

app = Flask(__name__)

# URL de ton API npoint
API_URL = "https://npoint.io"


@app.route('/')
def get_all_posts():
    try:
        # Récupération dynamique des données de l'API
        posts = requests.get(API_URL).json()
    except requests.RequestException:
        posts = []

    return render_template("index.html", all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/post/<int:index>")
def show_post(index):
    try:
        posts = requests.get(API_URL).json()
    except requests.RequestException:
        return abort(503, description="L'API de données est indisponible.")

    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
            break

    if requested_post is None:
        return abort(404, description="Article non trouvé.")

    return render_template("post.html", post=requested_post)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
