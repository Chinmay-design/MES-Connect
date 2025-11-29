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
    if 'current_chat' not in st.session_state:
        st.session_state.current_chat = None
    if 'start_call_with' not in st.session_state:
        st.session_state.start_call_with = None
    if 'active_call' not in st.session_state:
        st.session_state.active_call = None
    if 'show_forgot_password' not in st.session_state:
        st.session_state.show_forgot_password = False
    if 'show_announcement_form' not in st.session_state:
        st.session_state.show_announcement_form = False
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    
    # Show login if not authenticated
    if not st.session_state.user:
        login_page()
    else:
        show_app()

def show_app():
    """Show the main application based on user role"""
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("# 🎓 Campus Connect")
        st.write(f"**Welcome, {st.session_state.user.get('name', 'User')}**")
        st.write(f"🔹 {st.session_state.role.title()}")
        
        if st.session_state.role == 'student':
            st.write(f"📚 {st.session_state.user.get('major', 'Student')}")
            show_student_navigation()
        else:
            st.write("⚡ Administrator")
            show_admin_navigation()
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()

def show_student_navigation():
    """Student navigation menu"""
    pages = {
        "🏠 Home": "Home",
        "👤 Profile": "Profile", 
        "📢 Announcements": "Announcements",
        "👥 Clubs": "Clubs",
        "💬 Chat": "Chat",
        "📞 Calls": "Calls",
        "🗣️ Confessions": "Confessions"
    }
    
    selected = st.radio("Navigate to:", list(pages.keys()))
    st.session_state.page = pages[selected]
    
    # Display the selected page
    show_page()

def show_admin_navigation():
    """Admin navigation menu"""
    pages = {
        "📊 Dashboard": "Dashboard",
        "👥 User Management": "UserManagement",
        "📢 Announcements": "AnnouncementManagement", 
        "👥 Club Management": "ClubManagement",
        "🗣️ Confessions": "ConfessionManagement",
        "💬 Chat": "Chat",
        "📞 Calls": "Calls"
    }
    
    selected = st.radio("Admin Tools:", list(pages.keys()))
    st.session_state.page = pages[selected]
    
    # Display the selected page
    show_page()

def show_page():
    """Display the current page based on session state"""
    page = st.session_state.page
    
    if st.session_state.role == 'student':
        if page == "Home":
            show_student_home()
        elif page == "Profile":
            show_student_profile()
        elif page == "Announcements":
            show_announcements()
        elif page == "Clubs":
            show_clubs()
        elif page == "Chat":
            show_chat()
        elif page == "Calls":
            show_calls()
        elif page == "Confessions":
            show_confessions()
    else:  # Admin
        if page == "Dashboard":
            show_admin_dashboard()
        elif page == "UserManagement":
            show_user_management()
        elif page == "AnnouncementManagement":
            show_announcement_management()
        elif page == "ClubManagement":
            show_club_management()
        elif page == "ConfessionManagement":
            show_confessions_management()
        elif page == "Chat":
            show_chat()
        elif page == "Calls":
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
            st.session_state.page = "Chat"
            st.rerun()
    
    with col2:
        if st.button("📞 Call Admin", use_container_width=True):
            st.session_state.start_call_with = "MES.edu"
            st.session_state.page = "Calls"
            st.rerun()
    
    with col3:
        if st.button("🗣️ Share Confession", use_container_width=True):
            st.session_state.page = "Confessions"
            st.rerun()
    
    with col4:
        if st.button("👥 Browse Clubs", use_container_width=True):
            st.session_state.page = "Clubs"
            st.rerun()
    
    st.divider()
    
    # Recent confessions preview
    st.subheader("💭 Recent Campus Confessions")
    confessions = get_confessions_for_students()
    recent_confessions = [c for c in confessions if c.get('is_approved', True)][-2:]
    
    if recent_confessions:
        for confession in recent_confessions:
            with st.container():
                category_emoji = confession.get('category', '💭 General').split(' ')[0]
                st.write(f"**{category_emoji} {confession.get('category', 'General')}**")
                st.caption("👤 Anonymous")
                
                confession_text = confession.get('text', '')
                if len(confession_text) > 100:
                    st.write(confession_text[:100] + "...")
                else:
                    st.write(confession_text)
                
                likes = get_likes_count(confession)
                comments = len(get_comments_for_students(confession))
                st.caption(f"❤️ {likes} likes • 💬 {comments} comments")
                
                if st.button("Read More", key=f"read_more_{confession['id']}"):
                    st.session_state.page = "Confessions"
                    st.rerun()
                
                st.divider()
    else:
        st.info("No confessions yet. Be the first to share your thoughts!")
    
    st.divider()
    
    # Recent announcements
    st.subheader("📢 Recent Announcements")
    announcements = db.load_data("announcements.json")[-3:]
    for announcement in announcements:
        with st.container():
            priority = announcement.get('priority', 'medium')
            emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
            st.write(f"{emoji} **{announcement.get('title', 'No Title')}**")
            st.write(announcement.get('message', '')[:100] + "..." if len(announcement.get('message', '')) > 100 else announcement.get('message', ''))
            st.caption(f"By {announcement.get('author', 'Admin')} • {announcement.get('created_date', '')[:10]}")
            st.divider()

def show_student_profile():
    st.title("👤 Your Profile")
    user = st.session_state.user
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Year:** {user.get('year', 'Not set')}")
        st.write(f"**Major:** {user.get('major', 'Not set')}")
        st.write(f"**Member since:** {user.get('joined_date', 'Today')[:10]}")
    
    with col2:
        # Clubs joined
        clubs = get_clubs()
        user_clubs = [club for club in clubs.values() if st.session_state.user['email'] in club.get('members', [])]
        st.write("**Clubs Joined:**")
        if user_clubs:
            for club in user_clubs:
                st.write(f"• {club['name']}")
        else:
            st.write("No clubs joined yet")

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
        st.info("No announcements yet.")

def show_clubs():
    st.title("👥 Campus Clubs")
    
    clubs = get_clubs()
    current_user = st.session_state.user['email']
    
    categories = {
        "technology": "💻 Technology",
        "debate": "🗣️ Debate", 
        "arts": "🎨 Arts",
        "sports": "🏀 Sports",
        "science": "🔬 Science"
    }
    
    for club_id, club in clubs.items():
        with st.container():
            category_emoji = categories.get(club.get('category', 'general'), '👥')
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{category_emoji} {club['name']}**")
                st.write(club['description'])
                st.caption(f"👥 {len(club.get('members', []))} members • 📅 {club.get('meeting_schedule', 'Schedule TBA')}")
            
            with col2:
                if current_user in club.get('members', []):
                    st.success("✅ Joined")
                elif current_user in club.get('pending_requests', []):
                    st.info("⏳ Pending Approval")
                else:
                    if st.button("Request to Join", key=f"join_{club_id}"):
                        if join_club_request(current_user, club_id):
                            st.success("Join request sent! Waiting for admin approval.")
                            st.rerun()
            
            st.divider()

def show_chat():
    st.title("💬 Campus Chat")
    
    if st.session_state.current_chat:
        show_chat_messages()
    else:
        show_chat_list()

def show_chat_list():
    st.subheader("Start a Conversation")
    
    if st.session_state.role == 'student':
        show_student_chat_list()
    else:
        show_admin_chat_list()

def show_student_chat_list():
    current_user = st.session_state.user['email']
    
    # Chat with Admin
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("**👑 Campus Administrator**")
        st.caption("Get help with platform issues, club approvals, and general inquiries")
    with col2:
        if st.button("Message Admin", key="msg_admin"):
            chat_id = create_chat(current_user, "MES.edu")
            st.session_state.current_chat = chat_id
            st.rerun()
    st.divider()
    
    # Chat with other students
    students = db.load_data("students.json")
    for email, student in students.items():
        if email != current_user:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{student['name']}**")
                st.caption(f"{student.get('major', 'Student')} • {student.get('year', '')}")
            with col2:
                if st.button("Message", key=f"msg_{email}"):
                    chat_id = create_chat(current_user, email)
                    st.session_state.current_chat = chat_id
                    st.rerun()
            st.divider()

def show_admin_chat_list():
    students = db.load_data("students.json")
    
    for email, student in students.items():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.write(f"**{student['name']}**")
            st.caption(f"{student.get('major', 'Student')} • {student.get('year', '')}")
        
        with col2:
            clubs = get_clubs()
            user_clubs = [club for club in clubs.values() if email in club.get('members', [])]
            st.caption(f"Clubs: {len(user_clubs)}")
        
        with col3:
            if st.button("💬 Chat", key=f"chat_{email}"):
                chat_id = create_chat("MES.edu", email)
                st.session_state.current_chat = chat_id
                st.rerun()
            if st.button("📞 Call", key=f"call_{email}"):
                st.session_state.start_call_with = email
                st.session_state.page = "Calls"
                st.rerun()
        
        st.divider()

def show_chat_messages():
    chat_id = st.session_state.current_chat
    messages = get_chat_messages(chat_id)
    
    # Display messages
    st.subheader("Chat Messages")
    for msg in messages:
        if msg['sender'] == st.session_state.user['email']:
            st.write(f"**You:** {msg['message']}")
            st.caption(f"Sent at {msg['timestamp'][11:16]}")
        else:
            sender_name = "Admin" if msg['sender'] == "MES.edu" else msg['sender']
            st.write(f"**{sender_name}:** {msg['message']}")
            st.caption(f"Sent at {msg['timestamp'][11:16]}")
    
    # Message input
    st.divider()
    new_message = st.text_input("Type your message...")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if st.button("Send") and new_message.strip():
            send_message(chat_id, st.session_state.user['email'], new_message.strip())
            st.rerun()
    
    with col2:
        if st.button("← Back"):
            st.session_state.current_chat = None
            st.rerun()

def show_calls():
    st.title("📞 Calls")
    
    if st.session_state.get('start_call_with'):
        show_call_interface()
    elif st.session_state.get('active_call'):
        show_active_call()
    else:
        show_call_history()

def show_call_history():
    user_email = st.session_state.user['email']
    calls = get_user_calls(user_email)
    
    st.subheader("Call History")
    
    if calls:
        for call in calls[-10:]:
            with st.container():
                participants = call.get('participants', [])
                other_participants = [p for p in participants if p != user_email]
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    if len(other_participants) == 1:
                        other_email = other_participants[0]
                        if other_email == "MES.edu":
                            st.write("**👑 Campus Administrator**")
                        else:
                            students = db.load_data("students.json")
                            student = students.get(other_email, {})
                            st.write(f"**{student.get('name', other_email)}**")
                    
                    st.caption(f"📅 {call.get('start_time', '')[:16]}")
                
                with col2:
                    call_type = "📹 Video" if call.get('type') == 'video' else "📞 Voice"
                    duration = call.get('duration', '0m')
                    st.write(f"{call_type} • {duration}")
                
                with col3:
                    status = call.get('status', 'ended')
                    if status == 'ended':
                        st.success("✅ Completed")
                    elif status == 'missed':
                        st.error("❌ Missed")
                    else:
                        st.info("🔄 Active")
                
                st.divider()
    else:
        st.info("No call history yet.")

def show_call_interface():
    target_email = st.session_state.start_call_with
    students = db.load_data("students.json")
    target_user = students.get(target_email, {"name": "User"})
    
    st.title(f"📞 Call {target_user['name']}")
    
    call_type = st.radio("Call Type:", ["📞 Voice Call", "📹 Video Call"])
    
    if st.session_state.role == 'admin':
        call_purpose = st.text_area("Call Purpose/Notes:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎤 Start Call", use_container_width=True, type="primary"):
            call_data = {
                "id": str(uuid.uuid4()),
                "participants": [st.session_state.user['email'], target_email],
                "type": "video" if "Video" in call_type else "voice",
                "start_time": datetime.now().isoformat(),
                "status": "active",
                "initiator": st.session_state.user['email'],
                "purpose": call_purpose if st.session_state.role == 'admin' else ""
            }
            create_call(call_data)
            st.session_state.active_call = call_data
            st.session_state.start_call_with = None
            st.rerun()
    
    with col2:
        if st.button("← Cancel", use_container_width=True):
            st.session_state.start_call_with = None
            st.rerun()

def show_active_call():
    call = st.session_state.active_call
    
    st.title("📞 Active Call")
    
    participants = call.get('participants', [])
    other_participants = [p for p in participants if p != st.session_state.user['email']]
    
    if other_participants:
        other_email = other_participants[0]
        if other_email == "MES.edu":
            st.write("**Talking with: 👑 Campus Administrator**")
        else:
            students = db.load_data("students.json")
            student = students.get(other_email, {})
            st.write(f"**Talking with: {student.get('name', other_email)}**")
    
    # Call controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎤 Mute", use_container_width=True):
            st.info("Microphone muted")
    
    with col2:
        if st.button("🔇 Silence", use_container_width=True):
            st.info("Audio silenced")
    
    with col3:
        if call.get('type') == 'video':
            if st.button("📹 Stop Video", use_container_width=True):
                st.info("Video stopped")
    
    with col4:
        if st.button("📞 End Call", use_container_width=True, type="primary"):
            update_call_status(call['id'], 'ended')
            st.session_state.active_call = None
            st.success("Call ended successfully")
            st.rerun()
    
    # Simulated call duration
    st.write("---")
    st.write("**Call in progress...** ⏱️")
    
    if st.button("← Back to Calls"):
        st.session_state.active_call = None
        st.rerun()

def show_confessions():
    st.title("🗣️ Campus Confessions")
    
    tab1, tab2 = st.tabs(["📝 Share Confession", "💭 View Confessions"])
    
    with tab1:
        with st.form("confession_form"):
            category = st.selectbox("Category", 
                                  ["💭 General", "💕 Relationships", "📚 Academics", 
                                   "😔 Regrets", "🎉 Achievements", "🤔 Advice"])
            confession_text = st.text_area("Your Confession", height=150, 
                                         placeholder="Share your thoughts anonymously...")
            
            if st.form_submit_button("Share Confession", use_container_width=True):
                if confession_text.strip():
                    confession_data = {
                        "id": str(uuid.uuid4()),
                        "text": confession_text.strip(),
                        "category": category,
                        "user_email": st.session_state.user['email'],
                        "created_date": datetime.now().isoformat(),
                        "is_approved": True if st.session_state.role == 'admin' else False,
                        "likes": [],
                        "comments": []
                    }
                    
                    if create_confession(confession_data):
                        st.success("Confession shared successfully! 🎉")
                        if st.session_state.role == 'student':
                            st.info("Your confession is pending admin approval.")
                        st.rerun()
                else:
                    st.error("Please write your confession")
    
    with tab2:
        confessions = get_confessions_for_students()
        approved_confessions = [c for c in confessions if c.get('is_approved', True)]
        
        if approved_confessions:
            for confession in approved_confessions:
                with st.container():
                    st.write(f"**{confession.get('category', 'General')}**")
                    st.write(confession.get('text', ''))
                    
                    # Likes and comments
                    likes_count = get_likes_count(confession)
                    comments = get_comments_for_students(confession)
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        if st.button(f"❤️ {likes_count}", key=f"like_{confession['id']}"):
                            if like_confession(confession['id'], st.session_state.user['email']):
                                st.success("Liked!")
                                st.rerun()
                    
                    with col2:
                        if st.button(f"💬 {len(comments)}", key=f"comment_btn_{confession['id']}"):
                            st.session_state[f"show_comments_{confession['id']}"] = True
                    
                    with col3:
                        st.caption(f"Posted {confession.get('created_date', '')[:10]}")
                    
                    # Comments section
                    if st.session_state.get(f"show_comments_{confession['id']}"):
                        st.divider()
                        st.write("**Comments:**")
                        
                        for comment in comments:
                            st.write(f"👤 **Anonymous:** {comment.get('text', '')}")
                            st.caption(f"Posted {comment.get('created_date', '')[:10]}")
                        
                        # Add comment
                        with st.form(f"add_comment_{confession['id']}"):
                            new_comment = st.text_input("Add a comment...")
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
                        
                        if st.button("Hide Comments", key=f"hide_{confession['id']}"):
                            st.session_state[f"show_comments_{confession['id']}"] = False
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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📢 Create Announcement", use_container_width=True):
            st.session_state.page = "AnnouncementManagement"
            st.rerun()
    
    with col2:
        if st.button("👥 Manage Clubs", use_container_width=True):
            st.session_state.page = "ClubManagement"
            st.rerun()
    
    with col3:
        if st.button("🗣️ Review Confessions", use_container_width=True):
            st.session_state.page = "ConfessionManagement"
            st.rerun()
    
    with col4:
        if st.button("📞 Call Student", use_container_width=True):
            st.session_state.page = "Calls"
            st.rerun()
    
    st.divider()
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    # Recent club requests
    requests = db.load_data("club_requests.json")
    pending_requests = [r for r in requests if r.get('status') == 'pending']
    
    if pending_requests:
        st.write(f"**Pending Club Requests:** {len(pending_requests)}")
        for request in pending_requests[-3:]:
            st.write(f"• {request['student_email']} wants to join club")
    else:
        st.write("**Pending Club Requests:** 0")
    
    st.divider()
    
    # Recent confessions needing approval
    confessions = get_confessions_for_admin()
    pending_confessions = [c for c in confessions if not c.get('is_approved', False)]
    
    if pending_confessions:
        st.write(f"**Confessions Pending Approval:** {len(pending_confessions)}")
        for confession in pending_confessions[-2:]:
            st.write(f"• New confession in {confession.get('category', 'General')}")
    else:
        st.write("**Confessions Pending Approval:** 0")

def show_user_management():
    st.title("👥 User Management")
    students = db.load_data("students.json")
    
    if students:
        st.subheader(f"Total Students: {len(students)}")
        
        for email, student in students.items():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{student['name']}**")
                    st.caption(f"{email}")
                
                with col2:
                    st.write(f"**Major:** {student.get('major', 'N/A')}")
                    st.write(f"**Year:** {student.get('year', 'N/A')}")
                
                with col3:
                    clubs = get_clubs()
                    user_clubs = [club for club in clubs.values() if email in club.get('members', [])]
                    st.write(f"**Clubs Joined:** {len(user_clubs)}")
                    if user_clubs:
                        club_names = [club['name'] for club in user_clubs[:2]]
                        st.caption(", ".join(club_names))
                
                with col4:
                    if st.button("View", key=f"view_{email}"):
                        st.session_state.viewing_student = email
                
                st.divider()
    else:
        st.info("No students registered yet.")

def show_announcement_management():
    st.title("📢 Announcement Management")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("➕ Create New Announcement", use_container_width=True):
            st.session_state.show_announcement_form = True
    
    # Announcement form
    if st.session_state.get('show_announcement_form'):
        st.subheader("Create New Announcement")
        with st.form("announcement_form"):
            title = st.text_input("Title")
            message = st.text_area("Message", height=150)
            category = st.selectbox("Category", ["general", "events", "academic", "urgent"])
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Publish Announcement", use_container_width=True):
                    if title and message:
                        announcement_data = {
                            "id": str(uuid.uuid4()),
                            "title": title,
                            "message": message,
                            "category": category,
                            "priority": priority,
                            "author": st.session_state.user['name'],
                            "created_date": datetime.now().isoformat(),
                            "expiry_date": None
                        }
                        if create_announcement(announcement_data):
                            st.success("Announcement published!")
                            st.session_state.show_announcement_form = False
                            st.rerun()
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_announcement_form = False
                    st.rerun()
    
    st.divider()
    
    # Existing announcements
    st.subheader("Existing Announcements")
    announcements = db.load_data("announcements.json")
    
    if announcements:
        for announcement in announcements:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    priority = announcement.get('priority', 'medium')
                    emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                    st.write(f"{emoji} **{announcement.get('title', 'No Title')}**")
                    st.write(announcement.get('message', ''))
                    st.caption(f"By {announcement.get('author', 'Admin')} • {announcement.get('created_date', '')[:10]}")
                
                with col2:
                    if st.button("Delete", key=f"del_{announcement['id']}"):
                        # Implementation for deleting announcements
                        st.warning("Delete functionality to be implemented")
                
                st.divider()
    else:
        st.info("No announcements yet.")

def show_club_management():
    st.title("👥 Club Management")
    
    clubs = get_clubs()
    requests = db.load_data("club_requests.json")
    pending_requests = [r for r in requests if r.get('status') == 'pending']
    
    # Pending requests section
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
                    st.caption(f"Requested: {request.get('request_date', '')[:10]}")
                
                with col2:
                    st.write(f"Major: {student.get('major', 'N/A')}")
                    st.write(f"Year: {student.get('year', 'N/A')}")
                
                with col3:
                    if st.button("✅ Approve", key=f"approve_{request['id']}"):
                        if approve_club_request(request['id'], club_id, student_email):
                            st.success("Request approved!")
                            st.rerun()
                
                st.divider()
    else:
        st.info("No pending club requests.")
    
    # Club management section
    st.subheader("🏢 Manage Clubs")
    for club_id, club in clubs.items():
        with st.expander(f"📋 {club['name']} - {len(club.get('members', []))} members"):
            st.write(f"**Description:** {club['description']}")
            st.write(f"**Meeting Schedule:** {club.get('meeting_schedule', 'Not set')}")
            st.write(f"**Location:** {club.get('location', 'Not set')}")
            
            # Members list
            members = club.get('members', [])
            if members:
                st.write("**Members:**")
                for member_email in members:
                    students = db.load_data("students.json")
                    student = students.get(member_email, {})
                    st.write(f"• {student.get('name', member_email)}")
            else:
                st.write("**Members:** No members yet")
            
            # Pending requests for this club
            club_pending = [r for r in pending_requests if r['club_id'] == club_id]
            if club_pending:
                st.write("**Pending Requests:**")
                for request in club_pending:
                    student_email = request['student_email']
                    students = db.load_data("students.json")
                    student = students.get(student_email, {})
                    st.write(f"• {student.get('name', student_email)}")

def show_confessions_management():
    st.title("🗣️ Confessions Management")
    
    confessions = get_confessions_for_admin()
    pending_confessions = [c for c in confessions if not c.get('is_approved', False)]
    
    # Pending confessions for approval
    if pending_confessions:
        st.subheader("⏳ Pending Approval")
        for confession in pending_confessions:
            with st.container():
                st.write(f"**{confession.get('category', 'General')}**")
                st.write(confession.get('text', ''))
                st.caption(f"Submitted: {confession.get('created_date', '')[:10]}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve", key=f"approve_conf_{confession['id']}"):
                        # Update confession approval status
                        confessions = db.load_data("confessions.json")
                        for conf in confessions:
                            if conf['id'] == confession['id']:
                                conf['is_approved'] = True
                                break
                        db.save_data("confessions.json", confessions)
                        st.success("Confession approved!")
                        st.rerun()
                with col2:
                    if st.button("❌ Reject", key=f"reject_conf_{confession['id']}"):
                        # Remove confession
                        confessions = db.load_data("confessions.json")
                        confessions = [conf for conf in confessions if conf['id'] != confession['id']]
                        db.save_data("confessions.json", confessions)
                        st.success("Confession rejected!")
                        st.rerun()
                st.divider()
    else:
        st.info("No confessions pending approval.")
    
    # All confessions
    st.subheader("📋 All Confessions")
    approved_confessions = [c for c in confessions if c.get('is_approved', False)]
    
    if approved_confessions:
        for confession in approved_confessions:
            with st.container():
                st.write(f"**{confession.get('category', 'General')}**")
                st.write(confession.get('text', ''))
                st.caption(f"Posted: {confession.get('created_date', '')[:10]}")
                
                likes = get_likes_count(confession)
                comments = len(confession.get('comments', []))
                st.caption(f"❤️ {likes} likes • 💬 {comments} comments")
                
                if st.button("Delete", key=f"del_conf_{confession['id']}"):
                    # Remove confession
                    confessions = db.load_data("confessions.json")
                    confessions = [conf for conf in confessions if conf['id'] != confession['id']]
                    db.save_data("confessions.json", confessions)
                    st.success("Confession deleted!")
                    st.rerun()
                
                st.divider()
    else:
        st.info("No approved confessions yet.")

if __name__ == "__main__":
    main()
