import streamlit as st
from database import Database
from elo_system import process_match


def init_session_state():
    """Initialize session state variables."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None


def login_page(db: Database):
    """Display the login/registration page."""
    st.title("🏓 Ping Pong ELO Tracker")
    st.subheader("Login or Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    if db.verify_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = db.get_user_id(username)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register = st.form_submit_button("Register")
            
            if register:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        if db.create_user(new_username, new_password):
                            st.success("Registration successful! Please login.")
                        else:
                            st.error("Username already exists")
                else:
                    st.warning("Please fill in all fields")


def main_app(db: Database):
    """Display the main application interface."""
    st.title("🏓 Ping Pong ELO Tracker")
    
    # Sidebar
    with st.sidebar:
        st.write(f"👤 Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.rerun()
        
        st.divider()
        st.subheader("Add New Player")
        with st.form("add_player_form"):
            player_name = st.text_input("Player Name")
            add_player = st.form_submit_button("Add Player")
            
            if add_player and player_name:
                if db.create_player(player_name):
                    st.success(f"Player {player_name} added!")
                    st.rerun()
                else:
                    st.error("Player already exists")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📊 Leaderboard", "➕ Add Match", "📜 Recent Matches"])
    
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
        st.subheader("Record a Match")
        
        players = db.get_all_players()
        
        if len(players) < 2:
            st.warning("You need at least 2 players to record a match. Add players from the sidebar.")
        else:
            player_names = [p[0] for p in players]
            
            with st.form("match_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    player_a = st.selectbox("Player A", player_names)
                    player_a_points = st.number_input("Points for Player A", min_value=0, value=0)
                
                with col2:
                    player_b = st.selectbox("Player B", player_names)
                    player_b_points = st.number_input("Points for Player B", min_value=0, value=0)
                
                submit_match = st.form_submit_button("Submit Match")
                
                if submit_match:
                    if player_a == player_b:
                        st.error("Please select different players")
                    else:
                        # Get player IDs and current ELO ratings
                        player_a_id = db.get_player_id(player_a)
                        player_b_id = db.get_player_id(player_b)
                        
                        player_a_elo = db.get_player_elo(player_a_id)
                        player_b_elo = db.get_player_elo(player_b_id)
                        
                        # Calculate new ELO ratings
                        new_elo_a, new_elo_b = process_match(
                            player_a_elo, player_b_elo,
                            player_a_points, player_b_points
                        )
                        
                        # Update database
                        db.add_match(
                            player_a_id, player_b_id,
                            player_a_points, player_b_points,
                            player_a_elo, player_b_elo,
                            new_elo_a, new_elo_b,
                            st.session_state.user_id
                        )
                        
                        # Update player stats
                        player_a_won = player_a_points > player_b_points
                        player_b_won = player_b_points > player_a_points
                        
                        db.update_player_stats(player_a_id, new_elo_a, player_a_won)
                        db.update_player_stats(player_b_id, new_elo_b, player_b_won)
                        
                        # Display results
                        st.success("Match recorded successfully!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(
                                label=f"{player_a} ELO",
                                value=new_elo_a,
                                delta=new_elo_a - player_a_elo
                            )
                        with col2:
                            st.metric(
                                label=f"{player_b} ELO",
                                value=new_elo_b,
                                delta=new_elo_b - player_b_elo
                            )
                        
                        st.rerun()
    
    with tab3:
        st.subheader("Recent Matches")
        
        matches = db.get_recent_matches(20)
        
        if matches:
            for match in matches:
                player_a, player_b, points_a, points_b, elo_a, elo_b, created_at = match
                
                # Determine winner
                if points_a > points_b:
                    result_text = f"**{player_a}** defeated {player_b}"
                elif points_b > points_a:
                    result_text = f"**{player_b}** defeated {player_a}"
                else:
                    result_text = f"**{player_a}** tied with **{player_b}**"
                
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.write(result_text)
                    with col2:
                        st.write(f"Score: {points_a} - {points_b}")
                    with col3:
                        # Format timestamp properly
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(created_at)
                            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            formatted_date = created_at[:16] if len(created_at) >= 16 else created_at
                        st.write(f"📅 {formatted_date}")
                    st.caption(f"ELO: {player_a} ({elo_a}) | {player_b} ({elo_b})")
                    st.divider()
        else:
            st.info("No matches recorded yet. Add a match to get started!")


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Ping Pong ELO Tracker",
        page_icon="🏓",
        layout="wide"
    )
    
    # Initialize database
    db = Database()
    
    # Initialize session state
    init_session_state()
    
    # Show appropriate page
    if st.session_state.logged_in:
        main_app(db)
    else:
        login_page(db)


if __name__ == "__main__":
    main()
