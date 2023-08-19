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
    st.sidebar.header("Get your JAM on! 🎧")

    # Image URL
    image_url = "data:image/jpeg;base64,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"  # Replace with your image URL

    # Display the image in the sidebar
    st.sidebar.image(image_url, use_column_width=True)

    # Spacer
    st.sidebar.write("\n\n")
    st.sidebar.write("\n\n")

    rss_link = st.sidebar.text_input("Provide a RSS Feed 📡 for a music podcast:")

    if rss_link:
        # Basic Format Check (using a simple method)
        if not rss_link.startswith("http"):
            st.sidebar.warning("Please provide a valid URL.")

    predefined_values = {
        "The Podcast That Rocked": "podcast-2.json",
        "Coffee and Country Music": "podcast-1.json",
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

    button_clicked = st.sidebar.button("Let's go!!!!!")

    if not rss_link and not button_clicked:
        st.markdown(
            f'<span style="font-size:24px">**👈 Please use the sidebar to interact with the app!**</span>',
            unsafe_allow_html=True,
        )

    # If the button hasn't been clicked, display the note
    if not button_clicked:
        st.sidebar.markdown(
            """
        🎵 *Give me 5, and you'll see,*  
        *The answer's worth the wait, you'll agree!* 🎶  
        """
        )

    if button_clicked:
        with st.spinner("Working our magic..."):
            # Call the mock API function
            data = fetch_podcast_data(rss_link or selected_value)

        st.write("\n\n")

        # Provide an instruction to the user to manually collapse the sidebar
        st.sidebar.write("Want a better view? Collapse me")

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
