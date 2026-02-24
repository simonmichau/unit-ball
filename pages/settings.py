from random import choice

import streamlit as st
from streamlit_extras.let_it_rain import rain

from app import player_delete_dialog


db = st.session_state.db


with st.form("add_player_form"):
    player_name = st.text_input("Player Name")
    add_player = st.form_submit_button("Add New Player", type="primary")

    if add_player and player_name:
        if db.create_player(player_name):
            st.success(f"Player {player_name} added!")
            st.rerun()
        else:
            st.error("Player already exists")

if st.button("💶 Make it rain!", ):
    celebration_list = ["🎱🏓", "🎱", "🏓", "🏆", "⚔️", "🪩", "💯", "💶"]
    rain(
        emoji=choice(celebration_list),
        font_size=54,
        falling_speed=2,
        animation_length=1,
    )

with st.expander("⚠️ Call Kenny Loggins because you are entering the **Danger Zone**"):
    with st.form("delete_player_form"):
        players = db.get_all_players()
        player_entries = [f"#{' '.join(str(x) for x in player)}" for player in players]

        player_entry = st.selectbox("Player to delete", player_entries)
        player_id_to_delete = int(player_entry.split()[0][1:])
        player_name_to_delete = player_entry.split()[1]

        delete_player = st.form_submit_button("Delete Player", type="primary")

        if delete_player and player_name_to_delete:
            player_delete_dialog(db, player_name_to_delete, player_id_to_delete)