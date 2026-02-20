import streamlit as st
from streamlit_extras.let_it_rain import rain
from datetime import datetime
from database import Database
from random import choice
from elo_system import process_match


def main_app(db: Database):
    """Display the main application interface."""
    st.logo("img/unit-ball.svg", size="large")
    st.title("🏓 Ping Pong ELO Tracker")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📊 Leaderboard", "🏆 Matches", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Player Leaderboard")
        players = db.get_all_players()
        
        if players:
            # Create a formatted table
            st.markdown("### Rankings")
            for idx, (name, elo, matches_played, matches_won) in enumerate(players, 1):
                win_rate = (matches_won / matches_played * 100) if matches_played > 0 else 0
                
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                with col1:
                    if idx == 1:
                        st.markdown("🥇")
                    elif idx == 2:
                        st.markdown("🥈")
                    elif idx == 3:
                        st.markdown("🥉")
                    else:
                        st.markdown(f"**{idx}**")
                with col2:
                    st.markdown(f"**{name}**")
                with col3:
                    st.markdown(f"⭐ {elo}")
                with col4:
                    st.markdown(f"🎮 {matches_played}")
                with col5:
                    st.markdown(f"📈 {win_rate:.1f}%")
            
            st.divider()
            st.caption("⭐ ELO Rating | 🎮 Matches Played | 📈 Win Rate")
        else:
            st.info("No players yet. Add players from the sidebar!")
    
    with tab2:
        st.subheader("➕ Record a Match")
        
        players = db.get_all_players()
        
        if len(players) < 2:
            st.warning("You need at least 2 players to record a match. Add players from the sidebar.")
        else:
            player_names = [p[0] for p in players]
            
            with st.container(border=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    winner = st.selectbox("Winner", player_names)

                with col2:
                    other_player_names = list(filter(lambda x: x != winner, player_names))
                    looser = st.selectbox("Defeated", other_player_names)

                # Get player IDs and current ELO ratings
                winner_id = db.get_player_id(winner)
                looser_id = db.get_player_id(looser)

                winner_elo = db.get_player_elo(winner_id)
                looser_elo = db.get_player_elo(looser_id)

                # Calculate new ELO ratings
                new_elo_winner, new_elo_defeated = process_match(winner_elo, looser_elo)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label=f"{winner}'s ELO after this match",
                        value=new_elo_winner,
                        delta=new_elo_winner - winner_elo
                    )
                with col2:
                    st.metric(
                        label=f"{looser}'s ELO after this match",
                        value=new_elo_defeated,
                        delta=new_elo_defeated - looser_elo
                    )

                submit_match = st.button("🏓 Submit Match")
                
                if submit_match:
                    if winner == looser:
                        st.error("Please select different players")
                    else:
                        # Update database
                        db.add_match(
                            winner_id, looser_id,
                            winner_elo, looser_elo,
                            new_elo_winner, new_elo_defeated,
                            st.user
                        )
                        
                        # Update player stats
                        db.update_player_stats(winner_id, new_elo_winner, True)
                        db.update_player_stats(looser_id, new_elo_defeated, False)

                        st.toast(f"Match {winner} v {looser} recorded successfully!", icon="✅")

        st.subheader("📜 Recent Matches")

        matches = db.get_recent_matches(20)

        if matches:
            for match in matches:
                player_a, player_b, elo_a, elo_b, elo_a_before, elo_b_before, created_at, created_by = match

                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 2], vertical_alignment="center")
                    with col1:
                        st.metric(str(elo_a), player_a, elo_a - elo_a_before)
                    with col2:
                        verbs = ['defeated', 'destroyed', 'beat', 'vanquished', 'overwhelmed',
                                 'crushed', 'subdued', 'subjugated']
                        st.write(f"**{choice(verbs)}**")
                    with col3:
                        st.metric(str(elo_b), player_b, elo_b - elo_b_before)
                    with col4:
                        # Format timestamp properly
                        try:
                            dt = datetime.fromisoformat(created_at)
                            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                        except (ValueError, AttributeError, TypeError):
                            formatted_date = created_at[:16] if len(created_at) >= 16 else created_at
                        st.write(f"📅 {formatted_date}")
                        st.caption(f"Match entered by {created_by}")
        else:
            st.info("No matches recorded yet. Add a match to get started!")

    with tab3:
        with st.form("add_player_form"):
            player_name = st.text_input("Player Name")
            add_player = st.form_submit_button("Add New Player")

            if add_player and player_name:
                if db.create_player(player_name):
                    st.success(f"Player {player_name} added!")
                    st.rerun()
                else:
                    st.error("Player already exists")

        if st.button("Make it rain!"):
            celebration_list = ["🎱🏓", "🎱", "🏓", "🏆", "⚔️", "🪩", "💯"]
            rain(
                emoji=choice(celebration_list),
                font_size=54,
                falling_speed=2,
                animation_length=1,
            )

    if st.button(f"👤 Logout **{st.user.name}**", type='tertiary'):
        st.logout()
        st.rerun()


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Ping Pong ELO Tracker",
        page_icon="🏓",
        layout="wide"
    )
    
    # Initialize database
    db = Database()
    
    # Show appropriate page
    if st.user.is_logged_in:
        main_app(db)
    else:
        st.login("google")


if __name__ == "__main__":
    main()
