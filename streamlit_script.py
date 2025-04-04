import streamlit as st
from chatbot_main import get_movie_review, autocomplete_movie_titles, answer_question_from_reviews

st.set_page_config(page_title="🎬 Movie Review Chatbot", layout="centered")
st.title("🎬 Movie Review Chatbot")

# Session state for chat and selected movie
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# Text input for search
search_query = st.text_input("Type a movie name to get suggestions:")

# Show autocomplete dropdown
movie_options = autocomplete_movie_titles(search_query) if search_query else []
selected = st.selectbox("Pick a movie from suggestions:", movie_options) if movie_options else None

# On selection, run the chatbot
if selected and selected != st.session_state.selected_movie:
    st.session_state.selected_movie = selected

    # Save user message
    st.session_state.messages.append({"role": "user", "content": selected})

    with st.chat_message("user"):
        st.markdown(selected)

    with st.chat_message("assistant"):
        with st.spinner("Fetching reviews..."):
            review, movie, reviews, poster_url, rating, mood = get_movie_review(selected)

            st.session_state.reviews = reviews

            if review == "No reviews found.":
                bot_reply = "No reviews found for that movie."
            else:
                bot_reply = f"**{movie['title']}**\n\n**Rating:** {rating}/10\n**Sentiment:** {mood}\n\n**Top Review:**\n{review}"

                if poster_url:
                    st.image(poster_url, width=300)

                for i, rev in enumerate(reviews):
                    st.markdown(f"**Review {i + 1}:**")
                    st.write(rev["content"][:1000])
                    st.markdown("---")

        st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# Display past messages
st.divider()
st.markdown("### 💬 Conversation History")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# After displaying reviews
st.markdown("## 💬 Ask a question about this movie")
user_question = st.text_input("What do you want to know?")

if user_question and "reviews" in st.session_state and st.session_state.reviews:
    with st.spinner("Thinking..."):
        response = answer_question_from_reviews(user_question, st.session_state.reviews)

    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        st.markdown(response)


