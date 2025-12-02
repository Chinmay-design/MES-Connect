import streamlit as st
import uuid
from datetime import datetime
from auth import login_page, logout
from database import (
    db, get_clubs, join_club_request, approve_club_request, 
    create_chat, send_message, get_chat_messages, create_call, 
    get_calls, get_user_calls, update_call_status, create_confession,
    get_confessions_for_students, get_confessions_for_admin, like_confession,
    get_likes_count, add_comment, get_comments_for_students, create_announcement
)

# Page configuration
st.set_page_config(
    page_title="Campus Connect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'current_chat' not in st.session_state:
        st.session_state.current_chat = None
    if 'start_call_with' not in st.session_state:
        st.session_state.start_call_with = None
    if 'active_call' not in st.session_state:
        st.session_state.active_call = None
    
    # Show login if not authenticated
    if not st.session_state.user:
        login_page()
    else:
        show_main_app()

def show_main_app():
    """Show the main application with sidebar navigation"""
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("# 🎓 Campus Connect")
        st.write(f"**Welcome, {st.session_state.user.get('name', 'User')}**")
        st.write(f"**Role:** {st.session_state.role.title()}")
        
        if st.session_state.role == 'student':
            st.write(f"**Major:** {st.session_state.user.get('major', 'Student')}")
            st.write(f"**Year:** {st.session_state.user.get('year', '')}")
            
            # Student navigation
            st.markdown("---")
            st.subheader("Student Navigation")
            pages = [
                "🏠 Home", "👤 Profile", "📢 Announcements", 
                "👥 Clubs", "💬 Chat", "📞 Calls", "🗣️ Confessions"
            ]
            
            selected_page = st.radio("Go to:", pages, key="student_nav")
            st.session_state.current_page = selected_page
            
        else:  # Admin
            st.write("⚡ Administrator")
            
            # Admin navigation
            st.markdown("---")
            st.subheader("Admin Tools")
            pages = [
                "📊 Dashboard", "👥 User Management", "📢 Announcements", 
                "👥 Club Management", "🗣️ Confessions", "💬 Chat", "📞 Calls"
            ]
            
            selected_page = st.radio("Go to:", pages, key="admin_nav")
            st.session_state.current_page = selected_page
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Main content area
    display_current_page()

def display_current_page():
    """Display the current page based on selection"""
    page = st.session_state.current_page
    
    if st.session_state.role == 'student':
        if page == "🏠 Home":
            show_student_home()
        elif page == "👤 Profile":
            show_student_profile()
        elif page == "📢 Announcements":
            show_announcements()
        elif page == "👥 Clubs":
            show_clubs()
        elif page == "💬 Chat":
            show_chat()
        elif page == "📞 Calls":
            show_calls()
        elif page == "🗣️ Confessions":
            show_confessions()
    else:  # Admin
        if page == "📊 Dashboard":
            show_admin_dashboard()
        elif page == "👥 User Management":
            show_user_management()
        elif page == "📢 Announcements":
            show_announcement_management()
        elif page == "👥 Club Management":
            show_club_management()
        elif page == "🗣️ Confessions":
            show_confession_management()
        elif page == "💬 Chat":
            show_chat()
        elif page == "📞 Calls":
            show_calls()

# Student Pages
def show_student_home():
    st.title("🏠 Welcome to Campus Connect!")
    st.write(f"Hello, {st.session_state.user['name']}! 👋")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        clubs = get_clubs()
        user_clubs = sum(1 for club in clubs.values() if st.session_state.user['email'] in club.get('members', []))
        st.metric("Clubs Joined", user_clubs)
    
    with col2:
        announcements = db.load_data("announcements.json")
        st.metric("Announcements", len(announcements))
    
    with col3:
        students = db.load_data("students.json")
        st.metric("Campus Members", len(students))
    
    with col4:
        confessions = get_confessions_for_students()
        st.metric("Confessions", len(confessions))
    
    st.divider()
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💬 Message Admin", use_container_width=True):
            chat_id = create_chat(st.session_state.user['email'], "MES.edu")
            st.session_state.current_chat = chat_id
            st.session_state.current_page = "💬 Chat"
            st.rerun()
    
    with col2:
        if st.button("📞 Call Admin", use_container_width=True):
            st.session_state.start_call_with = "MES.edu"
            st.session_state.current_page = "📞 Calls"
            st.rerun()
    
    with col3:
        if st.button("🗣️ Share Confession", use_container_width=True):
            st.session_state.current_page = "🗣️ Confessions"
            st.rerun()
    
    with col4:
        if st.button("👥 Browse Clubs", use_container_width=True):
            st.session_state.current_page = "👥 Clubs"
            st.rerun()
    
    st.divider()
    
    # Recent announcements
    st.subheader("📢 Recent Announcements")
    announcements = db.load_data("announcements.json")[-3:]
    
    if announcements:
        for announcement in announcements:
            with st.container():
                priority = announcement.get('priority', 'medium')
                emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                st.write(f"{emoji} **{announcement.get('title', 'No Title')}**")
                message = announcement.get('message', '')
                if len(message) > 150:
                    st.write(f"{message[:150]}...")
                else:
                    st.write(message)
                st.caption(f"By {announcement.get('author', 'Admin')} • {announcement.get('created_date', '')[:10]}")
                st.divider()
    else:
        st.info("No announcements yet.")

def show_student_profile():
    st.title("👤 Student Profile")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Personal Information")
        st.write(f"**Name:** {st.session_state.user['name']}")
        st.write(f"**Email:** {st.session_state.user['email']}")
        st.write(f"**Year:** {st.session_state.user.get('year', 'Not specified')}")
        st.write(f"**Major:** {st.session_state.user.get('major', 'Not specified')}")
        st.write(f"**Member since:** {st.session_state.user.get('joined_date', 'Today')[:10]}")
    
    with col2:
        st.subheader("Club Memberships")
        clubs = get_clubs()
        user_clubs = [club for club in clubs.values() if st.session_state.user['email'] in club.get('members', [])]
        
        if user_clubs:
            for club in user_clubs:
                st.success(f"✅ {club['name']}")
        else:
            st.info("Not joined any clubs yet")

def show_announcements():
    st.title("📢 Campus Announcements")
    
    announcements = db.load_data("announcements.json")
    
    if announcements:
        for announcement in announcements:
            with st.container():
                priority = announcement.get('priority', 'medium')
                emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                st.write(f"{emoji} **{announcement.get('title', 'No Title')}**")
                st.write(announcement.get('message', ''))
                st.caption(f"By {announcement.get('author', 'Admin')} • {announcement.get('created_date', '')[:10]}")
                st.divider()
    else:
        st.info("No announcements available.")

def show_clubs():
    st.title("👥 Campus Clubs")
    
    clubs = get_clubs()
    current_user = st.session_state.user['email']
    
    if clubs:
        for club_id, club in clubs.items():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(club['name'])
                    st.write(club['description'])
                    st.caption(f"📍 {club.get('location', 'TBA')}")
                    st.caption(f"📅 {club.get('meeting_schedule', 'Schedule TBA')}")
                    st.caption(f"👥 {len(club.get('members', []))} members")
                
                with col2:
                    if current_user in club.get('members', []):
                        st.success("✅ Joined")
                    elif current_user in club.get('pending_requests', []):
                        st.info("⏳ Pending Approval")
                    else:
                        if st.button("Join Club", key=f"join_{club_id}"):
                            if join_club_request(current_user, club_id):
                                st.success("Join request sent!")
                                st.rerun()
                
                st.divider()
    else:
        st.info("No clubs available at the moment.")

def show_chat():
    st.title("💬 Campus Chat")
    
    if st.session_state.current_chat:
        show_chat_messages()
    else:
        show_chat_list()

def show_chat_list():
    st.subheader("Start a Conversation")
    
    if st.session_state.role == 'student':
        # Student can chat with admin and other students
        st.write("**Chat with Administrator**")
        if st.button("💬 Message Admin", key="admin_chat"):
            chat_id = create_chat(st.session_state.user['email'], "MES.edu")
            st.session_state.current_chat = chat_id
            st.rerun()
        
        st.divider()
        
        # Other students
        students = db.load_data("students.json")
        other_students = [s for s in students.items() if s[0] != st.session_state.user['email']]
        
        if other_students:
            st.write("**Other Students**")
            for email, student in other_students:
                if st.button(f"💬 {student['name']} ({student.get('major', 'Student')})", key=f"chat_{email}"):
                    chat_id = create_chat(st.session_state.user['email'], email)
                    st.session_state.current_chat = chat_id
                    st.rerun()
        else:
            st.info("No other students registered yet.")
    
    else:  # Admin
        students = db.load_data("students.json")
        
        if students:
            for email, student in students.items():
                if st.button(f"💬 {student['name']} - {student.get('major', 'Student')}", key=f"admin_chat_{email}"):
                    chat_id = create_chat("MES.edu", email)
                    st.session_state.current_chat = chat_id
                    st.rerun()
        else:
            st.info("No students registered yet.")

def show_chat_messages():
    chat_id = st.session_state.current_chat
    messages = get_chat_messages(chat_id)
    
    # Display chat header
    st.subheader("Chat Messages")
    
    # Display messages
    chat_container = st.container()
    with chat_container:
        for msg in messages:
            if msg['sender'] == st.session_state.user['email']:
                st.write(f"**You:** {msg['message']}")
            else:
                sender_name = "Admin" if msg['sender'] == "MES.edu" else msg['sender']
                st.write(f"**{sender_name}:** {msg['message']}")
            st.caption(f"Sent at {msg['timestamp'][11:16]}")
    
    # Message input
    st.divider()
    new_message = st.text_input("Type your message...", key="new_message")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Send") and new_message.strip():
            send_message(chat_id, st.session_state.user['email'], new_message.strip())
            st.rerun()
    with col2:
        if st.button("Back to Chat List"):
            st.session_state.current_chat = None
            st.rerun()

def show_calls():
    st.title("📞 Voice/Video Calls")
    
    if st.session_state.start_call_with:
        show_call_interface()
    elif st.session_state.active_call:
        show_active_call()
    else:
        show_call_dashboard()

def show_call_dashboard():
    st.subheader("Start a Call")
    
    if st.session_state.role == 'student':
        # Student can call admin
        if st.button("📞 Call Administrator", use_container_width=True):
            st.session_state.start_call_with = "MES.edu"
            st.rerun()
    else:
        # Admin can call students
        students = db.load_data("students.json")
        
        if students:
            for email, student in students.items():
                if st.button(f"📞 Call {student['name']}", key=f"call_{email}", use_container_width=True):
                    st.session_state.start_call_with = email
                    st.rerun()
        else:
            st.info("No students available to call.")
    
    st.divider()
    st.subheader("Call History")
    
    calls = get_user_calls(st.session_state.user['email'])
    if calls:
        for call in calls[-5:]:
            with st.container():
                other_participants = [p for p in call['participants'] if p != st.session_state.user['email']]
                other_user = other_participants[0] if other_participants else "Unknown"
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**With:** {other_user}")
                with col2:
                    st.write(f"**Type:** {call['type']}")
                with col3:
                    st.write(f"**Status:** {call['status']}")
                st.caption(f"Time: {call.get('start_time', '')[:16]}")
                st.divider()
    else:
        st.info("No call history yet.")

def show_call_interface():
    target_email = st.session_state.start_call_with
    students = db.load_data("students.json")
    target_name = students.get(target_email, {}).get('name', 'User') if target_email != "MES.edu" else "Administrator"
    
    st.title(f"📞 Calling {target_name}")
    
    call_type = st.radio("Call Type:", ["Voice Call", "Video Call"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Call", type="primary", use_container_width=True):
            call_data = {
                "id": str(uuid.uuid4()),
                "participants": [st.session_state.user['email'], target_email],
                "type": "video" if call_type == "Video Call" else "voice",
                "start_time": datetime.now().isoformat(),
                "status": "active",
                "initiator": st.session_state.user['email']
            }
            create_call(call_data)
            st.session_state.active_call = call_data
            st.session_state.start_call_with = None
            st.rerun()
    
    with col2:
        if st.button("Cancel Call", use_container_width=True):
            st.session_state.start_call_with = None
            st.rerun()

def show_active_call():
    call = st.session_state.active_call
    
    st.title("📞 Active Call")
    
    participants = call['participants']
    other_user = [p for p in participants if p != st.session_state.user['email']][0]
    students = db.load_data("students.json")
    other_name = students.get(other_user, {}).get('name', 'User') if other_user != "MES.edu" else "Administrator"
    
    st.write(f"**In call with:** {other_name}")
    st.write(f"**Call type:** {call['type'].title()} Call")
    st.write("**Status:** 🔴 Live")
    
    # Call controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Mute Audio", use_container_width=True):
            st.info("Audio muted")
    
    with col2:
        if st.button("Disable Video", use_container_width=True):
            st.info("Video disabled")
    
    with col3:
        if st.button("End Call", type="primary", use_container_width=True):
            update_call_status(call['id'], 'ended')
            st.session_state.active_call = None
            st.success("Call ended")
            st.rerun()

def show_confessions():
    st.title("🗣️ Campus Confessions")
    
    tab1, tab2 = st.tabs(["Share Confession", "View Confessions"])
    
    with tab1:
        st.subheader("Share Your Confession")
        with st.form("confession_form"):
            category = st.selectbox("Category", [
                "💭 General", "💕 Relationships", "📚 Academics", 
                "😔 Regrets", "🎉 Achievements", "🤔 Advice"
            ])
            confession_text = st.text_area("Your confession", height=150, 
                                         placeholder="Share your thoughts anonymously...")
            
            if st.form_submit_button("Share Confession"):
                if confession_text.strip():
                    confession_data = {
                        "id": str(uuid.uuid4()),
                        "text": confession_text.strip(),
                        "category": category,
                        "user_email": st.session_state.user['email'],
                        "created_date": datetime.now().isoformat(),
                        "is_approved": st.session_state.role == 'admin',  # Auto-approve for admin
                        "likes": [],
                        "comments": []
                    }
                    
                    if create_confession(confession_data):
                        st.success("Confession shared successfully! 🎉")
                        if st.session_state.role == 'student':
                            st.info("Your confession is pending admin approval.")
                else:
                    st.error("Please write your confession")
    
    with tab2:
        st.subheader("Campus Confessions")
        confessions = get_confessions_for_students()
        
        if confessions:
            for confession in confessions:
                with st.container():
                    st.write(f"**{confession['category']}**")
                    st.write(confession['text'])
                    
                    # Likes and comments
                    likes_count = len(confession.get('likes', []))
                    comments_count = len(confession.get('comments', []))
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        if st.button(f"❤️ {likes_count}", key=f"like_{confession['id']}"):
                            if like_confession(confession['id'], st.session_state.user['email']):
                                st.success("Liked!")
                                st.rerun()
                    
                    with col2:
                        if st.button(f"💬 {comments_count}", key=f"comment_btn_{confession['id']}"):
                            # Toggle comments view
                            if f"show_comments_{confession['id']}" not in st.session_state:
                                st.session_state[f"show_comments_{confession['id']}"] = True
                            else:
                                st.session_state[f"show_comments_{confession['id']}"] = not st.session_state[f"show_comments_{confession['id']}"]
                            st.rerun()
                    
                    with col3:
                        st.caption(f"Posted on {confession['created_date'][:10]}")
                    
                    # Show comments if toggled
                    if st.session_state.get(f"show_comments_{confession['id']}"):
                        st.divider()
                        st.write("**Comments:**")
                        
                        comments = get_comments_for_students(confession)
                        for comment in comments:
                            st.write(f"👤 Anonymous: {comment.get('text', '')}")
                            st.caption(f"Posted on {comment.get('created_date', '')[:10]}")
                        
                        # Add comment
                        with st.form(f"add_comment_{confession['id']}"):
                            new_comment = st.text_input("Add a comment...", key=f"new_comment_{confession['id']}")
                            if st.form_submit_button("Post Comment"):
                                if new_comment.strip():
                                    comment_data = {
                                        "id": str(uuid.uuid4()),
                                        "text": new_comment.strip(),
                                        "created_date": datetime.now().isoformat()
                                    }
                                    if add_comment(confession['id'], comment_data, st.session_state.user['email']):
                                        st.success("Comment added!")
                                        st.rerun()
                    
                    st.divider()
        else:
            st.info("No confessions yet. Be the first to share!")

# Admin Pages
def show_admin_dashboard():
    st.title("📊 Admin Dashboard")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        students = db.load_data("students.json")
        st.metric("Total Students", len(students))
    
    with col2:
        clubs = get_clubs()
        st.metric("Active Clubs", len(clubs))
    
    with col3:
        announcements = db.load_data("announcements.json")
        st.metric("Announcements", len(announcements))
    
    with col4:
        confessions = get_confessions_for_admin()
        pending_confessions = len([c for c in confessions if not c.get('is_approved', False)])
        st.metric("Pending Confessions", pending_confessions)
    
    st.divider()
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📢 Create Announcement", use_container_width=True):
            st.session_state.current_page = "📢 Announcements"
            st.rerun()
    
    with col2:
        if st.button("👥 Manage Club Requests", use_container_width=True):
            st.session_state.current_page = "👥 Club Management"
            st.rerun()
    
    with col3:
        if st.button("🗣️ Review Confessions", use_container_width=True):
            st.session_state.current_page = "🗣️ Confessions"
            st.rerun()
    
    st.divider()
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Pending club requests
    requests = db.load_data("club_requests.json")
    pending_requests = [r for r in requests if r.get('status') == 'pending']
    
    if pending_requests:
        st.write(f"**Pending Club Join Requests:** {len(pending_requests)}")
        for request in pending_requests[:3]:
            student_email = request['student_email']
            student = students.get(student_email, {})
            st.write(f"• {student.get('name', student_email)} wants to join a club")
    else:
        st.write("No pending club requests")

def show_user_management():
    st.title("👥 User Management")
    
    students = db.load_data("students.json")
    
    if students:
        st.subheader(f"Registered Students ({len(students)})")
        
        for email, student in students.items():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{student['name']}**")
                    st.caption(f"Email: {email}")
                
                with col2:
                    st.write(f"Major: {student.get('major', 'Not specified')}")
                    st.write(f"Year: {student.get('year', 'Not specified')}")
                
                with col3:
                    # Count clubs joined
                    clubs = get_clubs()
                    clubs_joined = sum(1 for club in clubs.values() if email in club.get('members', []))
                    st.write(f"Clubs: {clubs_joined}")
                
                st.divider()
    else:
        st.info("No students registered yet.")

def show_announcement_management():
    st.title("📢 Announcement Management")
    
    # Create announcement
    with st.expander("Create New Announcement", expanded=True):
        with st.form("create_announcement"):
            title = st.text_input("Announcement Title")
            message = st.text_area("Announcement Message", height=100)
            priority = st.selectbox("Priority Level", ["low", "medium", "high"])
            
            if st.form_submit_button("Publish Announcement"):
                if title and message:
                    announcement_data = {
                        "id": str(uuid.uuid4()),
                        "title": title,
                        "message": message,
                        "category": "general",
                        "priority": priority,
                        "author": st.session_state.user['name'],
                        "created_date": datetime.now().isoformat(),
                        "expiry_date": None
                    }
                    if create_announcement(announcement_data):
                        st.success("Announcement published successfully!")
                        st.rerun()
                else:
                    st.error("Please fill in both title and message")
    
    st.divider()
    
    # Existing announcements
    st.subheader("Existing Announcements")
    announcements = db.load_data("announcements.json")
    
    if announcements:
        for announcement in announcements:
            with st.container():
                priority = announcement.get('priority', 'medium')
                emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                st.write(f"{emoji} **{announcement['title']}**")
                st.write(announcement['message'])
                st.caption(f"By {announcement.get('author', 'Admin')} • {announcement['created_date'][:10]}")
                st.divider()
    else:
        st.info("No announcements created yet.")

def show_club_management():
    st.title("👥 Club Management")
    
    clubs = get_clubs()
    requests = db.load_data("club_requests.json")
    pending_requests = [r for r in requests if r.get('status') == 'pending']
    
    # Pending requests
    if pending_requests:
        st.subheader("📥 Pending Join Requests")
        for request in pending_requests:
            with st.container():
                student_email = request['student_email']
                club_id = request['club_id']
                club = clubs.get(club_id, {})
                
                students = db.load_data("students.json")
                student = students.get(student_email, {})
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{student.get('name', student_email)}**")
                    st.caption(f"Wants to join: **{club.get('name', 'Unknown Club')}**")
                
                with col2:
                    st.write(f"Major: {student.get('major', 'N/A')}")
                    st.write(f"Year: {student.get('year', 'N/A')}")
                
                with col3:
                    if st.button("Approve", key=f"approve_{request['id']}"):
                        if approve_club_request(request['id'], club_id, student_email):
                            st.success("Request approved!")
                            st.rerun()
                
                st.divider()
    else:
        st.info("No pending club join requests.")
    
    # Club details
    st.subheader("🏢 Club Details")
    for club_id, club in clubs.items():
        with st.expander(f"{club['name']} - {len(club.get('members', []))} members"):
            st.write(f"**Description:** {club['description']}")
            st.write(f"**Schedule:** {club.get('meeting_schedule', 'Not set')}")
            st.write(f"**Location:** {club.get('location', 'Not set')}")
            
            members = club.get('members', [])
            if members:
                st.write("**Members:**")
                for member_email in members:
                    students = db.load_data("students.json")
                    student = students.get(member_email, {})
                    st.write(f"• {student.get('name', member_email)}")
            else:
                st.write("No members yet")

def show_confession_management():
    st.title("🗣️ Confession Management")
    
    confessions = get_confessions_for_admin()
    pending_confessions = [c for c in confessions if not c.get('is_approved', False)]
    
    # Pending approval
    if pending_confessions:
        st.subheader("⏳ Pending Approval")
        for confession in pending_confessions:
            with st.container():
                st.write(f"**{confession['category']}**")
                st.write(confession['text'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"approve_{confession['id']}"):
                        # Approve confession
                        confessions_data = db.load_data("confessions.json")
                        for conf in confessions_data:
                            if conf['id'] == confession['id']:
                                conf['is_approved'] = True
                                break
                        db.save_data("confessions.json", confessions_data)
                        st.success("Confession approved!")
                        st.rerun()
                
                with col2:
                    if st.button("Delete", key=f"delete_{confession['id']}"):
                        # Delete confession
                        confessions_data = [c for c in db.load_data("confessions.json") if c['id'] != confession['id']]
                        db.save_data("confessions.json", confessions_data)
                        st.success("Confession deleted!")
                        st.rerun()
                
                st.divider()
    else:
        st.info("No confessions pending approval.")
    
    # Approved confessions
    st.subheader("✅ Approved Confessions")
    approved_confessions = [c for c in confessions if c.get('is_approved', False)]
    
    if approved_confessions:
        for confession in approved_confessions:
            with st.container():
                st.write(f"**{confession['category']}**")
                st.write(confession['text'])
                
                likes_count = len(confession.get('likes', []))
                comments_count = len(confession.get('comments', []))
                
                st.caption(f"❤️ {likes_count} likes • 💬 {comments_count} comments • Posted on {confession['created_date'][:10]}")
                
                if st.button("Delete", key=f"del_{confession['id']}"):
                    confessions_data = [c for c in db.load_data("confessions.json") if c['id'] != confession['id']]
                    db.save_data("confessions.json", confessions_data)
                    st.success("Confession deleted!")
                    st.rerun()
                
                st.divider()
    else:
        st.info("No approved confessions yet.")

if __name__ == "__main__":
    main()
