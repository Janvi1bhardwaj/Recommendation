from flask import Flask, render_template, request
import pickle
import numpy as np
import requests

# Load book recommendation models
popular_df = pickle.load(open(r'C:\Users\as\OneDrive\Desktop\recommandation\notebook\popular.pkl', 'rb'))
pt = pickle.load(open(r'C:\Users\as\OneDrive\Desktop\recommandation\notebook\books_pt.pkl', 'rb'))
books = pickle.load(open(r'C:\Users\as\OneDrive\Desktop\recommandation\notebook\books.pkl', 'rb'))
similarity_scores = pickle.load(open(r'C:\Users\as\OneDrive\Desktop\recommandation\notebook\book_similarity_score.pkl', 'rb'))

# Load movie recommendation models - now a pandas DataFrame
movies = pickle.load(open(r'notebook\movie.pkl', 'rb'))
similarity = pickle.load(open(r'notebook\movie_similarity.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', 
                          book_name=list(popular_df['Book-Title'].values),
                          author=list(popular_df['Book-Author'].values),
                          image=list(popular_df['Image-URL-M'].values),
                          votes=list(popular_df['Num_Rating'].values),
                          rating=list(popular_df['Avg_Rating'].values))

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:10]
    
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        data.append(item)
    
    return render_template('recommend.html', data=data)

@app.route('/recommend_mov')
def recommend_ui_mov():
    return render_template('recommend_mov.html')

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

@app.route('/recommend_movies', methods=['post'])
def recommend_movies():
    movie_name = request.form.get('movie_name')  # Get movie name from form
    
    # Error handling if movie not found
    if movie_name not in movies['title'].values:
        return render_template('recommend_mov.html', error="Movie not found. Please try another movie.")
    
    # Find the index of the movie in the DataFrame
    index = movies[movies['title'] == movie_name].index[0]
    
    # Get similar movies
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:10]
    
    recommended_movie_names = []
    recommended_movie_posters = []
    
    for i in distances:
        # Access movie_id from the DataFrame
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]]['title'])
    
    data = zip(recommended_movie_names, recommended_movie_posters)
    return render_template('recommend_mov.html', data=list(data))

if __name__ == '__main__':
    app.run(debug=True)