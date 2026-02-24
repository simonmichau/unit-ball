from datetime import datetime
from random import choice

import streamlit as st

from app import match_delete_dialog
from elo_system import process_match

db = st.session_state.db

st.subheader("➕ Record a Match")

players = db.get_all_players()

tab_1, tab_2 = st.tabs(['👤 1v1', '👥 2v2'], default='👥 2v2')

with tab_1:
    if len(players) < 2:
        st.warning("You need at least 2 players to record a match. Add players in the ⚙️ Settings tab.")
    else:
        player_names = [p[1] for p in players]

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
            new_elo_winner, new_elo_looser = process_match(winner_elo, looser_elo)

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
                    value=new_elo_looser,
                    delta=new_elo_looser - looser_elo
                )

            submit_match = st.button("🏓 Submit Match", key="submit_1v1")

            if submit_match:
                if winner == looser:
                    st.error("Please select different players")
                else:
                    # Update database
                    db.add_match(
                        winner_id, looser_id,
                        winner_elo, looser_elo,
                        new_elo_winner, new_elo_looser,
                        st.user
                    )

                    # Update player stats
                    db.update_player_stats(winner_id, new_elo_winner, True)
                    db.update_player_stats(looser_id, new_elo_looser, False)

                    st.toast(f"Match {winner}/{looser} recorded successfully!", icon="✅")
with tab_2:
    if len(players) < 4:
        st.warning("You need at least 4 players to record a 2v2 match. Add players in the ⚙️ Settings tab.")
    else:
        player_names = [p[1] for p in players]

        with st.container(border=True):
            col1, col2 = st.columns(2)

            with col1:
                winner_a = st.selectbox("Winner A", player_names)
                winner_b = st.selectbox("Winner B", player_names)

            with col2:
                other_player_names = list(filter(lambda x: x != winner_a and x != winner_b, player_names))
                looser_a = st.selectbox("Defeated A", other_player_names)
                looser_b = st.selectbox("Defeated B", other_player_names)

            # Get player IDs and current ELO ratings
            winner_a_id = db.get_player_id(winner_a)
            winner_b_id = db.get_player_id(winner_b)
            looser_a_id = db.get_player_id(looser_a)
            looser_b_id = db.get_player_id(looser_b)

            winner_a_elo = db.get_player_elo(winner_a_id)
            winner_b_elo = db.get_player_elo(winner_b_id)
            looser_a_elo = db.get_player_elo(looser_a_id)
            looser_b_elo = db.get_player_elo(looser_b_id)
            winners_avg_elo = (db.get_player_elo(winner_a_id) + db.get_player_elo(winner_b_id)) // 2
            loosers_avg_elo = (db.get_player_elo(looser_a_id) + db.get_player_elo(looser_b_id)) // 2

            # Calculate new ELO ratings
            new_elo_winners, new_elo_loosers = process_match(winners_avg_elo, loosers_avg_elo)
            elo_delta_winners = (new_elo_winners - winners_avg_elo) // 2
            elo_delta_loosers = (new_elo_loosers - loosers_avg_elo) // 2

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    label=f"{winner_a}'s ELO after this match",
                    value=winner_a_elo + elo_delta_winners,
                    delta=elo_delta_winners
                )
            with col2:
                st.metric(
                    label=f"{winner_b}'s ELO after this match",
                    value=winner_b_elo + elo_delta_winners,
                    delta=elo_delta_winners
                )
            with col3:
                st.metric(
                    label=f"{looser_a}'s ELO after this match",
                    value=looser_a_elo + elo_delta_loosers,
                    delta=elo_delta_loosers
                )
            with col4:
                st.metric(
                    label=f"{looser_b}'s ELO after this match",
                    value=looser_b_elo + elo_delta_loosers,
                    delta=elo_delta_loosers
                )

            submit_match = st.button("🏓 Submit Match", key="submit_2v2")

            if submit_match:
                if winner_a in [looser_a, looser_b]:
                    st.error("Please select different players")
                else:
                    # Update database
                    # TODO: change scheme to accomodate 2v2 (maybe just add new DB table)
                    db.add_match(
                        winner_id, looser_id,
                        winner_elo, looser_elo,
                        new_elo_winners, new_elo_loosers,
                        st.user
                    )

                    # Update player stats
                    db.update_player_stats(winner_a_id, winner_a_elo + elo_delta_winners, True)
                    db.update_player_stats(winner_b_id, winner_b_elo + elo_delta_loosers, True)
                    db.update_player_stats(looser_a_id, looser_a_elo + elo_delta_loosers, False)
                    db.update_player_stats(looser_b_id, looser_b_elo + elo_delta_loosers, False)

                    st.toast(f"Match {winner}/{looser} recorded successfully!", icon="✅")

st.subheader("📜 Recent Matches")

matches = db.get_recent_matches(20)

if matches:
    for match in matches:
        match_id, player_a, player_b, elo_a, elo_b, elo_a_before, elo_b_before, created_at, created_by = match

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
                left, right = st.columns(2)
                with left:
                    # Format timestamp properly
                    try:
                        dt = datetime.fromisoformat(created_at)
                        formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                    except (ValueError, AttributeError, TypeError):
                        formatted_date = created_at[:16] if len(created_at) >= 16 else created_at
                    st.write(f"📅 {formatted_date}")
                    st.caption(f"Match entered by {created_by}")
                with right:
                    if st.button("", icon="🗑️", type="tertiary", key=str(match_id)):
                        match_delete_dialog(db, match_id)
else:
    st.info("No matches recorded yet. Add a match to get started!")