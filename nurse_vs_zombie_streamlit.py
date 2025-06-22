
import streamlit as st
import random

# Initialize game state
if "nurse_hp" not in st.session_state:
    st.session_state.nurse_hp = 100
    st.session_state.zombie_hp = 120
    st.session_state.nurse_heals = 3
    st.session_state.nurse_specials = 2
    st.session_state.inventory = {"Medkit": 1, "Syringe": 2}
    st.session_state.difficulty = "Medium"
    st.session_state.logs = []
    st.session_state.wave = 1

# Character stats by difficulty
difficulty_settings = {
    "Easy": (80, 10, 15),
    "Medium": (120, 15, 25),
    "Hard": (150, 20, 30)
}

# Select difficulty at start
if "difficulty_set" not in st.session_state:
    st.title("🩺 Nurse vs 🧟 Zombie")
    st.write("Choose difficulty")
    col1, col2, col3 = st.columns(3)
    with col1: if st.button("Easy"): st.session_state.difficulty = "Easy"; st.session_state.difficulty_set = True; st.experimental_rerun()
    with col2: if st.button("Medium"): st.session_state.difficulty = "Medium"; st.session_state.difficulty_set = True; st.experimental_rerun()
    with col3: if st.button("Hard"): st.session_state.difficulty = "Hard"; st.session_state.difficulty_set = True; st.experimental_rerun()
    st.stop()

# Load difficulty
z_hp, z_min, z_max = difficulty_settings[st.session_state.difficulty]
if st.session_state.zombie_hp > z_hp:
    st.session_state.zombie_hp = z_hp

# Sidebar stats
st.sidebar.title("Stats")
st.sidebar.write(f"Nurse HP: {st.session_state.nurse_hp}/100")
st.sidebar.write(f"Zombie HP: {st.session_state.zombie_hp}/{z_hp}")
st.sidebar.write(f"Heals Left: {st.session_state.nurse_heals}")
st.sidebar.write(f"Specials Left: {st.session_state.nurse_specials}")
st.sidebar.write("Inventory:")
for item, count in st.session_state.inventory.items():
    st.sidebar.write(f"- {item}: x{count}")

# Game Log
st.title("Wave " + str(st.session_state.wave))
st.header("Nurse: 100/100 HP")
st.header(f"Zombie: {z_hp}/{z_hp} HP")
st.subheader("Action")

col1, col2, col3, col4 = st.columns(4)

def log(message):
    st.session_state.logs.append(message)

def nurse_attack():
    dmg = random.randint(10, 20)
    st.session_state.zombie_hp = max(st.session_state.zombie_hp - dmg, 0)
    log(f"🩺 Nurse attacks for {dmg} damage!")
    zombie_attack()

def nurse_heal():
    if st.session_state.nurse_heals > 0:
        st.session_state.nurse_heals -= 1
        st.session_state.nurse_hp = min(st.session_state.nurse_hp + 25, 100)
        log(f"🩺 Nurse heals for 25 HP!")
        zombie_attack()
    else:
        log("🩺 No heals left!")

def nurse_special():
    if st.session_state.nurse_specials > 0:
        st.session_state.nurse_specials -= 1
        dmg = random.randint(30, 50)
        st.session_state.zombie_hp = max(st.session_state.zombie_hp - dmg, 0)
        log(f"💉 Special attack hits for {dmg} damage!")
        zombie_attack()
    else:
        log("💉 No specials left!")

def nurse_use_item():
    available = [k for k,v in st.session_state.inventory.items() if v > 0]
    if not available:
        log("📦 No items left!")
        zombie_attack()
        return
    item = st.radio("Select item to use:", available)
    if st.button("Use Item"):
        if st.session_state.inventory[item] > 0:
            st.session_state.inventory[item] -= 1
            heal_amt = 50 if item == "Medkit" else 15
            st.session_state.nurse_hp = min(st.session_state.nurse_hp + heal_amt, 100)
            log(f"🩺 Used {item} and healed for {heal_amt} HP!")
            zombie_attack()

def zombie_attack():
    dmg = random.randint(z_min, z_max)
    st.session_state.nurse_hp = max(st.session_state.nurse_hp - dmg, 0)
    log(f"🧟 Zombie attacks for {dmg} damage!")

# Button logic
with col1: st.button("Attack", on_click=nurse_attack)
with col2: st.button("Heal", on_click=nurse_heal)
with col3: st.button("Special", on_click=nurse_special)
with col4: st.button("Use Item", on_click=nurse_use_item)

# Game logs
st.subheader("Combat Log")
for log_line in st.session_state.logs[-10:]:
    st.write(log_line)

# Game Over
if st.session_state.nurse_hp <= 0:
    st.error("💀 Nurse has fallen. Game Over!")
    if st.button("Restart"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()

elif st.session_state.zombie_hp <= 0:
    st.success("🎉 You defeated the zombie!")
    if st.button("Next Wave"):
        st.session_state.wave += 1
        st.session_state.zombie_hp = z_hp + 20 * st.session_state.wave
        st.experimental_rerun()
