import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz

# CSV file to store user data and calendar events
USER_CSV_FILE = "users_data.csv"
CALENDAR_CSV_FILE = "calendar_events.csv"

# Initialize CSV if it doesn't exist
def init_csv(file_name, columns):
    try:
        pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_name, index=False)

# Save new user data to CSV
def save_to_csv(new_data, file_name):
    df = pd.DataFrame([new_data])
    df.to_csv(file_name, mode="a", index=False, header=False)
    st.success("Data saved successfully!")

# Load existing data from CSV
def load_data(file_name):
    return pd.read_csv(file_name)

# Delete a specific row from CSV
def delete_entry(row_idx, file_name):
    df = pd.read_csv(file_name)
    df.drop(row_idx, inplace=True)
    df.to_csv(file_name, index=False)
    st.success("Entry deleted!")

# User registration form
def user_registration():
    st.header("User Registration")
    name = st.text_input("Enter your name")
    email = st.text_input("Enter your email")
    location = st.text_input("Enter your location")
    timezone = st.selectbox("Select your time zone", pytz.all_timezones)
    free_time = st.slider("Select your free time (can stretch to next day)", 0, 48, (8, 18))

    # Adjust time if it stretches to the next day
    if free_time[1] > 24:
        free_time_str = f"{free_time[0]:02d}:00 - {free_time[1]-24:02d}:00 (next day)"
    else:
        free_time_str = f"{free_time[0]:02d}:00 - {free_time[1]:02d}:00"
    
    if st.button("Submit"):
        new_data = {'Name': name, 'Email': email, 'Location': location, 'Time Zone': timezone, 
                    'Free Time': free_time_str}
        save_to_csv(new_data, USER_CSV_FILE)

# Convert times to UTC for comparison
def convert_to_utc(free_time, timezone):
    start, end = [int(t.split(":")[0]) for t in free_time.split(" - ")[0].split(":")]
    tz = pytz.timezone(timezone)
    utc_start = tz.localize(datetime.now().replace(hour=start, minute=0)).astimezone(pytz.utc)
    utc_end = tz.localize(datetime.now().replace(hour=end, minute=0)).astimezone(pytz.utc)
    return utc_start.hour, utc_end.hour

# Find common available hours across all users and convert back to their time zones
def find_common_hours(users_df):
    utc_ranges = []
    for _, row in users_df.iterrows():
        start_utc, end_utc = convert_to_utc(row['Free Time'], row['Time Zone'])
        utc_ranges.append((start_utc, end_utc))

    min_start = max([start for start, _ in utc_ranges])
    max_end = min([end for _, end in utc_ranges])

    if min_start < max_end:
        common_utc_time = f"{min_start}:00 - {max_end}:00 UTC"
        return common_utc_time
    else:
        return "No common available time found"

# Calendar management
def manage_calendar():
    st.header("Calendar Events")
    event_name = st.text_input("Event name")
    event_date = st.date_input("Event date")
    event_time = st.time_input("Event time")

    if st.button("Add Event"):
        event_data = {"Event": event_name, "Date": event_date, "Time": event_time}
        save_to_csv(event_data, CALENDAR_CSV_FILE)

    st.subheader("Your Events")
    events_df = load_data(CALENDAR_CSV_FILE)
    st.dataframe(events_df)

    # Delete event
    if not events_df.empty:
        event_to_delete = st.selectbox("Select an event to delete", events_df.index)
        if st.button("Delete Event"):
            delete_entry(event_to_delete, CALENDAR_CSV_FILE)

# Task page functionality
def task_page():
    st.title("Manage Your Tasks")
    st.write("This page will be for managing personal tasks (feature coming soon).")

# Main app with page switching
def main():
    # Initialize CSVs
    init_csv(USER_CSV_FILE, ["Name", "Email", "Location", "Time Zone", "Free Time"])
    init_csv(CALENDAR_CSV_FILE, ["Event", "Date", "Time"])

    # Page selection
    page = st.sidebar.selectbox("Select a page", ["User Registration", "Calendar", "Tasks"])

    if page == "User Registration":
        user_registration()

        # Load and display user data
        users_df = load_data(USER_CSV_FILE)
        if not users_df.empty:
            st.subheader("Registered Users")
            st.dataframe(users_df)

            # Find common hours
            if st.button("Find Common Available Hours"):
                common_time = find_common_hours(users_df)
                st.write(common_time)
            
            # Delete user entry
            if not users_df.empty:
                user_to_delete = st.selectbox("Select a user to delete", users_df.index)
                if st.button("Delete User"):
                    delete_entry(user_to_delete, USER_CSV_FILE)

    elif page == "Calendar":
        manage_calendar()

    elif page == "Tasks":
        task_page()

if __name__ == "__main__":
    main()
