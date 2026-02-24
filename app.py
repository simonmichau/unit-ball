import streamlit as st

from database import Database


@st.dialog("Are you sure?")
def player_delete_dialog(db: Database, player: str, player_id: int) -> None:
    st.write(f"Do you want to delete {player}?")
    col1, col2, _ = st.columns([1, 1, 3])
    if col1.button("Yes", type="primary", width="stretch"):
        db.delete_player(player_id)
        st.rerun()
    if col2.button("No", type="secondary", width="stretch"):
        st.rerun()


@st.dialog("Are you sure?")
def match_delete_dialog(db: Database, match_id: int) -> None:
    st.write(f"Do you want to delete this match?")
    col1, col2, _ = st.columns([1, 1, 3])
    if col1.button("Yes", type="primary", width="stretch"):
        db.delete_match(match_id)
        st.rerun()
    if col2.button("No", type="secondary", width="stretch"):
        st.rerun()


def main_app(db: Database):
    """Display the main application interface."""
    st.logo("img/unit-ball.svg", size="large")
    st.title("🏓 Ping Pong ELO Tracker")

    # Navigation
    pg = st.navigation([
        st.Page("pages/leaderboard.py", title="Leaderboard", icon="📊"),
        st.Page("pages/matches.py", title="Matches", icon="🏆"),
        st.Page("pages/settings.py", title="Settings", icon="⚙️"),
    ], position="top")
    pg.run()

    if st.button(f"👤 Logout **{st.user.name}**", type='tertiary'):
        st.logout()
        st.rerun()


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="UnitBall",
        page_icon="🏓",
        layout="wide"
    )

    # Initialize database
    if "db" not in st.session_state:
        db = Database()
        st.session_state.db = db

    # Show appropriate page
    if st.user.is_logged_in:
        main_app(st.session_state.db)
    else:
        st.login("google")


if __name__ == "__main__":
    main()
