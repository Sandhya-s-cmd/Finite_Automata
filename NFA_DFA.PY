import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from graphviz import Digraph
from PIL import Image, ImageTk
import os

# ---------------------- AUTOMATA SIMULATOR WINDOW ----------------------
def open_simulation_window():
    root = tk.Tk()
    root.title("Automata Simulator")
    root.geometry("800x600")

    try:
        bg_image_path = "C:\\Users\\sandhya\\Pictures\\automata_finite_state_diagrams.jpg"
        if os.path.exists(bg_image_path):
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize((800, 600), Image.LANCZOS)
            bg_photo = ImageTk.PhotoImage(bg_image)

            bg_label = tk.Label(root, image=bg_photo)
            bg_label.image = bg_photo  # Keep reference
            bg_label.place(relwidth=1, relheight=1)
    except Exception as e:
        messagebox.showwarning("Warning", f"Could not load background image: {e}")

    class AutomataSimulator:
        def __init__(self, master):
            self.master = master
            self.setup_ui()

        def setup_ui(self):
            frame = ttk.Frame(self.master, padding=15)
            frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            ttk.Label(frame, text="Select Automata Type:").grid(row=0, column=0, sticky="w")
            self.automata_type = ttk.Combobox(frame, values=["DFA", "NFA"], state="readonly")
            self.automata_type.set("DFA")
            self.automata_type.grid(row=0, column=1, pady=5)

            ttk.Label(frame, text="States (comma-separated):").grid(row=1, column=0, sticky="w")
            self.states_entry = ttk.Entry(frame)
            self.states_entry.grid(row=1, column=1, pady=5)

            ttk.Label(frame, text="Alphabet (comma-separated):").grid(row=2, column=0, sticky="w")
            self.alphabet_entry = ttk.Entry(frame)
            self.alphabet_entry.grid(row=2, column=1, pady=5)

            ttk.Label(frame, text="Transitions (format: q0,a->q1) - One per line:").grid(row=3, column=0, sticky="w")
            self.transitions_entry = ScrolledText(frame, height=4, width=30)
            self.transitions_entry.grid(row=3, column=1, pady=5)

            ttk.Label(frame, text="Initial State:").grid(row=4, column=0, sticky="w")
            self.initial_state_entry = ttk.Entry(frame)
            self.initial_state_entry.grid(row=4, column=1, pady=5)

            ttk.Label(frame, text="Final States (comma-separated):").grid(row=5, column=0, sticky="w")
            self.final_states_entry = ttk.Entry(frame)
            self.final_states_entry.grid(row=5, column=1, pady=5)

            self.visualize_button = ttk.Button(frame, text="Visualize Automaton", command=self.visualize)
            self.visualize_button.grid(row=6, column=0, columnspan=2, pady=10)

        def visualize(self):
            states = set(self.states_entry.get().strip().split(','))
            alphabet = set(self.alphabet_entry.get().strip().split(','))
            transitions = self.transitions_entry.get("1.0", tk.END).strip()
            initial_state = self.initial_state_entry.get().strip()
            final_states = set(self.final_states_entry.get().strip().split(','))

            if not (states and alphabet and transitions and initial_state and final_states):
                messagebox.showerror("Input Error", "Please fill in all fields before visualizing.")
                return

            if initial_state not in states:
                messagebox.showerror("Input Error", "Initial state must be part of the defined states.")
                return

            try:
                dot = Digraph(format="png")
                dot.node("start", shape="point")
                dot.edge("start", initial_state.strip(), label="Start")

                for state in states:
                    shape = "doublecircle" if state in final_states else "circle"
                    dot.node(state.strip(), shape=shape, style="filled", fillcolor="lightblue")

                for transition in transitions.split("\n"):
                    if "->" not in transition or "," not in transition:
                        messagebox.showerror("Format Error", f"Invalid transition format: {transition}")
                        return

                    from_state, rest = transition.split(",")
                    symbol, to_state = rest.split("->")

                    if from_state.strip() not in states or to_state.strip() not in states:
                        messagebox.showerror("State Error", f"Transition includes undefined state: {transition}")
                        return
                    if symbol.strip() not in alphabet:
                        messagebox.showerror("Alphabet Error", f"Transition includes undefined symbol: {symbol}")
                        return

                    dot.edge(from_state.strip(), to_state.strip(), label=symbol.strip())

                dot.render("automata", format="png", cleanup=True)
                self.show_image()

            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")

        def show_image(self):
            img_window = tk.Toplevel(self.master)
            img_window.title("Automaton Visualization")
            img_window.geometry("600x400")

            img = Image.open("automata.png")
            img = img.resize((500, 300), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)

            img_label = ttk.Label(img_window, image=img)
            img_label.image = img  # Keep reference
            img_label.pack()

    app = AutomataSimulator(root)
    root.mainloop()

# Start the simulation window
open_simulation_window()
