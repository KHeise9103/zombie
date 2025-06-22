
import streamlit as st
import random

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
        if self.heals <= 0:
            return 0
        self.heals -= 1
        self.hp = min(self.hp + self.heal_amt, self.max_hp)
        return self.heal_amt

    def special(self, target):
        if self.specials <= 0:
            return 0
        self.specials -= 1
        dmg = random.randint(self.smin, self.smax)
        target.hp = max(target.hp - dmg, 0)
        return dmg

    def use_item(self, item):
        if self.inventory.get(item, 0) <= 0:
            return 0
        self.inventory[item] -= 1
        heal = self.item_vals[item]
        self.hp = min(self.hp + heal, self.max_hp)
        return heal

class Zombie(Character): pass

# Game Setup
if 'started' not in st.session_state:
    st.session_state.started = False
    st.session_state.nurse = Nurse()
    st.session_state.difficulty = 'Medium'
    st.session_state.zombie = None
    st.session_state.log = []

def start_game():
    st.session_state.nurse = Nurse()
    params = {"Easy":(80,10,15), "Medium":(120,15,25), "Hard":(150,20,30)}[st.session_state.difficulty]
    st.session_state.zombie = Zombie("Zombie", *params)
    st.session_state.log = []
    st.session_state.started = True

def log(msg):
    st.session_state.log.append(msg)

def zombie_attack():
    dmg = st.session_state.zombie.attack(st.session_state.nurse)
    log(f"🧟 Zombie bites you for {dmg} dmg.")

def game_over():
    n = st.session_state.nurse
    z = st.session_state.zombie
    if n.hp <= 0:
        st.error("💀 YOU DIED")
        return True
    elif z.hp <= 0:
        st.success("🎉 YOU WIN!")
        return True
    return False

# UI
st.title("🩺 Nurse vs 🧟 Zombie")

if not st.session_state.started:
    st.subheader("Choose difficulty")
    st.session_state.difficulty = st.radio("", ["Easy", "Medium", "Hard"], index=1)
    if st.button("Start Game"):
        start_game()
        st.experimental_rerun()
else:
    n = st.session_state.nurse
    z = st.session_state.zombie

    st.subheader(f"Wave 1")
    st.markdown(f"**Nurse:** {n.hp}/{n.max_hp} HP")
    st.markdown(f"**Zombie:** {z.hp}/{z.max_hp} HP")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚔️ Attack"):
            dmg = n.attack(z)
            log(f"You attack for {dmg} dmg.")
            zombie_attack()
            st.experimental_rerun()

        if st.button("💊 Heal", disabled=n.heals <= 0):
            healed = n.heal()
            log(f"You heal for {healed} HP.")
            zombie_attack()
            st.experimental_rerun()

        if st.button("💉 Special", disabled=n.specials <= 0):
            dmg = n.special(z)
            log(f"Adrenaline Shot! {dmg} dmg.")
            zombie_attack()
            st.experimental_rerun()

        items = [k for k,v in n.inventory.items() if v > 0]
        item = st.selectbox("Use Item", options=items if items else ["No Items"], disabled=not items)
        if st.button("🧪 Use Item", disabled=not items):
            healed = n.use_item(item)
            log(f"You use {item} and heal {healed} HP.")
            zombie_attack()
            st.experimental_rerun()

    with col2:
        st.markdown(f"**Heals left:** {n.heals}")
        st.markdown(f"**Specials left:** {n.specials}")
        st.markdown("**Inventory:**")
        for k, v in n.inventory.items():
            st.markdown(f"- {k}: ×{v}")

    st.divider()
    for l in st.session_state.log[-10:]:
        st.markdown(l)

    if game_over():
        if st.button("🔁 Retry"):
            st.session_state.started = False
            st.experimental_rerun()
