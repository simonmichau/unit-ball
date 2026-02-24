import streamlit as st


db = st.session_state.db

st.subheader("Player Leaderboard")

players = db.get_all_players()

if players:
    # Create a formatted table
    for idx, (id, name, elo, matches_played, matches_won) in enumerate(players, 1):
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