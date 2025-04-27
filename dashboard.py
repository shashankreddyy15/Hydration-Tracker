import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.agent import WaterIntakeAgent
from src.database import log_intake, get_intake_history , delete_user_history

if "tracker_started" not in st.session_state:
    st.session_state.tracker_started = False

# -------------------------------------
# 👋 Welcome Section
# -------------------------------------
if not st.session_state.tracker_started:
    st.title("💧 Welcome to AI Hydration Tracker")
    st.markdown("""
    Track your daily hydration with help of an AI Assistant.
    Log your water intake, receive smart feedback, and stay healthy.    
    """)

    if st.button("Start Tracking"):
        st.session_state.tracker_started = True
        st.rerun()

# -------------------------------------
# 📊 Dashboard Section
# -------------------------------------
else:
    st.title("📈 AI Hydration Tracker Dashboard")

    st.sidebar.header("🚰 Log Your Water Intake")
    st.sidebar.markdown("💡 **Quick Hydration Tips:**")
    st.sidebar.markdown("🥤 Drink a glass of water before every meal.")
    st.sidebar.markdown("💻 Keep a bottle next to your laptop or desk.")
    st.sidebar.markdown("🌞 Start your day with 1 full glass of water.")
    st.sidebar.markdown("⏰ Sip water every 30 minutes, not just when thirsty.")
    st.sidebar.markdown("🍋 Flavor water with lemon or mint if it feels boring.")

user_list = ["user_1", "user_2", "Add New User"]
selected_user = st.sidebar.selectbox("Select User", options=user_list)

if selected_user == "Add New User":
    user_id = st.sidebar.text_input("Enter New User ID")
else:
    user_id = selected_user

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:red;'>⚠️ Danger Zone</h3>", unsafe_allow_html=True)

if st.sidebar.button("Delete User History"):
    st.session_state.confirm_delete = True  

if st.session_state.get("confirm_delete", False):
    if st.sidebar.button("✅ Confirm Delete"):
        if user_id:
            delete_user_history(user_id)
            st.success(f"🗑️ Deleted all hydration history for `{user_id}`")
            st.session_state.confirm_delete = False  
            st.rerun()
    if st.sidebar.button("❌ Cancel"):
        st.session_state.confirm_delete = False 

if "last_deleted_user" in st.session_state:
        st.sidebar.info(f"🗂️ Last Deleted User: `{st.session_state.last_deleted_user}`")

intake_ml = st.sidebar.number_input("Water Intake (ml)", min_value=0, max_value=1000)
daily_goal = st.sidebar.number_input("Set Your Daily Goal (ml)", min_value=500, max_value=10000, step=100, value=7000)

if st.sidebar.button("Submit"):
    if user_id and intake_ml > 0:
        log_intake(user_id, intake_ml)
        st.success(f"✅ Logged {intake_ml}ml for `{user_id}`")

        agent = WaterIntakeAgent()
        feedback = agent.analyze_intake(intake_ml)

        if "good" in feedback.lower() or "well" in feedback.lower():
            st.info(f"🥤 {feedback}")
        elif "drink more" in feedback.lower() or "increase" in feedback.lower():
            st.warning(f"🕒 {feedback}")
        else:
            st.info(f"💧 {feedback}")


    # -------------------------------------
    # 📅 Hydration History
    # -------------------------------------
    st.markdown("---")
    st.header("📆 Water Intake History")

    if user_id:
        history = get_intake_history(user_id)

        if history:
            dates = []
            for row in history:
                ts = row[1]
                try:
                    dt = datetime.strptime(ts, "%d-%m-%y %H:%M:%S")  
                except ValueError:
                    dt = datetime.strptime(ts, "%d-%m-%y") 
                dates.append(dt)

            values = [row[0] for row in history]

            df = pd.DataFrame({
                "Date & Time": dates,
                "Water Intake (ml)": values
            })

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Intake History as CSV",
                data=csv,
                file_name='hydration_log.csv',
                mime='text/csv',
            )

            st.dataframe(df)

            st.line_chart(df, x="Date & Time", y="Water Intake (ml)")

            # -------------------------------------
            # 🎯 Daily Goal Progress
            # -------------------------------------
            st.markdown("---")
            st.header("🎯 Daily Goal Progress")

            today = date.today()
            today_total = sum([
                row[0] for i, row in enumerate(history)
                if (
                    datetime.strptime(row[1], "%d-%m-%y %H:%M:%S").date() == today
                    if len(row[1]) > 10 else
                    datetime.strptime(row[1], "%d-%m-%y").date() == today
                )
            ])

            col1, col2, col3 = st.columns(3)
            col1.metric("Today's Intake", f"{today_total} ml")
            col2.metric("Goal", f"{daily_goal} ml")
            col3.metric("Completion", f"{int(today_total/daily_goal*100)}%")

            progress = min(today_total / daily_goal, 1.0)
            st.progress(progress)

            if progress == 1.0:
                st.success("🎉 You've reached your hydration goal!")
            elif progress >= 0.75:
                st.info("💪 Almost there, keep it up!")
            else:
                st.warning("🕒 Drink more water to reach your goal.")

            # -------------------------------------
            # 🔥 Streaks / Achievements
            # -------------------------------------
            st.markdown("---")
            st.header("🔥 Hydration Streaks")

            streak = 0
            previous_date = None
            for d in sorted(dates):
                if previous_date is None or (d.date() - previous_date).days == 1:
                    streak += 1
                else:
                    streak = 1
                previous_date = d.date()

            if streak >= 5:
                st.success(f"🏆 You're on a {streak}-day hydration streak!")
            else:
                st.info(f"✅ Current streak: {streak} day(s)")

        else:
            st.warning("⚠️ No water intake data found. Please log your intake first.")
