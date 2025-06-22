    # ─── Actions ──────────────────────────────────────────────────────────
    cols = st.columns(3)
    acted = False

    if cols[0].button("Attack"):
        dmg = n.attack(z)
        st.success(f"You attack for {dmg} damage!")
        acted = True

    if cols[1].button("Heal", disabled=(n.heals<=0)):
        amt = n.heal_self()
        st.info(f"You heal for {amt} HP.")
        acted = True

    if cols[2].button("Special", disabled=(n.specials<=0)):
        dmg = n.special_attack(z)
        st.warning(f"Adrenaline shot for {dmg} damage!")
        acted = True

    # ─── Inventory / Use Item ──────────────────────────────────────────────
    items = [item for item,count in n.inventory.items() if count>0]
    if items:
        # Let the user pick BEFORE clicking
        item_choice = st.selectbox("Choose an item to use", items, key="item_choice")
        if st.button("Use Item"):
            healed = n.use_item(item_choice)
            st.info(f"You use a {item_choice} and heal {healed} HP.")
            acted = True
    else:
        st.button("Use Item", disabled=True)

    # ─── Zombie counterattack ──────────────────────────────────────────────
    if acted:
        dmg = z.attack(n)
        st.error(f"Zombie bites you for {dmg} damage!")
