import streamlit as st
import pandas as pd
import statistics
from datetime import date, timedelta

st.set_page_config(
    page_title="LifePattern AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- SESSION DATA ----------------

if "health_data" not in st.session_state:
    st.session_state.health_data = pd.DataFrame(
        columns=[
            "Date", "Sleep", "Steps",
            "Water", "Exercise", "Mood"
        ]
    )

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# ---------------- TITLE ----------------

st.title("🧠 LifePattern AI")
st.subheader("Personal Health Intelligence & Habit Discovery")

st.write(
    "Understand your habits, discover patterns "
    "and receive personalized lifestyle suggestions."
)

st.info(
    "Your personal health companion focuses on "
    "understanding habits, not just tracking numbers."
)

# ---------------- SIDEBAR ----------------

st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Choose a section",
    [
        "Daily Health Entry",
        "Health Dashboard",
        "Habit Intelligence",
        "Weekly Insights",
        "Recommendation Feedback"
    ]
)

# ---------------- SAMPLE DATA ----------------

def load_sample_data():
    today = date.today()

    sample = []

    values = [
        (6, 2500, 1.2, 10, 2),
        (7, 4500, 1.8, 25, 3),
        (5, 2000, 1.0, 10, 2),
        (8, 7500, 2.5, 40, 4),
        (7, 6500, 2.2, 35, 4),
        (8, 8500, 2.8, 45, 5),
        (7, 7000, 2.5, 30, 4)
    ]

    for i, value in enumerate(values):
        sample.append({
            "Date": today - timedelta(days=6-i),
            "Sleep": value[0],
            "Steps": value[1],
            "Water": value[2],
            "Exercise": value[3],
            "Mood": value[4]
        })

    st.session_state.health_data = pd.DataFrame(sample)
    st.session_state.feedback = {}

# ---------------- DAILY ENTRY ----------------

if page == "Daily Health Entry":

    st.header("📝 Record Your Daily Habits")

    st.write("Enter your daily health information.")

    selected_date = st.date_input(
        "Date",
        value=date.today()
    )

    sleep = st.slider(
        "Sleep duration (hours)",
        0.0, 12.0, 7.0, 0.5
    )

    steps = st.number_input(
        "Steps walked",
        min_value=0,
        max_value=100000,
        value=5000
    )

    water = st.slider(
        "Water intake (litres)",
        0.0, 6.0, 2.0, 0.5
    )

    exercise = st.slider(
        "Exercise duration (minutes)",
        0, 180, 30
    )

    mood = st.select_slider(
        "How was your mood?",
        options=[1, 2, 3, 4, 5],
        value=3
    )

    if st.button("Save Daily Record"):

        new_record = {
            "Date": selected_date,
            "Sleep": sleep,
            "Steps": steps,
            "Water": water,
            "Exercise": exercise,
            "Mood": mood
        }

        df = st.session_state.health_data

        df = df[df["Date"] != selected_date]

        df = pd.concat(
            [df, pd.DataFrame([new_record])],
            ignore_index=True
        )

        st.session_state.health_data = (
            df.sort_values("Date").reset_index(drop=True)
        )

        st.success("Your daily health record has been saved!")

    st.divider()

    st.subheader("Competition Demo")

    if st.button("Load 7-Day Sample Data"):

        load_sample_data()

        st.success(
            "Sample data loaded! Explore the other sections."
        )

# ---------------- DATA CHECK ----------------

df = st.session_state.health_data.copy()

# ---------------- DASHBOARD ----------------

elif_page = page

if page == "Health Dashboard":

    st.header("📊 Personal Health Dashboard")

    if df.empty:
        st.warning("Please add health records first.")
    else:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Average Sleep",
            f"{df['Sleep'].mean():.1f} hrs"
        )

        col2.metric(
            "Average Steps",
            f"{df['Steps'].mean():,.0f}"
        )

        col3.metric(
            "Average Water",
            f"{df['Water'].mean():.1f} L"
        )

        col4.metric(
            "Average Exercise",
            f"{df['Exercise'].mean():.0f} min"
        )

        st.subheader("Your Health History")

        chart = df.set_index("Date")[
            ["Sleep", "Water", "Exercise"]
        ]

        st.line_chart(chart)

        st.subheader("Daily Activity")

        st.bar_chart(
            df.set_index("Date")[["Steps"]]
        )

        st.subheader("Recorded Information")

        st.dataframe(
            df.sort_values("Date", ascending=False),
            use_container_width=True
        )

        st.download_button(
            "Download Health History",
            df.to_csv(index=False),
            file_name="health_history.csv",
            mime="text/csv"
        )

# ---------------- HABIT INTELLIGENCE ----------------

elif page == "Habit Intelligence":

    st.header("🔍 Habit Relationship Discovery")

    if len(df) < 4:
        st.warning(
            "Record at least 4 days of data "
            "to explore habit relationships."
        )
    else:

        st.write(
            "This section explores how your recorded "
            "daily habits change together."
        )

        correlation = df[
            ["Sleep", "Steps", "Water", "Exercise", "Mood"]
        ].corr()

        st.subheader("Habit Relationship Matrix")

        st.dataframe(
            correlation.round(2),
            use_container_width=True
        )

        pairs = [
            ("Sleep", "Exercise"),
            ("Sleep", "Steps"),
            ("Water", "Exercise"),
            ("Steps", "Mood")
        ]

        st.subheader("Discovered Patterns")

        for first, second in pairs:

            value = correlation.loc[first, second]

            if pd.isna(value):
                continue

            if value >= 0.5:
                st.success(
                    f"{first} and {second} show a positive "
                    f"relationship in your recorded data ({value:.2f})."
                )

            elif value <= -0.5:
                st.warning(
                    f"{first} and {second} show an inverse "
                    f"relationship in your recorded data ({value:.2f})."
                )

            else:
                st.info(
                    f"No strong relationship was found "
                    f"between {first} and {second} ({value:.2f})."
                )

        st.caption(
            "These are statistical associations, not proof "
            "that one habit causes another."
        )

# ---------------- WEEKLY INSIGHTS ----------------

elif page == "Weekly Insights":

    st.header("📅 Weekly Habit Analysis")

    if len(df) < 2:
        st.warning(
            "Add more daily records to compare your habits."
        )
    else:

        df = df.sort_values("Date").copy()

        midpoint = len(df) // 2

        first_period = df.iloc[:midpoint]
        second_period = df.iloc[midpoint:]

        metrics = [
            "Sleep", "Steps", "Water", "Exercise"
        ]

        st.subheader("Habit Progress Comparison")

        comparison = pd.DataFrame({
            "Earlier Period": first_period[metrics].mean(),
            "Recent Period": second_period[metrics].mean()
        })

        comparison["Change"] = (
            comparison["Recent Period"]
            - comparison["Earlier Period"]
        )

        st.dataframe(
            comparison.round(2),
            use_container_width=True
        )

        for metric in metrics:

            change = comparison.loc[metric, "Change"]

            if change > 0:
                st.success(
                    f"{metric}: Increased by {change:.2f}."
                )
            elif change < 0:
                st.warning(
                    f"{metric}: Decreased by {abs(change):.2f}."
                )
            else:
                st.info(
                    f"{metric}: No change."
                )

# ---------------- PERSONALIZED SUGGESTIONS ----------------

elif page == "Recommendation Feedback":

    st.header("💡 Personalized Recommendations")

    if df.empty:
        st.warning("Please add your health records first.")
    else:

        suggestions = []

        average_sleep = df["Sleep"].mean()
        average_steps = df["Steps"].mean()
        average_water = df["Water"].mean()
        average_exercise = df["Exercise"].mean()

        if average_sleep < 7:
            suggestions.append(
                "Try maintaining a regular sleep schedule."
            )

        if average_steps < 5000:
            suggestions.append(
                "Gradually increase your daily walking activity."
            )

        if average_water < 2:
            suggestions.append(
                "Try drinking water regularly throughout the day."
            )

        if average_exercise < 30:
            suggestions.append(
                "Consider adding regular physical activity "
                "to your daily routine."
            )

        if not suggestions:
            suggestions.append(
                "Your recorded habits are meeting these "
                "general activity targets. Keep tracking!"
            )

        st.subheader("Your Suggested Actions")

        for i, suggestion in enumerate(suggestions):

            st.info(suggestion)

            choice = st.radio(
                "Did you follow this suggestion?",
                ["Not yet", "Yes", "Partially"],
                key=f"feedback_{i}"
            )

            st.session_state.feedback[suggestion] = choice

        st.divider()

        st.subheader("Your Feedback Summary")

        for suggestion, answer in st.session_state.feedback.items():

            st.write(f"**{suggestion}** — {answer}")

        st.caption(
            "Suggestions are based on simple activity thresholds "
            "and recorded averages. They are not medical advice."
        )

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "LifePattern AI | Personal Health Intelligence "
    "| Educational prototype, not a medical diagnostic tool."
)