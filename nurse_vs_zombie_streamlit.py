
import streamlit as st
import random
from PIL import Image

# Set page config
st.set_page_config(page_title="Nurse vs Zombie", layout="centered")

# Initialize session state
if "difficulty" not in st.session_state:
    st.session_state.difficulty = None
    st.session_state.nurse = None
    st.session_state.zombie = None
    st.session_state.log = []
    st.session_state.game_over = False

# Character classes
class Character:
    def __init__(self, name, max_hp, dmin, dmax):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.dmin = dmin
        self.dmax = dmax

    def attack(self, target):
        dmg = random.randint(self.dmin, self.dmax)
        target.hp = max(target.hp - dmg, 0)
        return dmg

class Nurse(Character):
    def __init__(self):
        super().__init__("Nurse", 100, 10, 20)
        self.heals = 3
        self.heal_amt = 25
        self.specials = 2
        self.smin, self.smax = 30, 50
        self.inventory = {"Medkit":1, "Syringe":2}
        self.item_vals = {"Medkit":50, "Syringe":15}

    def heal(self):
        if self.heals <= 0: return 0
        self.heals -= 1
        self.hp = min(self.hp + self.heal_amt, self.max_hp)
        return self.heal_amt

    def special(self, target):
        if self.specials <= 0: return 0
        self.specials -= 1
        dmg = random.randint(self.smin, self.smax)
        target.hp = max(target.hp - dmg, 0)
        return dmg

    def use_item(self, item):
        if self.inventory.get(item, 0) <= 0: return 0
        self.inventory[item] -= 1
        heal = self.item_vals[item]
        self.hp = min(self.hp + heal, self.max_hp)
        return heal

class Zombie(Character): pass

# Game setup
def setup_game(level):
    params = {"Easy":(80,10,15), "Medium":(120,15,25), "Hard":(150,20,30)}[level]
    st.session_state.difficulty = level
    st.session_state.nurse = Nurse()
    st.session_state.zombie = Zombie("Zombie", *params)
    st.session_state.log = []
    st.session_state.game_over = False

def log_msg(msg):
    st.session_state.log.append(msg)

def reset_game():
    st.session_state.difficulty = None
    st.session_state.game_over = False

# Game rendering
def render_game():
    nurse = st.session_state.nurse
    zombie = st.session_state.zombie

    st.markdown(f"### Wave 1")
    st.markdown(f"**Nurse: {nurse.hp}/{nurse.max_hp} HP**")
    st.progress(nurse.hp / nurse.max_hp)

    st.markdown(f"**Zombie: {zombie.hp}/{zombie.max_hp} HP**")
    st.progress(zombie.hp / zombie.max_hp)

    st.markdown(f"Heals left: {nurse.heals} | Specials: {nurse.specials}")
    inventory = ', '.join(f"{k}×{v}" for k, v in nurse.inventory.items())
    st.markdown(f"Inventory: {inventory}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Attack"):
            dmg = nurse.attack(zombie)
            log_msg(f"You attacked the zombie for {dmg} damage.")
            zombie_turn()
    with col2:
        if st.button("Heal"):
            h = nurse.heal()
            log_msg(f"You healed for {h} HP." if h else "No heals left!")
            zombie_turn()
    with col3:
        if st.button("Special", disabled=nurse.specials <= 0):
            s = nurse.special(zombie)
            log_msg(f"Special attack! You did {s} damage.")
            zombie_turn()
    with col4:
        item = st.selectbox("Use Item", [i for i, v in nurse.inventory.items() if v > 0], key="item_use")
        if st.button("Use Item"):
            healed = nurse.use_item(item)
            log_msg(f"You used {item} and healed {healed} HP.")
            zombie_turn()

    st.markdown("### Battle Log")
    for entry in reversed(st.session_state.log[-8:]):
        st.write(entry)

    if nurse.hp <= 0 or zombie.hp <= 0:
        st.session_state.game_over = True
        winner = "💀 YOU DIED" if nurse.hp <= 0 else "🎉 YOU WIN"
        st.markdown(f"## {winner}")
        st.button("Restart", on_click=reset_game)

def zombie_turn():
    if st.session_state.zombie.hp <= 0: return
    d = st.session_state.zombie.attack(st.session_state.nurse)
    log_msg(f"Zombie attacks you for {d} damage.")

# UI
st.markdown("## 🩺 Nurse vs 🧟 Zombie")
if st.session_state.difficulty is None:
    st.markdown("### Choose difficulty")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Easy"): setup_game("Easy")
    with col2:
        if st.button("Medium"): setup_game("Medium")
    with col3:
        if st.button("Hard"): setup_game("Hard")
else:
    render_game()
