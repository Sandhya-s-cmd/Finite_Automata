import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from graphviz import Digraph
from PIL import Image, ImageTk

class AutomataSimulator:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=15)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(frame, text="Select Automata Type:").grid(row=0, column=0, sticky="w")
        self.automata_type = ttk.Combobox(frame, values=["PDA"], state="readonly")
        self.automata_type.set("PDA")
        self.automata_type.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="States (comma-separated):").grid(row=1, column=0, sticky="w")
        self.states_entry = ttk.Entry(frame)
        self.states_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Alphabet (comma-separated):").grid(row=2, column=0, sticky="w")
        self.alphabet_entry = ttk.Entry(frame)
        self.alphabet_entry.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="Stack Alphabet (comma-separated):").grid(row=3, column=0, sticky="w")
        self.stack_alphabet_entry = ttk.Entry(frame)
        self.stack_alphabet_entry.grid(row=3, column=1, pady=5)

        ttk.Label(frame, text="Transitions (format: q0,a,Z->q0,AZ or q1,b,A->q1,ε):").grid(row=4, column=0, sticky="w")
        self.transitions_entry = ScrolledText(frame, height=4, width=30)
        self.transitions_entry.grid(row=4, column=1, pady=5)

        ttk.Label(frame, text="Initial State:").grid(row=5, column=0, sticky="w")
        self.initial_state_entry = ttk.Entry(frame)
        self.initial_state_entry.grid(row=5, column=1, pady=5)

        ttk.Label(frame, text="Final States (comma-separated):").grid(row=6, column=0, sticky="w")
        self.final_states_entry = ttk.Entry(frame)
        self.final_states_entry.grid(row=6, column=1, pady=5)

        self.input_string_label = ttk.Label(frame, text="Input String:")
        self.input_string_label.grid(row=7, column=0, sticky="w")
        self.input_string_entry = ttk.Entry(frame)
        self.input_string_entry.grid(row=7, column=1, pady=5)

        self.simulate_button = ttk.Button(frame, text="Simulate", command=self.simulate)
        self.simulate_button.grid(row=8, column=0, pady=10)

        self.visualize_button = ttk.Button(frame, text="Visualize Automaton", command=self.visualize)
        self.visualize_button.grid(row=8, column=1, pady=10)

    def parse_transitions(self):
        transitions = {}
        raw_transitions = self.transitions_entry.get("1.0", tk.END).strip().split("\n")

        for transition in raw_transitions:
            parts = transition.replace(" ", "").split("->")
            if len(parts) != 2:
                messagebox.showerror("Format Error", f"Invalid transition: {transition}")
                return None

            left, right = parts
            left_parts = left.split(",")

            if len(left_parts) != 3:
                messagebox.showerror("Format Error", f"Invalid PDA transition format: {transition}")
                return None

            state, symbol, stack_top = left_parts
            next_state, new_stack = right.split(",")

            transitions.setdefault((state, symbol, stack_top), []).append((next_state, new_stack))
        
        return transitions

    def simulate(self):
        states = set(self.states_entry.get().strip().split(","))
        alphabet = set(self.alphabet_entry.get().strip().split(","))
        stack_alphabet = set(self.stack_alphabet_entry.get().strip().split(","))
        initial_state = self.initial_state_entry.get().strip()
        final_states = set(self.final_states_entry.get().strip().split(","))
        input_string = self.input_string_entry.get().strip()

        transitions = self.parse_transitions()
        if transitions is None:
            return

        stack = ["Z"]
        state = initial_state
        input_string += "ε"  # Append epsilon for final transition

        log = f"Initial State: {state}, Stack: {stack}\n"

        for symbol in input_string:
            stack_top = stack[-1] if stack else "ε"

            # Check if we have a valid transition with the current state, symbol, and stack top
            if (state, symbol, stack_top) in transitions:
                next_state, stack_replace = transitions[(state, symbol, stack_top)][0]

                # Stack management: Pop the top stack symbol if it's not epsilon
                if stack_top != "ε":
                    stack.pop()

                # Push the new stack symbol if it's not epsilon
                if stack_replace != "ε":
                    stack.extend(reversed(stack_replace))  # Reversed to maintain proper order

                log += f"Transition: ({state}, {symbol}, {stack_top}) → ({next_state}, {stack})\n"
                state = next_state
            else:
                # If no transition exists, reject input
                log += f"Transition not found for ({state}, {symbol}, {stack_top}). Rejected!\n"
                break

        # Check if the state is final and the stack is empty for acceptance
        if state in final_states and stack == ["Z"]:
            log += "Input Accepted! ✅"
        else:
            log += "Input Rejected ❌"

        messagebox.showinfo("Simulation Result", log)

    def visualize(self):
        states = set(self.states_entry.get().strip().split(","))
        alphabet = set(self.alphabet_entry.get().strip().split(","))
        stack_alphabet = set(self.stack_alphabet_entry.get().strip().split(","))
        transitions = self.transitions_entry.get("1.0", tk.END).strip()
        initial_state = self.initial_state_entry.get().strip()
        final_states = set(self.final_states_entry.get().strip().split(","))

        if not (states and alphabet and stack_alphabet and transitions and initial_state and final_states):
            messagebox.showerror("Input Error", "Please fill in all fields before visualizing.")
            return

        try:
            dot = Digraph(format="png")
            dot.node("start", shape="none", label="", width="0")
            dot.edge("start", initial_state)

            for state in states:
                if state in final_states:
                    dot.node(state.strip(), shape="doublecircle", style="filled", fillcolor="lightblue")
                else:
                    dot.node(state.strip(), shape="circle", style="filled", fillcolor="lightgray")

            for transition in transitions.split("\n"):
                transition = transition.strip()
                if not transition:
                    continue

                parts = transition.split("->")
                if len(parts) != 2:
                    messagebox.showerror("PDA Format Error", f"Invalid PDA transition format: {transition}")
                    return

                left, right = parts
                left_parts = left.split(",")
                right_parts = right.split(",")

                if len(left_parts) != 3 or len(right_parts) != 2:
                    messagebox.showerror("PDA Format Error", f"Invalid PDA transition format: {transition}")
                    return

                from_state, symbol, stack_symbol = left_parts
                to_state, new_stack_symbol = right_parts

                dot.edge(from_state, to_state, label=f"{symbol},{stack_symbol} → {new_stack_symbol}", arrowhead="box")

            # *Render and Save the Automata Graph*
            dot.render("automata", format="png", cleanup=False)

            self.show_image()

        except Exception as e:
            messagebox.showerror("Visualization Error", f"An error occurred: {str(e)}")

    def show_image(self):
        try:
            img_window = tk.Toplevel(self.root)
            img_window.title("Automaton Visualization")
            img_window.geometry("600x400")

            img = Image.open("automata.png")  # Make sure this file exists
            img = img.resize((500, 300), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)

            img_label = ttk.Label(img_window, image=img)
            img_label.image = img  # Keep reference to avoid garbage collection
            img_label.pack()

        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load image: {str(e)}")


def open_simulation_window():
    root = tk.Tk()
    root.title("Automata Simulator")
    root.geometry("800x600")
    app = AutomataSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    open_simulation_window()
