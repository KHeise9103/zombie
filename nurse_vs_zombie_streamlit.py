# nurse_vs_zombie_streamlit.py
import streamlit as st
from PIL import Image
import random, os

# ─── Models ────────────────────────────────────────────────────────────────────

class Character:
    def __init__(self, name, max_hp, min_d, max_d):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.min_d, self.max_d = min_d, max_d

    def attack(self, other):
        dmg = random.randint(self.min_d, self.max_d)
        other.hp = max(other.hp - dmg, 0)
        return dmg

class Nurse(Character):
    def __init__(self):
        super().__init__("Nurse", 100, 10, 20)
        self.heals, self.heal_amt = 3, 25
        self.specials, (self.smin, self.smax) = 2, (30,50)
        self.inventory = {"Medkit":1, "Syringe":2}
        self.item_vals = {"Medkit":50, "Syringe":15}

    def heal_self(self):
        if self.heals <= 0: return 0
        self.heals -= 1
        amt = self.heal_amt
        self.hp = min(self.hp + amt, self.max_hp)
        return amt

    def special_attack(self, other):
        if self.specials <= 0: return 0
        self.specials -= 1
        dmg = random.randint(self.smin, self.smax)
        other.hp = max(other.hp - dmg, 0)
        return dmg

    def use_item(self, item):
        if self.inventory.get(item,0) <= 0: return 0
        self.inventory[item] -= 1
        amt = self.item_vals[item]
        self.hp = min(self.hp + amt, self.max_hp)
        return amt

class Zombie(Character): pass

# ─── State Helpers ─────────────────────────────────────────────────────────────

def init_state():
    """Initialize session state on first load."""
    if "started" not in st.session_state:
        st.session_state.started = False
        st.session_state.diff    = "Medium"
    if st.session_state.started:
        if "nurse" not in st.session_state:
            st.session_state.nurse  = Nurse()
        if "zombie" not in st.session_state:
            hp, dmin, dmax = DIFF_PARAMS[st.session_state.diff]
            st.session_state.zombie = Zombie("Zombie", hp, dmin, dmax)
        if "wave" not in st.session_state:
            st.session_state.wave   = 1

def reset_game(difficulty):
    """(Re)start the game at a given difficulty."""
    st.session_state.started = True
    st.session_state.diff    = difficulty
    st.session_state.nurse  = Nurse()
    hp, dmin, dmax = DIFF_PARAMS[difficulty]
    st.session_state.zombie = Zombie("Zombie", hp, dmin, dmax)
    st.session_state.wave   = 1

# ─── Image Loader ─────────────────────────────────────────────────────────────

def load_img(fn, width=None):
    img = Image.open(fn)
    if width:
        ratio = width / img.width
        img = img.resize((int(img.width*ratio), int(img.height*ratio)))
    return img

# ─── Constants ────────────────────────────────────────────────────────────────

DIFF_PARAMS = {
    "Easy":   (80, 10, 15),
    "Medium": (120,15,25),
    "Hard":   (150,20,30),
}

# ─── Streamlit Layout ─────────────────────────────────────────────────────────

st.set_page_config(page_title="Nurse vs Zombie", layout="wide")
st.title("🩺 Nurse vs 🧟 Zombie")

init_state()

# 1) Difficulty screen
if not st.session_state.started:
    choice = st.radio(
        "Choose difficulty", 
        options=list(DIFF_PARAMS.keys()), 
        index=list(DIFF_PARAMS.keys()).index(st.session_state.diff),
        horizontal=True
    )
    if st.button("Start Game"):
        reset_game(choice)
        st.experimental_rerun()
    st.stop()  # don't render the rest until they've started

# 2) Main battle UI
n = st.session_state.nurse
z = st.session_state.zombie

# Sprites & background
bg = load_img("background.png", width=600)
c1, c2, c3 = st.columns([1,2,1])
with c1:
    st.image(load_img("nurse.png", width=200), caption="Nurse", use_container_width=False)
with c2:
    st.image(bg, use_container_width=True)
with c3:
    st.image(load_img("zombie.png", width=200), caption="Zombie", use_container_width=False)

st.subheader(f"Wave {st.session_state.wave}")
# Health display
st.markdown(f"**Nurse:** {n.hp}/{n.max_hp} HP")
st.progress(n.hp / n.max_hp)
st.markdown(f"**Zombie:** {z.hp}/{z.max_hp} HP")
st.progress(z.hp / z.max_hp)

# Actions
cols = st.columns(4)
action = None
if cols[0].button("Attack"):
    dmg = n.attack(z)
    st.success(f"You attack for {dmg} damage!")
    action = True
if cols[1].button("Heal", disabled=(n.heals<=0)):
    amt = n.heal_self()
    st.info(f"You heal for {amt} HP.")
    action = True
if cols[2].button("Special", disabled=(n.specials<=0)):
    dmg = n.special_attack(z)
    st.warning(f"Adrenaline shot for {dmg} damage!")
    action = True
if cols[3].button("Use Item", disabled=(sum(n.inventory.values())==0)):
    item = st.selectbox("Select item", [i for i,c in n.inventory.items() if c>0])
    amt  = n.use_item(item)
    st.info(f"You use {item} and heal {amt} HP.")
    action = True

# Zombie turn
if action:
    dmg = z.attack(n)
    st.error(f"Zombie bites you for {dmg} damage!")

# Check end
if n.hp <= 0:
    st.error("💀 You died…")
    if st.button("Play Again"):
        st.session_state.started = False
        st.experimental_rerun()
    st.stop()

if z.hp <= 0:
    st.success("🎉 You defeated the Zombie!")
    if st.button("Next Wave"):
        st.session_state.wave += 1
        hp, dmin, dmax = 120 + 10*st.session_state.wave, 15, 25
        st.session_state.zombie = Zombie("Zombie", hp, dmin, dmax)
        st.experimental_rerun()
    st.stop()
