import streamlit as st
import pickle
import requests
import pandas as pd

# Set page config for a modern look
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎥",
    layout="centered",
    initial_sidebar_state="expanded"
)

## Custom CSS and JavaScript for animations and 3D effects
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #fff;
        font-family: 'Segoe UI', sans-serif;
        overflow-x: hidden;
    }
    .stSelectbox > div {
        background: #222;
        color: #fff;
        border-radius: 8px;
        transition: box-shadow 0.3s;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    .stSelectbox > div:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .stButton > button {
        background: #ff4b2b;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5em 2em;
        font-size: 1.1em;
        transition: background 0.3s, transform 0.2s;
    }
    .stButton > button:hover {
        background: #ff416c;
        transform: scale(1.05);
    }
    .movie-card {
        background: #333;
        border-radius: 12px;
        padding: 1.5em;
        margin: 1em 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        transition: transform 0.3s, box-shadow 0.3s;
        text-align: center; /* Center align content */
    }
    .movie-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 6px 30px rgba(0,0,0,0.5);
    }
    .movie-card img {
        margin: 10px auto; /* Center the image */
        display: block;
        border-radius: 8px;
        transition: transform 0.3s ease-in-out;
    }
    .movie-card img:hover {
        transform: scale(1.1); /* Slight zoom effect on hover */
    }
    canvas {
        position: absolute;
        top: 0;
        left: 0;
        z-index: -1;
    }
    </style>
    <script>
    // WebGL background animation
    document.addEventListener('DOMContentLoaded', function() {
        const canvas = document.createElement('canvas');
        document.body.appendChild(canvas);
        const gl = canvas.getContext('webgl');
        if (!gl) return;

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const vertexShaderSource = `
            attribute vec4 a_position;
            void main() {
                gl_Position = a_position;
            }
        `;
        const fragmentShaderSource = `
            precision mediump float;
            void main() {
                gl_FragColor = vec4(0.1, 0.2, 0.5, 1.0);
            }
        `;

        const vertexShader = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vertexShader, vertexShaderSource);
        gl.compileShader(vertexShader);

        const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fragmentShader, fragmentShaderSource);
        gl.compileShader(fragmentShader);

        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        gl.useProgram(program);

        const positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
            -1, -1,
             1, -1,
            -1,  1,
             1,  1,
        ]), gl.STATIC_DRAW);

        const positionLocation = gl.getAttribLocation(program, "a_position");
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

        function render() {
            gl.clearColor(0.0, 0.0, 0.0, 1.0);
            gl.clear(gl.COLOR_BUFFER_BIT);
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            requestAnimationFrame(render);
        }
        render();
    });
    </script>
""", unsafe_allow_html=True)

# Load the movies data
def fetch_poster(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US")
    data = response.json()
    return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"

def fetch_movie_details(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US")
    data = response.json()
    return {
        "poster": f"https://image.tmdb.org/t/p/w500{data['poster_path']}",
        "description": data.get("overview", "No description available."),
        "rating": data.get("vote_average", "N/A"),
        "trailer": fetch_trailer(movie_id)
    }

def fetch_trailer(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US")
    data = response.json()
    for video in data.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

def recommend(movie):
    index = moviess[moviess['title'] == movie].index[0]
    distances = similarity[index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_list= []
    movies_posters = []
    for i in movies_list:
        movies_id = moviess.iloc[i[0]].id

        #fetch the movie title using the index and poster
        recommended_list.append(moviess.iloc[i[0]].title)
        movies_posters.append(fetch_poster(movies_id))
    return recommended_list, movies_posters

movies = pickle.load(open("movies.pkl", "rb"))
moviess = pd.DataFrame(movies)
similarity = pickle.load(open("similarity.pkl", "rb"))

st.title('🎥 Movie Recommender System')
st.write("Find your next favorite movie with ease! Select a movie below:")

selected_movie = st.selectbox('Select a movie', moviess['title'].values)
if st.button('Recommend'):
    recommended_movies, posters = recommend(selected_movie)
    st.markdown(f"### Recommended movies for **{selected_movie}**:")
    for i in range(len(recommended_movies)):
        movie_id = moviess[moviess['title'] == recommended_movies[i]].iloc[0].id
        details = fetch_movie_details(movie_id)
        st.markdown(
            f"""
            <div class="movie-card">
                <strong>{recommended_movies[i]}</strong><br>
                <img src="{details['poster']}" width="150"><br>
                <p><strong>Rating:</strong> {details['rating']}</p>
                <p>{details['description']}</p>
                {f'<a href="{details['trailer']}" target="_blank">🎥 Watch Trailer</a>' if details['trailer'] else ''}
            </div>
            """, unsafe_allow_html=True
        )
