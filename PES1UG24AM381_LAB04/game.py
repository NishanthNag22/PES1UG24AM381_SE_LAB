import random
from logic import feedback

DIFFICULTIES = {
    "1": {"name": "Easy", "length": 4, "range": 6, "turns": 12},
    "2": {"name": "Normal", "length": 4, "range": 6, "turns": 10},
    "3": {"name": "Hard", "length": 5, "range": 8, "turns": 8},
}

class Mastermind:
    def __init__(self):
        self.setup_game()
        self.history = []
        self.game_over = False

    def setup_game(self):
        print("Select difficulty:")
        for key, diff in DIFFICULTIES.items():
            print(f"{key}. {diff['name']} (Length: {diff['length']}, Range: 1-{diff['range']}, Turns: {diff['turns']})")
        
        while True:
            choice = input("Enter choice (1/2/3): ").strip()
            if choice in DIFFICULTIES:
                self.config = DIFFICULTIES[choice]
                break
            print("Invalid choice. Please enter 1, 2, or 3.")
            
        self.code_length = self.config["length"]
        self.symbol_range = self.config["range"]
        self.turns = self.config["turns"]
        self.code = [str(random.randint(1, self.symbol_range)) for _ in range(self.code_length)]
        self.valid_chars = "".join(str(i) for i in range(1, self.symbol_range + 1))

    def run(self):
        print(f"\nMastermind — enter {self.code_length} digits from 1 to {self.symbol_range}.")
        while self.turns > 0 and not self.game_over:
            raw = input(f"{self.turns} turns left > ").strip()
            if raw.lower() == "q":
                self.game_over = True
                return
            if len(raw) != self.code_length or any(ch not in self.valid_chars for ch in raw):
                print(f"Invalid input: Enter exactly {self.code_length} digits from 1 to {self.symbol_range}.")
                continue
            
            guess = list(raw)
            exact, partial = feedback(self.code, guess)
            self.history.append((raw, exact, partial))
            self.turns -= 1
            
            print("\n--- History ---")
            for i, (h_raw, h_e, h_p) in enumerate(self.history, 1):
                print(f"{i}: {h_raw} -> Exact: {h_e}, Partial: {h_p}")
            print("---------------\n")
            
            if exact == self.code_length:
                print("Cracked the code! You win!")
                self.game_over = True
                return
                
        if not self.game_over:
            print("Game over! You lost.")
            print("The code was", "".join(self.code))
            self.game_over = True
