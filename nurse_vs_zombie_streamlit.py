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
        if self.heals <= 0:
            return 0
        self.heals -= 1
        self.hp = min(self.hp + self.heal_amt, self.max_hp)
        return self.heal_amt

    def special_attack(self, other):
        if self.specials <= 0:
            return 0
        self.specials -= 1
        dmg = random.randint(self.smin, self.smax)
        other.hp = max(other.hp - dmg, 0)
        return dmg

    def use_item(self, item):
        if self.inventory.get(item, 0) <= 0:
            return 0
        self.inventory[item] -= 1
        amt = self.item_vals[item]
        self.hp = min(self.hp + amt, self.max_hp)
        return amt

class Zombie(Character): pass

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_state():
    """Ensure nurse, zombie, wave exist."""
    if "nurse" not in st.session_state:
        st.session_state.nurse = Nurse()
    if "zombie" not in st.session_state:
        # default medium
        st.session_state.zombie = Zombie("Zombie", 120, 15, 25)
    if "wave" not in st.session_state:
        st.session_state.wave = 1

def reset_state(difficulty):
    """Reset for new game or retry."""
    st.session_state.nurse = Nurse()
    hp, dmin, dmax = {"Easy":(80,10,15),"Medium":(120,15,25),"Hard":(150,20,30)}[difficulty]
    st.session_state.zombie = Zombie("Zombie", hp, dmin, dmax)
    st.session_state.wave = 1

def load_img(fn, width=None):
    img = Image.open(fn)
    if width:
        ratio = width / img.width
        img = img.resize((int(img.width*ratio), int(img.height*ratio)))
    return img

# ─── Streamlit page setup ─────────────────────────────────────────────────────

st.set_page_config(page_title="Nurse vs Zombie", layout="wide")
st.title("🩺 Nurse vs 🧟 Zombie")

# Initialize our “started” flag once
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.diff = "Medium"  # default

# ─── Difficulty selector ──────────────────────────────────────────────────────

if not st.session_state.started:
    diff = st.radio("Choose difficulty", ["Easy","Medium","Hard"], index=["Easy","Medium","Hard"].index(st.session_state.diff), horizontal=True)
    if st.button("Start Game"):
        st.session_state.diff = diff
        reset_state(diff)
        st.session_state.started = True

# ─── Main game UI ────────────────────────────────────────────────────────────

if st.session_state.started:
    get_state()
    n = st.session_state.nurse
    z = st.session_state.zombie

    # Sprites + Background
    bg = load_img("background.png", width=600)
    c1, c2, c3 = st.columns([1,2,1])
    with c1:
        st.image(load_img("nurse.png", width=200), caption="Nurse")
    with c2:
        st.image(bg, use_column_width=True)
    with c3:
        st.image(load_img("zombie.png", width=200), caption="Zombie")

    st.subheader(f"Wave {st.session_state.wave}")
    st.progress(n.hp / n.max_hp, text=f"Nurse: {n.hp}/{n.max_hp} HP")
    st.progress(z.hp / z.max_hp, text=f"Zombie: {z.hp}/{z.max_hp} HP")

    # Action buttons
    cols = st.columns(4)
    action_taken = False

    if cols[0].button("Attack"):
        dmg = n.attack(z)
        st.success(f"You attack for {dmg} damage!")
        action_taken = True

    if cols[1].button("Heal", disabled=(n.heals<=0)):
        amt = n.heal_self()
        st.info(f"You heal for {amt} HP.")
        action_taken = True

    if cols[2].button("Special", disabled=(n.specials<=0)):
        dmg = n.special_attack(z)
        st.warning(f"Adrenaline shot! {dmg} damage.")
        action_taken = True

    if cols[3].button("Use Item", disabled=(sum(n.inventory.values())==0)):
        choice = st.selectbox("Choose item", [i for i,c in n.inventory.items() if c>0])
        amt = n.use_item(choice)
        st.info(f"You use a {choice} and heal {amt} HP.")
        action_taken = True

    # Zombie counterattack once per interaction
    if action_taken:
        dmg = z.attack(n)
        st.error(f"Zombie bites you for {dmg} damage!")

    # End‐game checks
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
            hp = 120 + 10*st.session_state.wave
            st.session_state.zombie = Zombie("Zombie", hp, 15, 25)
            # carry nurse forward
            st.experimental_rerun()
        st.stop()
