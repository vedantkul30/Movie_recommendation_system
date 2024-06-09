import streamlit as st
import pickle
import pandas as pd
import requests

movies_list = pickle.load(open('movies_transformer.pkl','rb'))
movies = pd.DataFrame(movies_list)

if not isinstance(movies, pd.DataFrame):
    st.error("Error: 'movies' is not a DataFrame.")
    st.stop()

similarity_list = pickle.load(open('similarity_trans (1).pkl','rb'))
similarity = pd.DataFrame(similarity_list)

def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=7d5006c7c4e432cdc72be35a5118e4c4'.format(movie_id))
    data = response.json()
    poster_url =  "https://image.tmdb.org/t/p/w500/"+ data['poster_path']
    desc = data['overview']

    return poster_url,desc

def fetch_movie_details(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=7d5006c7c4e432cdc72be35a5118e4c4'.format(movie_id))
    data = response.json()
    
    poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    title = data['title']
    overview = data['overview']
    genres = [genre['name'] for genre in data['genres']]
    
    # Fetch cast details
    credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=7d5006c7c4e432cdc72be35a5118e4c4'
    credits_response = requests.get(credits_url)
    credits_data = credits_response.json()
    cast = [cast_member['name'] for cast_member in credits_data['cast'][:5]]  
    
    return poster_url, title, overview, genres, cast

def display_movie_details(movie_id):
    poster_url, title, overview, genres, cast = fetch_movie_details(movie_id)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.image(poster_url)
        
    with col2:
        st.markdown(f"**Name:** {title}")
        st.markdown("**Cast:**")
        for member in cast:
            st.markdown(f"- {member}")
        st.markdown(f"**Genre:** {', '.join(genres)}")
        st.markdown(f"**Overview:** {overview}")
    


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_desc = []
    for i in distances[0:11]:
        movie_id = movies.iloc[i[0]].tmdbId_x	
        poster_url,desc = fetch_poster(movie_id)
        recommended_movie_posters.append(poster_url)
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_desc.append(desc)

    return recommended_movie_names,recommended_movie_posters,recommended_movie_desc

st.title('Movie Recomendation System')

selected_movie = st.selectbox('Select Movie',movies['title'].values)

if st.button('Recommend'):
    name,poster,desc = recommend(selected_movie)
    
    index = movies[movies['title'] == selected_movie].index[0]
    movie_id= movies.iloc[index].tmdbId_x
    display_movie_details(movie_id)
    st.subheader('Recommended Movies')
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(name[i+1])
            st.image(poster[i+1])
            st.text_area("Description", desc[i+1], height=100,disabled=True)
    
    cols = st.columns(5)
    for i in range(5, 10):
        with cols[i-5]:
            st.text(name[i+1])
            st.image(poster[i+1])
            st.text_area("Description", desc[i+1], height=100,disabled=True)
