import dropbox
from dotenv import load_dotenv
import os

load_dotenv()

TEAM_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

dbx = dropbox.DropboxTeam(TEAM_ACCESS_TOKEN)

# Get list of team members
members = dbx.team_members_list_v2(limit=100)

for member in members.members:
    profile = member.profile
    print("Name:", profile.name.display_name)
    print("Email:", profile.email)
    print("Team Member ID:", profile.team_member_id)
    print("-" * 40)