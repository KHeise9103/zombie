import streamlit as st
from PIL import Image
import random, os

# ─── Models ────────────────────────────────────────────────────────────────────

class Character:
    def __init__(self, name, max_hp, min_d, max_d):
        self.name, self.max_hp, self.hp = name, max_hp, max_hp
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
        if self.heals<=0: return 0
        self.heals-=1; amt=self.heal_amt
        self.hp = min(self.hp+amt, self.max_hp)
        return amt
    def special_attack(self, other):
        if self.specials<=0: return 0
        self.specials-=1
        dmg = random.randint(self.smin, self.smax)
        other.hp = max(other.hp-dmg, 0)
        return dmg
    def use_item(self, item):
        if self.inventory.get(item,0)<=0: return 0
        self.inventory[item]-=1
        h = self.item_vals[item]
        self.hp = min(self.hp+h, self.max_hp)
        return h

class Zombie(Character): pass

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_state():
    if "nurse" not in st.session_state: st.session_state.nurse = Nurse()
    if "zombie" not in st.session_state:
        # default Medium
        st.session_state.zombie = Zombie("Zombie",120,15,25)
    if "wave" not in st.session_state: st.session_state.wave = 1

def reset_state(difficulty):
    st.session_state.nurse = Nurse()
    hp, dmin, dmax = {"Easy":(80,10,15),
                      "Medium":(120,15,25),
                      "Hard":(150,20,30)}[difficulty]
    st.session_state.zombie = Zombie("Zombie", hp, dmin, dmax)

def load_img(fn, width=None):
    img = Image.open(fn)
    if width:
        ratio = width/img.width
        img = img.resize((int(img.width*ratio), int(img.height*ratio)))
    return img

# ─── UI ──────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Nurse vs Zombie", layout="wide")
st.title("🩺 Nurse vs 🧟 Zombie")

# First‐time difficulty selector
if "started" not in st.session_state or not st.session_state.started:
    diff = st.radio("Choose difficulty", ["Easy","Medium","Hard"], index=1, horizontal=True)
    if st.button("Start Game"):
        reset_state(diff)
        st.session_state.started = True
        st.experimental_rerun()
else:
    get_state()
    n, z = st.session_state.nurse, st.session_state.zombie

    # Display sprites + background
    bg = load_img("background.png", width=600)
    c1, c2, c3 = st.columns([1,2,1])
    with c1: st.image(load_img("nurse.png", width=200), caption="Nurse")
    with c2: st.image(bg, use_column_width=True)
    with c3: st.image(load_img("zombie.png", width=200), caption="Zombie")

    st.subheader(f"Wave {st.session_state.wave}")
    st.progress(n.hp/n.max_hp, text=f"Nurse {n.hp}/{n.max_hp} HP")
    st.progress(z.hp/z.max_hp, text=f"Zombie {z.hp}/{z.max_hp} HP")

    cols = st.columns(4)
    if cols[0].button("Attack"):
        dmg = n.attack(z); st.success(f"You attack for {dmg} dmg!")
    if cols[1].button("Heal", disabled=n.heals<=0):
        amt = n.heal_self(); st.info(f"You heal for {amt} HP.")
    if cols[2].button("Special", disabled=n.specials<=0):
        dmg = n.special_attack(z); st.warning(f"Adrenaline shot for {dmg} dmg!")
    if cols[3].button("Use Item", disabled=sum(n.inventory.values())==0):
        choice = st.selectbox("Item", [i for i,c in n.inventory.items() if c>0])
        amt = n.use_item(choice); st.info(f"You use {choice} and heal {amt} HP.")

    # Zombie retaliates once per interaction
    if st.session_state.get("last", None) != (n.hp,z.hp):
        st.session_state.last = (n.hp,z.hp)
        dmg = z.attack(n); st.error(f"Zombie bites you for {dmg} dmg!")

    # Check for end
    if n.hp<=0:
        if st.button("Play Again?"):
            st.session_state.started=False; st.experimental_rerun()
        st.error("💀 You died…")
        st.stop()
    if z.hp<=0:
        if st.button("Next Wave"):
            st.session_state.wave+=1
            hp = 120+10*st.session_state.wave
            st.session_state.zombie=Zombie("Zombie",hp,15,25)
            st.experimental_rerun()
        st.success("🎉 You win!")
        st.stop()
