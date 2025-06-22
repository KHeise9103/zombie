# File: nurse_vs_zombie_gui_2.py
import tkinter as tk
from tkinter import messagebox, ttk
import random
import os

# ─── Game Logic ───────────────────────────────────────────────────────────────

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

# ─── GUI ──────────────────────────────────────────────────────────────────────

class GameGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🩺 Nurse vs 🧟 Zombie")
        self.configure(bg="#000")
        self.resizable(True, True)

        # Styles
        style = ttk.Style(self)
        style.theme_use('default')
        style.configure("Green.Horizontal.TProgressbar", background="#4caf50")
        style.configure("Yellow.Horizontal.TProgressbar", background="#ffeb3b")
        style.configure("Red.Horizontal.TProgressbar", background="#f44336")

        self.nurse = Nurse()
        self.zombie = None

        self._build_start()

    def _build_start(self):
        diff_frame = tk.Frame(self, bg="#000")
        tk.Label(diff_frame, text="Select difficulty:", font=("Arial",14), fg="#FFF", bg="#000").pack(pady=5)
        self.diff_var = tk.StringVar(self, value="Medium")
        for lvl in ("Easy","Medium","Hard"):
            tk.Radiobutton(diff_frame, text=lvl, variable=self.diff_var, value=lvl,
                           fg="#FFF", bg="#000", selectcolor="#333").pack(anchor="w")
        tk.Button(diff_frame, text="Start Game", command=self.start_game).pack(pady=10)
        diff_frame.pack(padx=20, pady=20)

    def start_game(self):
        lvl = self.diff_var.get()
        params = {"Easy":(80,10,15), "Medium":(120,15,25), "Hard":(150,20,30)}[lvl]
        self.zombie = Zombie("Zombie", *params)
        for widget in self.winfo_children():
            widget.destroy()
        self.build_battle_ui()

    def build_battle_ui(self):
        bg_path = "background.png"
        max_h = int(self.winfo_screenheight()*0.5)
        if os.path.exists(bg_path):
            bg = tk.PhotoImage(file=bg_path)
            w,h = bg.width(), bg.height()
            if h > max_h:
                bg = bg.subsample(1, h//max_h+1)
                w,h = bg.width(), bg.height()
            self.bg_img = bg
        else:
            w,h = 600, max_h
            self.bg_img = None
        self.canvas_width, self.canvas_height = w, h
        self.canvas = tk.Canvas(self, width=w, height=h, bg="#000", highlightthickness=0)
        if self.bg_img:
            self.canvas.create_image(0,0,anchor='nw',image=self.bg_img)
        else:
            self.canvas.create_rectangle(0,0,w,h,fill="#333")
        self.canvas.pack(side='top', fill='x')

        # sprite scaling based on canvas height
        sprite_size = h // 6
        y = h // 2
        raw_n = tk.PhotoImage(file="nurse.png")
        fn = max(raw_n.width()//sprite_size, raw_n.height()//sprite_size, 1)
        self.nurse_img = raw_n.subsample(fn, fn)
        self.nurse_spr = self.canvas.create_image(50, y, image=self.nurse_img)
        raw_z = tk.PhotoImage(file="zombie.png")
        fz = max(raw_z.width()//sprite_size, raw_z.height()//sprite_size, 1)
        self.zombie_img = raw_z.subsample(fz, fz)
        self.zombie_spr = self.canvas.create_image(w-50, y, image=self.zombie_img)

        ui = tk.Frame(self, bg="#000")
        # health bars
        bars = tk.Frame(ui, bg="#000"); bl = w//2
        tk.Label(bars, text="Nurse HP", fg="#FFF", bg="#000").pack(anchor='w')
        self.nurse_bar = ttk.Progressbar(bars, length=bl, maximum=self.nurse.max_hp, style="Green.Horizontal.TProgressbar")
        self.nurse_bar.pack(fill='x', padx=20)
        self.nurse_hp_label = tk.Label(bars, fg="#FFF", bg="#000"); self.nurse_hp_label.pack(anchor='e', padx=20)
        tk.Label(bars, text="Zombie HP", fg="#FFF", bg="#000").pack(anchor='w', pady=(10,0))
        self.zombie_bar = ttk.Progressbar(bars, length=bl, maximum=self.zombie.max_hp, style="Green.Horizontal.TProgressbar")
        self.zombie_bar.pack(fill='x', padx=20)
        self.zombie_hp_label = tk.Label(bars, fg="#FFF", bg="#000"); self.zombie_hp_label.pack(anchor='e', padx=20)
        bars.pack(pady=10)

        # controls and log
        self.status = tk.Label(ui, font=("Consolas",12), fg="#FFF", bg="#000"); self.status.pack(pady=5)
        ctrl = tk.Frame(ui, bg="#000"); self.buttons = []
        for txt, cmd in [("Attack", self.do_attack), ("Heal", self.do_heal), ("Special", self.do_special), ("Use Item", self.do_item)]:
            b = tk.Button(ctrl, text=txt, command=cmd); b.pack(side='left', padx=5); self.buttons.append(b)
        ctrl.pack(pady=5)
        self.log = tk.Text(ui, height=8, width=60, state='disabled', bg="#000", fg="#FFF"); self.log.pack(pady=(0,10))
        ui.pack(side='bottom', fill='x')

        self.update_status()

    def update_status(self):
        n,z = self.nurse, self.zombie
        def style(hp,mx):
            if hp<20: return "Red.Horizontal.TProgressbar"
            if hp<45: return "Yellow.Horizontal.TProgressbar"
            return "Green.Horizontal.TProgressbar"
        self.nurse_bar.config(style=style(n.hp,n.max_hp), value=n.hp)
        self.nurse_hp_label.config(text=f"{n.hp}/{n.max_hp}")
        self.zombie_bar.config(style=style(z.hp,z.max_hp), value=z.hp)
        self.zombie_hp_label.config(text=f"{z.hp}/{z.max_hp}")
        sx,ex=50,self.canvas_width-50; cx=self.canvas_width//2; y=self.canvas_height//2
        nx=sx+int((cx-sx)*(1-n.hp/n.max_hp)); zx=ex+int((cx-ex)*(1-z.hp/n.max_hp))
        self.canvas.coords(self.nurse_spr,nx,y); self.canvas.coords(self.zombie_spr,zx,y)
        inv = ", ".join(f"{k}:×{v}" for k,v in n.inventory.items())
        self.status.config(text=f"Heals:{n.heals} Specials:{n.specials}\nInventory:{inv}")
        # disable resource buttons
        self.buttons[2].config(state='normal' if n.specials>0 else 'disabled')
        self.buttons[1].config(state='normal' if n.heals>0 else 'disabled')
        self.buttons[3].config(state='normal' if any(n.inventory.values()) else 'disabled')

    def log_msg(self, m):
        self.log.config(state='normal'); self.log.insert('end', m+"\n"); self.log.see('end'); self.log.config(state='disabled')

    def animate_lunge(self):
        self.canvas.move(self.nurse_spr, 20, 0); self.after(100, lambda: self.canvas.move(self.nurse_spr, -20, 0))

    def disable_buttons(self):
        for b in self.buttons: b.config(state='disabled')

    def enable_buttons(self):
        for b in self.buttons: b.config(state='normal')

    def do_attack(self): self._player_action('attack')
    def do_heal(self):   self._player_action('heal')
    def do_special(self):self._player_action('special')

    def _player_action(self, action):
        self.disable_buttons()
        if action=='attack': d=self.nurse.attack(self.zombie); self.animate_lunge(); self.log_msg(f"You attack for {d} dmg.")
        elif action=='heal': h=self.nurse.heal(); self.log_msg(f"You heal {h} HP." if h else "No heals left!")
        else: s=self.nurse.special(self.zombie); self.log_msg(f"Adrenaline Shot! {s} dmg.")
        self.update_status(); self.after(500, self.zombie_attack)

    def zombie_attack(self):
        self.enable_buttons()
        d=self.zombie.attack(self.nurse); self.log_msg(f"Zombie bites you for {d} dmg.")
        self.update_status()
        if self.nurse.hp<=0 or self.zombie.hp<=0:
            over=tk.Toplevel(self); over.transient(self); over.grab_set()
            over.title("Game Over")
            over.geometry(f"{int(self.winfo_width()*0.8)}x{int(self.winfo_height()*0.8)}+{self.winfo_x()+50}+{self.winfo_y()+50}")
            over.config(bg="#222")
            msg = "💀 YOU DIED" if self.nurse.hp<=0 else "🎉 YOU WIN"
            clr = '#FF5555' if self.nurse.hp<=0 else '#55FF55'
            tk.Label(over, text=msg, fg=clr, bg="#222", font=("Helvetica",24,"bold")).pack(expand=True)
            frm=tk.Frame(over, bg="#222"); frm.pack(pady=20)
            tk.Button(frm, text="Retry", width=12, command=lambda o=over: self._retry(o)).pack(side='left', padx=10)
            tk.Button(frm, text="Exit", width=12, command=self.destroy).pack(side='left', padx=10)

    def do_item(self):
        self.disable_buttons()
        items=[i for i,c in self.nurse.inventory.items() if c>0]
        if not items: self.log_msg("No items!"); self.after(500, self.zombie_attack); return
        win=tk.Toplevel(self); win.title("Choose Item"); win.config(bg="#000")
        tk.Label(win, text="Select Item:", fg="#FFF", bg="#000").pack(pady=5)
        for it in items:
            amt=self.nurse.item_vals[it]
            tk.Button(win, text=f"{it} (×{self.nurse.inventory[it]}) heals {amt} HP",
                      command=lambda i=it, w=win: self._select_item(i, w)).pack(fill='x', padx=10, pady=2)
        win.update_idletasks()
        x=self.winfo_x()+(self.winfo_width()-win.winfo_width())//2; y=self.winfo_y()+(self.winfo_height()-win.winfo_height())//2
        win.geometry(f"+{x}+{y}")

    def _select_item(self, item, win):
        h=self.nurse.use_item(item); self.log_msg(f"You use {item} and heal {h} HP.")
        win.destroy(); self.after(500, self.zombie_attack)

    def _retry(self, over_win):
        over_win.destroy()
        self.nurse = Nurse()
        lvl = self.diff_var.get()
        params = {"Easy":(80,10,15), "Medium":(120,15,25), "Hard":(150,20,30)}[lvl]
        self.zombie = Zombie("Zombie", *params)
        for w in self.winfo_children(): w.destroy()
        self.build_battle_ui()

if __name__=="__main__":
    GameGUI().mainloop()