import json
import os
import bcrypt
import uuid
from datetime import datetime

class SimpleDB:
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.init_default_data()
    
    def init_default_data(self):
        """Initialize with default admin and sample data"""
        # Admin account
        admin_data = {
            "MES.edu": {
                "password": bcrypt.hashpw("education".encode(), bcrypt.gensalt()).decode(),
                "role": "admin",
                "name": "Admin User"
            }
        }
        
        # Sample clubs
        sample_clubs = {
            "club_cs": {
                "id": "club_cs",
                "name": "Computer Science Club",
                "category": "technology",
                "description": "Weekly coding sessions, hackathon preparation, and tech workshops. Open to all skill levels!",
                "members": [],
                "pending_requests": [],
                "admins": ["MES.edu"],
                "meeting_schedule": "Wednesdays 6-8 PM",
                "location": "Tech Building 301",
                "created_date": datetime.now().isoformat()
            },
            "club_debate": {
                "id": "club_debate",
                "name": "Debate Society",
                "category": "debate",
                "description": "Improve your public speaking and critical thinking skills through weekly debates and tournaments.",
                "members": [],
                "pending_requests": [],
                "admins": ["MES.edu"],
                "meeting_schedule": "Fridays 4-6 PM",
                "location": "Humanities Building 204",
                "created_date": datetime.now().isoformat()
            },
            "club_music": {
                "id": "club_music",
                "name": "Music Club",
                "category": "arts",
                "description": "For musicians and music lovers. Jam sessions, performances, and collaborative projects.",
                "members": [],
                "pending_requests": [],
                "admins": ["MES.edu"],
                "meeting_schedule": "Tuesdays 7-9 PM",
                "location": "Arts Center Room 101",
                "created_date": datetime.now().isoformat()
            }
        }
        
        # Sample announcements
        sample_announcements = [
            {
                "id": str(uuid.uuid4()),
                "title": "Welcome to Campus Connect!",
                "message": "Welcome to our new campus social platform! Connect with fellow students, join clubs, and stay updated with campus events.",
                "category": "general",
                "priority": "high",
                "author": "Admin User",
                "created_date": datetime.now().isoformat(),
                "expiry_date": None
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Hackathon 2024 Registration Open",
                "message": "Annual coding competition is here! Form teams of 2-4 and showcase your skills. Prizes include cash awards and internships.",
                "category": "events",
                "priority": "medium",
                "author": "Admin User", 
                "created_date": datetime.now().isoformat(),
                "expiry_date": None
            }
        ]
        
        # Ensure files exist with default data
        default_data = {
            "users.json": admin_data,
            "students.json": {},
            "announcements.json": sample_announcements,
            "clubs.json": sample_clubs,
            "club_requests.json": [],
            "chats.json": {},
            "calls.json": [],
            "confessions.json": []
        }
        
        for filename, data in default_data.items():
            if not os.path.exists(os.path.join(self.data_dir, filename)):
                self.save_data(filename, data)
    
    def load_data(self, filename):
        """Load data from JSON file"""
        try:
            with open(os.path.join(self.data_dir, filename), 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if filename.endswith('.json') and not filename.endswith('announcements.json') else []
    
    def save_data(self, filename, data):
        """Save data to JSON file"""
        with open(os.path.join(self.data_dir, filename), 'w') as f:
            json.dump(data, f, indent=2)

# Global database instance
db = SimpleDB()

# User Management Functions
def get_user_by_email(email):
    users = db.load_data("users.json")
    students = db.load_data("students.json")
    return users.get(email) or students.get(email)

def create_student(student_data):
    students = db.load_data("students.json")
    students[student_data['email']] = student_data
    db.save_data("students.json", students)
    return True

def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False

# Announcement Functions
def create_announcement(announcement_data):
    announcements = db.load_data("announcements.json")
    announcements.append(announcement_data)
    db.save_data("announcements.json", announcements)
    return True

def get_announcements():
    return db.load_data("announcements.json")

# Club Functions
def get_clubs():
    return db.load_data("clubs.json")

def join_club_request(student_email, club_id):
    clubs = db.load_data("clubs.json")
    if club_id in clubs:
        if student_email not in clubs[club_id]["pending_requests"]:
            clubs[club_id]["pending_requests"].append(student_email)
            db.save_data("clubs.json", clubs)
            
            requests = db.load_data("club_requests.json")
            requests.append({
                "id": str(uuid.uuid4()),
                "student_email": student_email,
                "club_id": club_id,
                "status": "pending",
                "request_date": datetime.now().isoformat()
            })
            db.save_data("club_requests.json", requests)
            return True
    return False

def approve_club_request(request_id, club_id, student_email):
    clubs = db.load_data("clubs.json")
    if club_id in clubs:
        if student_email in clubs[club_id]["pending_requests"]:
            clubs[club_id]["pending_requests"].remove(student_email)
        if student_email not in clubs[club_id]["members"]:
            clubs[club_id]["members"].append(student_email)
        db.save_data("clubs.json", clubs)
        
        requests = db.load_data("club_requests.json")
        for request in requests:
            if request.get("id") == request_id:
                request["status"] = "approved"
                request["processed_date"] = datetime.now().isoformat()
                break
        db.save_data("club_requests.json", requests)
        return True
    return False

# Chat Functions
def create_chat(user1, user2):
    chats = db.load_data("chats.json")
    chat_id = f"chat_{user1}_{user2}"
    if chat_id not in chats:
        chats[chat_id] = {
            "participants": [user1, user2],
            "messages": [],
            "created_date": datetime.now().isoformat()
        }
        db.save_data("chats.json", chats)
    return chat_id

def send_message(chat_id, sender, message):
    chats = db.load_data("chats.json")
    if chat_id in chats:
        chats[chat_id]["messages"].append({
            "id": str(uuid.uuid4()),
            "sender": sender,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        db.save_data("chats.json", chats)
        return True
    return False

def get_chat_messages(chat_id):
    chats = db.load_data("chats.json")
    return chats.get(chat_id, {}).get("messages", [])

# Call Functions
def create_call(call_data):
    calls = db.load_data("calls.json")
    calls.append(call_data)
    db.save_data("calls.json", calls)
    return True

def get_calls():
    return db.load_data("calls.json")

def get_user_calls(user_email):
    calls = db.load_data("calls.json")
    user_calls = []
    for call in calls:
        if user_email in call.get('participants', []):
            user_calls.append(call)
    return user_calls

def update_call_status(call_id, status):
    calls = db.load_data("calls.json")
    for call in calls:
        if call.get('id') == call_id:
            call['status'] = status
            if status == 'ended':
                call['end_time'] = datetime.now().isoformat()
            db.save_data("calls.json", calls)
            return True
    return False

# Confession Functions
def create_confession(confession_data):
    confessions = db.load_data("confessions.json")
    confession_data['anonymous_id'] = f"anon_{str(uuid.uuid4())[:8]}"
    confession_data['user_email'] = confession_data.pop('user_email', None)
    confessions.append(confession_data)
    db.save_data("confessions.json", confessions)
    return True

def get_confessions_for_students():
    confessions = db.load_data("confessions.json")
    student_view = []
    for confession in confessions:
        student_confession = confession.copy()
        student_confession.pop('user_email', None)
        student_view.append(student_confession)
    return student_view

def get_confessions_for_admin():
    return db.load_data("confessions.json")

def like_confession(confession_id, student_email):
    confessions = db.load_data("confessions.json")
    for confession in confessions:
        if confession.get('id') == confession_id:
            if 'likes' not in confession:
                confession['likes'] = []
            like_data = {
                'anonymous_id': f"anon_{str(uuid.uuid4())[:8]}",
                'user_email': student_email
            }
            confession['likes'].append(like_data)
            db.save_data("confessions.json", confessions)
            return True
    return False

def get_likes_count(confession):
    likes = confession.get('likes', [])
    return len(likes)

def add_comment(confession_id, comment_data, user_email):
    confessions = db.load_data("confessions.json")
    for confession in confessions:
        if confession.get('id') == confession_id:
            if 'comments' not in confession:
                confession['comments'] = []
            comment_data['anonymous_id'] = f"anon_{str(uuid.uuid4())[:8]}"
            comment_data['user_email'] = user_email
            confession['comments'].append(comment_data)
            db.save_data("confessions.json", confessions)
            return True
    return False

def get_comments_for_students(confession):
    comments = confession.get('comments', [])
    student_comments = []
    for comment in comments:
        student_comment = comment.copy()
        student_comment.pop('user_email', None)
        student_comments.append(student_comment)
    return student_comments
