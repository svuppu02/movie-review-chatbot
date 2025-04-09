import streamlit as st
from chatbot_main import (get_movie_review, autocomplete_movie_titles, answer_question_from_reviews, get_movie_trailer,
                          get_movie_streaming_links)

st.set_page_config(page_title="🎬 Movie Review Chatbot", layout="centered")
st.title("🎬 Movie Review Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []


if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# --- Movie Search ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🎬 Search a Movie")
    search_query = st.text_input("Type a movie name to get reviews:", key="movie_search")
    movie_options = autocomplete_movie_titles(search_query) if search_query else []
    selected = st.selectbox("Pick a movie from suggestions:", movie_options, key="movie_select") if movie_options else None

with col2:
    st.markdown("#### 💬 Ask a Question")
    user_question = st.text_input("What do you want to know?", key="user_question")


# --- On movie selection ---
if selected and selected != st.session_state.selected_movie:
    st.session_state.selected_movie = selected
    st.session_state.messages.append({"role": "user", "content": selected})

    with st.chat_message("user"):
        st.markdown(selected)

    with st.chat_message("assistant"):
        with st.spinner("Fetching reviews..."):
            review, movie, reviews, poster_url, rating, mood = get_movie_review(selected)
            st.session_state.reviews = reviews  # Save for question answering
            trailer_url = get_movie_trailer(movie['id'])

            if review == "No reviews found.":
                bot_reply = "No reviews found for that movie."
                st.markdown(bot_reply)
            else:
                bot_reply = f"**{movie['title']}**\n\n**Rating:** {rating}/10\n**Sentiment:** {mood}\n\n**Top Review:**\n{review}"
                st.markdown(bot_reply)

                if poster_url:
                    st.image(poster_url, width=300)

                if trailer_url:
                    st.markdown(f"▶️ [Watch Trailer]({trailer_url})", unsafe_allow_html=True)

                for i, rev in enumerate(reviews):
                    st.markdown(f"**Review {i + 1}:**")
                    st.write(rev["content"][:1000])
                    st.markdown("---")

            st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        # --- Auto Recommendations ---
        summary, recs = answer_question_from_reviews("What are similar movies?", reviews)


        if recs:
            st.markdown("### 🎥 You might also like")
            cols = st.columns(min(5, len(recs)))
            for col, rec in zip(cols, recs):
                with col:
                    title = rec.get("title", "Unknown")
                    poster_path = rec.get("poster_path")
                    poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                    link = f"https://www.themoviedb.org/movie/{rec['id']}"

                    if poster:
                        st.image(poster, use_container_width=True)
                    st.markdown(f"[**{title}**]({link})", unsafe_allow_html=True)

# Add button to fetch where to watch the movie
if selected:
    with st.expander("Where to Watch this Movie?"):
        with st.spinner("Fetching streaming platforms..."):
            streaming_links = get_movie_streaming_links(selected)

        if streaming_links:
            st.markdown("### Available on:")
            for platform in streaming_links:
                st.markdown(f"- **{platform['name']}**: [Link]({platform['url']})")
        else:
            st.markdown("No streaming information available for this movie.")

# --- Chat History ---


if st.session_state.messages:
    st.divider()
    st.markdown("### 💬 Conversation History")
    with st.expander("💬 Show Conversation History"):
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# --- Ask Questions about the Movie ---


if st.session_state.selected_movie and "reviews" in st.session_state:
    if user_question:
        with st.spinner("Thinking..."):
            answer, recs = answer_question_from_reviews(user_question, st.session_state.reviews)

        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            st.markdown(answer)

        if recs:
            st.markdown("### 🍿 You might also like")
            cols = st.columns(min(5, len(recs)))
            for col, rec in zip(cols, recs):
                with col:
                    title = rec.get("title", "Unknown")
                    poster_path = rec.get("poster_path")
                    poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                    link = f"https://www.themoviedb.org/movie/{rec['id']}"

                    if poster:
                        st.image(poster, use_container_width=True)
                    st.markdown(f"[**{title}**]({link})", unsafe_allow_html=True)
