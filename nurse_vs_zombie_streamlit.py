import streamlit as st
import random
from PIL import Image

# ─── Game Logic ────────────────────────────────────────────────

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
        self.inventory = {"Medkit": 1, "Syringe": 2}
        self.item_vals = {"Medkit": 50, "Syringe": 15}

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

class Zombie(Character):
    pass

# ─── Session Initialization ───────────────────────────────────

if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.log = []
    st.session_state.difficulty = None

# ─── Main UI ───────────────────────────────────────────────────

st.title("🩺 Nurse vs 🧟 Zombie")

if not st.session_state.game_started:
    st.header("Choose difficulty")
    cols = st.columns(3)
    if cols[0].button("Easy"): st.session_state.difficulty = "Easy"
    if cols[1].button("Medium"): st.session_state.difficulty = "Medium"
    if cols[2].button("Hard"): st.session_state.difficulty = "Hard"

    if st.session_state.difficulty:
        params = {"Easy": (80, 10, 15), "Medium": (120, 15, 25), "Hard": (150, 20, 30)}[st.session_state.difficulty]
        st.session_state.nurse = Nurse()
        st.session_state.zombie = Zombie("Zombie", *params)
        st.session_state.game_started = True
        st.rerun()
else:
    nurse = st.session_state.nurse
    zombie = st.session_state.zombie

    st.markdown(f"**{nurse.name}: {nurse.hp}/{nurse.max_hp} HP**")
    st.progress(nurse.hp / nurse.max_hp)

    st.markdown(f"**{zombie.name}: {zombie.hp}/{zombie.max_hp} HP**")
    st.progress(zombie.hp / zombie.max_hp)

    st.markdown(f"Heals left: {nurse.heals} | Specials left: {nurse.specials} | Inventory: {nurse.inventory}")

    cols = st.columns(4)

    def attack():
        dmg = nurse.attack(zombie)
        st.session_state.log.append(f"You attacked the zombie for {dmg} damage.")
        enemy_turn()

    def heal():
        amt = nurse.heal()
        st.session_state.log.append(f"You healed yourself for {amt} HP." if amt else "No heals left.")
        enemy_turn()

    def special():
        dmg = nurse.special(zombie)
        st.session_state.log.append(f"You used Adrenaline Shot for {dmg} damage." if dmg else "No specials left.")
        enemy_turn()

    def use_item():
        options = [item for item, count in nurse.inventory.items() if count > 0]
        item = st.selectbox("Choose an item", options)
        if st.button("Use Item"):
            amt = nurse.use_item(item)
            st.session_state.log.append(f"You used {item} and healed for {amt} HP.")
            enemy_turn()

    def enemy_turn():
        if zombie.hp > 0:
            dmg = zombie.attack(nurse)
            st.session_state.log.append(f"Zombie bites you for {dmg} damage.")
        check_game_over()

    def check_game_over():
        if nurse.hp <= 0:
            st.error("💀 YOU DIED")
            if st.button("Restart"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
        elif zombie.hp <= 0:
            st.success("🎉 YOU WIN")
            if st.button("Play Again"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

    if cols[0].button("Attack"): attack()
    if cols[1].button("Heal"): heal()
    if cols[2].button("Special"): special()
    with cols[3]:
        if any(v > 0 for v in nurse.inventory.values()):
            use_item()

    st.subheader("Battle Log")
    for entry in st.session_state.log[::-1][:10]:
        st.text(entry)
