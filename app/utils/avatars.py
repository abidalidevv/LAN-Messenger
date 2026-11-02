"""20 Prebuilt Stylish Avatars for LAN Messenger."""

AVATARS = [
    {"id": "gamer", "icon": "🎮", "name": "Gamer", "bg": "#5c6bc0"},
    {"id": "coder", "icon": "💻", "name": "Developer", "bg": "#00897b"},
    {"id": "rocket", "icon": "🚀", "name": "Astronaut", "bg": "#e53935"},
    {"id": "lion", "icon": "🦁", "name": "Lion", "bg": "#fb8c00"},
    {"id": "fox", "icon": "🦊", "name": "Fox", "bg": "#f4511e"},
    {"id": "panda", "icon": "🐼", "name": "Panda", "bg": "#424242"},
    {"id": "cool", "icon": "🕶️", "name": "Cool", "bg": "#1e88e5"},
    {"id": "crown", "icon": "👑", "name": "VIP", "bg": "#fbc02d"},
    {"id": "robot", "icon": "🤖", "name": "Bot", "bg": "#7cb342"},
    {"id": "star", "icon": "⭐", "name": "Star", "bg": "#ffb300"},
    {"id": "music", "icon": "🎧", "name": "Beats", "bg": "#8e24aa"},
    {"id": "diamond", "icon": "💎", "name": "Gem", "bg": "#00acc1"},
    {"id": "eagle", "icon": "🦅", "name": "Eagle", "bg": "#6d4c41"},
    {"id": "tiger", "icon": "🐯", "name": "Tiger", "bg": "#d81b60"},
    {"id": "cat", "icon": "🐱", "name": "Kitty", "bg": "#ff7043"},
    {"id": "lightning", "icon": "⚡", "name": "Bolt", "bg": "#fdd835"},
    {"id": "coffee", "icon": "☕", "name": "Cafe", "bg": "#795548"},
    {"id": "target", "icon": "🎯", "name": "Ace", "bg": "#c62828"},
    {"id": "shield", "icon": "🛡️", "name": "Guardian", "bg": "#2e7d32"},
    {"id": "ghost", "icon": "👻", "name": "Phantom", "bg": "#7e57c2"},
]

AVATAR_MAP = {a["id"]: a for a in AVATARS}


def get_avatar(avatar_id: str) -> dict:
    return AVATAR_MAP.get(avatar_id, AVATARS[0])

