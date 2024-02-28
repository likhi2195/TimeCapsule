import streamlit as st
from datetime import datetime
import json
import os

# Initialize session state
if 'users' not in st.session_state:
    st.session_state.users = {}

def load_users():
    try:
        with open("user_data.json", "r") as file:
            st.session_state.users = json.load(file)
    except FileNotFoundError:
        st.session_state.users = {}

def save_users():
    with open("user_data.json", "w") as file:
        json.dump(st.session_state.users, file)

def authenticate(username, password):
    return st.session_state.users.get(username, {}).get("password") == password

def save_entry(username, entry, media_file):
    current_time = datetime.now().strftime('%Y-%m-%d %H_%M_%S')  # Replace colons with underscores
    if username not in st.session_state.users:
        st.session_state.users[username] = {"password": None, "time_capsule_entries": []}
    entry_data = {"time": current_time, "entry": entry, "media_file": None}

    # Save media file
    if media_file:
        media_folder = os.path.join("media", username)
        os.makedirs(media_folder, exist_ok=True)
        media_filename = os.path.join(media_folder, f'media_{current_time}_{media_file.name}')
        entry_data["media_file"] = media_filename

        with open(media_filename, 'wb') as media_file_output:
            media_file_output.write(media_file.read())

    st.session_state.users[username]["time_capsule_entries"].append(entry_data)
    save_users()
    st.success("Entry saved successfully!")

def delete_entry(username, entry_time):
    if username in st.session_state.users and "time_capsule_entries" in st.session_state.users[username]:
        entries = st.session_state.users[username]["time_capsule_entries"]
        st.session_state.users[username]["time_capsule_entries"] = [entry for entry in entries if entry["time"] != entry_time]
        save_users()
        st.success("Entry deleted successfully!")

def edit_entry(username, entry_time, new_content):
    if username in st.session_state.users and "time_capsule_entries" in st.session_state.users[username]:
        for entry in st.session_state.users[username]["time_capsule_entries"]:
            if entry["time"] == entry_time:
                entry["entry"] = new_content
                save_users()
                st.success("Entry edited successfully!")
                break
def display_entries(username):
    st.subheader(f"Time Capsule Entries for {username}")
    entries = st.session_state.users.get(username, {}).get("time_capsule_entries", [])
    if entries:
        for entry in entries:
            st.markdown(f"**{entry['time']}**: {entry['entry']}")
            if entry.get("media_file"):
                st.image(entry["media_file"], caption=f"Media ({entry['time']})", use_column_width=True)

            # Delete and Edit options as buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                delete_button = st.button(f"Delete {entry['time']}")
            with col3:
                edit_content = st.text_input(f"Edit {entry['time']}", entry['entry'])
                edit_button = st.button(f"Edit {entry['time']}")

            if delete_button:
                delete_entry(username, entry["time"])

            if edit_button:
                edit_entry(username, entry["time"], edit_content)
    else:
        st.info("No entries yet. Start writing!")

def main():
    st.title("Time Capsule App")

    load_users()

    # Register section
    st.subheader("Register")
    new_username = st.text_input("Choose a username:")
    new_password = st.text_input("Choose a password:", type="password")
    register_button = st.button("Register")

    if register_button and new_username and new_password:
        if new_username not in st.session_state.users:
            st.session_state.users[new_username] = {"password": new_password, "time_capsule_entries": []}
            save_users()
            st.success("Registration successful! You can now log in.")
        else:
            st.warning("Username already taken. Choose a different username.")

    # Login section
    st.subheader("Login")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    login_button = st.button("Login")

    if login_button:
        if authenticate(username, password):
            st.success(f"Welcome, {username}!")
            st.session_state.current_user = username
        else:
            st.error("Invalid username or password. Please try again.")

    # Only show the rest of the app if the user is logged in
    if 'current_user' in st.session_state:
        # Text area for user input
        user_input = st.text_area("Write your time capsule entry for today:")

        # File uploader for media
        media_file = st.file_uploader("Upload media file (optional)", type=["jpg", "jpeg", "png", "gif", "mp4"])

        # Save button
        if st.button("Save Entry"):
            save_entry(st.session_state.current_user, user_input, media_file)

        # Display entries
        display_entries(st.session_state.current_user)

if __name__ == "__main__":
    main()
