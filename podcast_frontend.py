import streamlit as st
import modal
import json
import os
import requests


def main():
    st.set_page_config(layout="wide")

    # Customized main title using Markdown to adjust the font size
    st.markdown(
        """
        <h1 style='text-align: center; 
                font-size: 36px; 
                font-weight: bold; 
                color: #E1E1E1; 
                padding: 20px 0; 
                box-shadow: 0 4px 10px rgba(255, 255, 255, 0.1);
                background: linear-gradient(135deg, rgba(45, 45, 45, 1) 0%, rgba(25, 25, 25, 1) 100%);
                border-radius: 10px;
                '>
        🎵 Rhythm Rewind: Music Podcast Digest 🎵
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # Add 2 lines of space after the main title
    st.write("\n\n")

    # Input section in the sidebar
    st.sidebar.header("Input RSS Feed for a music podcast")
    rss_link = st.sidebar.text_input("Feed link:")

    if rss_link:
        # Basic Format Check (using a simple method)
        if not rss_link.startswith("http"):
            st.sidebar.warning("Please provide a valid URL.")

    predefined_values = {
        "Coffee and Country Music": "podcast-1.json",
        "The Podcast That Rocked": "podcast-2.json",
        "This Day in Metal": "podcast-3.json",
    }
    selected_value = st.sidebar.selectbox(
        "Or select a predefined RSS feed:", list(predefined_values.keys())
    )

    # Mock function to simulate the API call
    def fetch_podcast_data(value):
        if value in predefined_values.keys():
            with open(predefined_values[value], "r") as file:
                return json.load(file)
        else:
            return process_podcast_info(value)

    if st.sidebar.button("Fetch"):
        with st.spinner("Fetching podcast data..."):
            # Call the mock API function
            data = fetch_podcast_data(rss_link or selected_value)

        st.write("\n\n")

        # Provide an instruction to the user to manually collapse the sidebar
        st.sidebar.write(
            "Data fetched! You can collapse this sidebar for a better view."
        )

        # Display section in the main window
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

        # Display the image in the middle column.
        with col3:
            st.image(
                data["podcast_details"]["episode_image"],
                caption=data["podcast_details"]["podcast_title"],
                # width=300,
                use_column_width=True,
            )

        # Display episode title as a hyperlink, its summary, and the episode image side by side
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(
                f'<span style="font-size:24px">**Episode Name:** <a href="{data["podcast_details"]["episode_link"]}" target="_blank">{data["podcast_details"]["episode_title"]}</a></span>',
                unsafe_allow_html=True,
            )

            # Hyperlink for episode title
            st.markdown(
                f"**<u>Summary:</u>** {data['podcast_summary']}", unsafe_allow_html=True
            )
        with col2:
            st.write("\n")
            st.markdown(f"**<u>Host:</u>** {data['host_name']}", unsafe_allow_html=True)

            # Only write Date Published if a value is available
            if data["date_published"]:
                st.markdown(
                    f"**<u>Date Published:</u>** {data['date_published']}",
                    unsafe_allow_html=True,
                )

            # Only write Guests if guests are available
            if data["guests"]:
                st.markdown(
                    f"**<u>Guests:</u>** {', '.join(data['guests'])}",
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"**<u> Podcast Tone:</u>** {data['tone']}", unsafe_allow_html=True
            )

        # Extract artists_discussed and artist_details from the data
        artists_discussed = data["artists_discussed"]
        artist_details = data["artist_details"]

        # Title for the section
        st.markdown(
            "<h3 style='text-align: center;'>Artists Discussed</h3>",
            unsafe_allow_html=True,
        )

        # Define a function to calculate a score for sorting artists
        def artist_sort_key(artist_name):
            songs = artists_discussed[artist_name]
            # Count only songs that are not "-"
            valid_songs = [song for song in songs if song != "-"]
            return len(valid_songs)

        # Sort artists based on the number of valid songs associated with them
        sorted_artists = sorted(
            artists_discussed.keys(), key=artist_sort_key, reverse=True
        )

        # Iterate through each artist based on the sorted order
        for artist in sorted_artists:
            songs = [song for song in artists_discussed[artist] if song != "-"]

            # Create a column layout for each artist card
            col1, col2 = st.columns([3, 1])

            # Display artist's name in the first column
            with col1:
                st.markdown(f"**<u>{artist}</u>**", unsafe_allow_html=True)
                for song in songs:
                    st.write(f"Song discussed - {song}")

            # Display the Spotify link in the second column (if available in the artist_details)
            if artist in artist_details:
                with col2:
                    st.write(
                        f"[![Spotify](https://img.shields.io/badge/Spotify-Listen-green?logo=spotify&style=for-the-badge)]({artist_details[artist]})",
                        unsafe_allow_html=True,
                    )

        st.markdown(
            "<h3 style='text-align: center;'>Highlights</h3>", unsafe_allow_html=True
        )

        # Check if highlights are available and are in a list format
        if data["highlights"] and isinstance(data["highlights"], list):
            for highlight in data["highlights"]:
                st.markdown(f"- {highlight}")
        else:
            st.write(data["highlights"])

        st.write("\n\n")
        # Use a cool heading with an AI emoji
        st.markdown(
            "<h3 style='text-align: center;'> 🤖 AI's Perspective</h3>",
            unsafe_allow_html=True,
        )

        # Display the commentary in a styled container with a semi-transparent background
        st.markdown(
            f"<div style='background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px;'>{data['commentary']}</div>",
            unsafe_allow_html=True,
        )


def process_podcast_info(rss_link):
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.call(rss_link, "/content/podcast/")
    return output


if __name__ == "__main__":
    main()
