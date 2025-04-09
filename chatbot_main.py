import requests
from textblob import TextBlob
import openai
import requests
import os

TMDB_API_KEY = "YOUR_TMDB_API_KEY"
openai.api_key = "YOUR_OPENAI_API"



def search_movie(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(url)
    results = response.json().get("results", [])
    return results[0] if results else None


def get_movie_reviews(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json().get("results", [])

def get_movie_review(title):
    movie = search_movie(title)
    if not movie:
        # Return 6 items, but show a clean "no reviews" message
        return "No reviews found.", None, [], None, None, None

    reviews = get_movie_reviews(movie["id"])
    if not reviews:
        # Movie was found but no reviews — still return everything needed
        poster_path = movie.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        rating = movie.get("vote_average")
        return "No reviews found.", movie, [], poster_url, rating, None

    # Poster and rating
    poster_path = movie.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    rating = movie.get("vote_average")

    # Sentiment analysis
    top_review = reviews[0]
    sentiment = TextBlob(top_review["content"]).sentiment.polarity
    mood = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"

    return top_review["content"][:1000] + "...", movie, reviews[:3], poster_url, rating, mood



def autocomplete_movie_titles(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    data = response.json()
    suggestions = [movie["title"] for movie in data.get("results", [])][:5]
    return suggestions


def answer_question_from_reviews(question, reviews):
    context = "\n\n".join([r["content"][:1000] for r in reviews[:5]])

    # 1. Answer the question
    answer_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You answer questions based on movie reviews."},
            {"role": "user", "content": f"Based on the following reviews:\n\n{context}\n\nAnswer this: {question}"}
        ]
    )
    answer = answer_response.choices[0].message.content

    # 2. Get recommendations
    recommend_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You suggest movies based on user interest. Output only a list of 3-5 movie titles."},
            {"role": "user", "content": f"Based on the query '{question}', recommend similar movies."}
        ]
    )
    titles = recommend_response.choices[0].message.content.strip().split("\n")
    titles = [title.strip("-• ").strip() for title in titles if title.strip()]

    recommendations = []
    for title in titles:
        result = search_movie(title)
        if result:
            recommendations.append(result)

    return answer, recommendations
def get_movie_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    response = requests.get(url, params=params)
    data = response.json()

    for video in data.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None


def get_movie_streaming_links(movie_title):
    try:
        # Step 1: Get Movie ID using search API
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}&language=en-US"
        search_response = requests.get(search_url).json()

        if search_response['results']:
            movie_id = search_response['results'][0]['id']
        else:
            return []  # No results found

        # Step 2: Get Streaming Providers using the movie ID
        watch_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}"
        watch_response = requests.get(watch_url).json()

        if 'results' in watch_response:
            # Get US providers (you can change the region as needed)
            providers = watch_response['results'].get('US', {}).get('flatrate', [])

            streaming_links = []
            for provider in providers:
                name = provider.get('provider_name')
                link = f"https://www.themoviedb.org/network/{provider['provider_id']}"  # Link to provider page
                streaming_links.append({
                    'name': name,
                    'url': link
                })

            return streaming_links

        else:
            return []  # No streaming info available

    except Exception as e:
        print(f"Error: {e}")
        return []