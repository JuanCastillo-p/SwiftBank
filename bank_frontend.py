# bank_frontend.py
import customtkinter as ctk
from tkinter import messagebox
from bank_backend import BankLogic
           
class SwiftBankApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SwiftBank - Modern Banking")
        self.geometry("1000x700")
        self.minsize(500, 600)  # Minimum size for responsiveness
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.bank = BankLogic()
        
        # Configure grid for responsive layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.showWelcomeScreen()

    def clearWindow(self):
        for widget in self.winfo_children():
            widget.destroy()

    # Welcome Screen
    def showWelcomeScreen(self):
        self.clearWindow()
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Title - responsive font
        title_font_size = max(32, int(self.winfo_width() / 30))
        ctk.CTkLabel(frame, text="SWIFT BANK", font=("Arial", 48, "bold")).pack(pady=20)
        ctk.CTkLabel(frame, text="Welcome to Swift Bank!", font=("Arial", 18)).pack(pady=10)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=30, expand=True, fill="both", padx=40)
        
        # Calculate responsive button width
        btn_width = min(300, max(150, int(self.winfo_width() * 0.7)))
        btn_height = 60
        font_size = 16
        
        ctk.CTkButton(btn_frame, text="Login", width=btn_width, height=btn_height,
                      font=("Arial", font_size), command=self.showLoginScreen).pack(pady=15, fill="x")
        ctk.CTkButton(btn_frame, text="Open Account", width=btn_width, height=btn_height,
                      font=("Arial", font_size), fg_color="#2ecc71", hover_color="#27ae60",
                      command=self.showRegisterScreen).pack(pady=15, fill="x")
        ctk.CTkButton(btn_frame, text="Exit", width=btn_width, height=btn_height,
                      font=("Arial", font_size), fg_color="#e74c3c", hover_color="#c0392b",
                      command=self.quit).pack(pady=15, fill="x")

    # Login Screen
    def showLoginScreen(self):
        self.clearWindow()
        container = ctk.CTkFrame(self)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(container, text="Login", font=("Arial", 32, "bold")).pack(pady=20)

        entry_width = min(350, int(self.winfo_width() * 0.9))
        
        ctk.CTkLabel(container, text="Account ID:").pack(pady=(10, 5))
        acc = ctk.CTkEntry(container, width=entry_width)
        acc.pack(fill="x", padx=20)
        
        ctk.CTkLabel(container, text="Full Name:").pack(pady=(10, 5))
        name = ctk.CTkEntry(container, width=entry_width)
        name.pack(fill="x", padx=20)
        
        ctk.CTkLabel(container, text="4-Digit PIN:").pack(pady=(10, 5))
        pin = ctk.CTkEntry(container, width=entry_width, show="*")
        pin.pack(fill="x", padx=20)

        def doLogin():
            ok, msg = self.bank.login(acc.get(), name.get(), pin.get())
            messagebox.showinfo("Result", msg)
            # On successful login, proceed to dashboard
            if ok:
                self.showDashboard()
                return
            # If backend signaled too many failed attempts, return to welcome screen
            if "Returning to starting screen" in msg:
                self.showWelcomeScreen()
                return
            # otherwise remain on login screen and clear the PIN field for retry
            pin.delete(0, 'end')

        ctk.CTkButton(container, text="Login", width=entry_width, command=doLogin).pack(pady=20, fill="x", padx=20)
        ctk.CTkButton(container, text="Back", width=150, fg_color="gray",
                      command=self.showWelcomeScreen).pack(pady=10)

    # Register Screen
    def showRegisterScreen(self):
        self.clearWindow()
        container = ctk.CTkScrollableFrame(self)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(container, text="Open New Account", font=("Arial", 32, "bold")).pack(pady=20)

        entry_width = min(400, int(self.winfo_width() * 0.9))
        
        name = ctk.CTkEntry(container, placeholder_text="Full Name", width=entry_width)
        name.pack(pady=5, fill="x", padx=10)
        
        addr = ctk.CTkEntry(container, placeholder_text="Address", width=entry_width)
        addr.pack(pady=5, fill="x", padx=10)
        
        pin = ctk.CTkEntry(container, placeholder_text="4-Digit PIN", show="*", width=entry_width)
        pin.pack(pady=5, fill="x", padx=10)
        
        pin2 = ctk.CTkEntry(container, placeholder_text="Confirm PIN", show="*", width=entry_width)
        pin2.pack(pady=5, fill="x", padx=10)
        
        bal = ctk.CTkEntry(container, placeholder_text="Initial Deposit", width=entry_width)
        bal.pack(pady=5, fill="x", padx=10)

        def create():
            if pin.get() != pin2.get():
                messagebox.showerror("Error", "PINs do not match!")
                return
            ok, msg = self.bank.openAccount(name.get(), addr.get(), pin.get(), bal.get())
            if ok:
                messagebox.showinfo("Success", msg)
                self.showWelcomeScreen()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(container, text="Create Account", width=entry_width, fg_color="#2ecc71",
                      hover_color="#27ae60", command=create).pack(pady=20, fill="x", padx=10)
        ctk.CTkButton(container, text="Back", width=150, fg_color="gray",
                      command=self.showWelcomeScreen).pack(pady=10)

    # Dashboard
    def showDashboard(self):
        self.clearWindow()
        self.bank.refreshUser()
        u = self.bank.logged_in_user
        
        header = ctk.CTkFrame(self, height=100, fg_color="#1e3a5f")
        header.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(header, text=f"Welcome, {u['bank_user']}", font=("Arial", 24, "bold")).pack(side="left", padx=20, pady=15)
        ctk.CTkButton(header, text="Logout", width=100, fg_color="#e74c3c",
                      command=self.logout).pack(side="right", padx=20, pady=15)

        # Main content frame
        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Balance section
        bal_frame = ctk.CTkFrame(content)
        bal_frame.pack(fill="x", pady=15)
        ctk.CTkLabel(bal_frame, text="Current Balance", font=("Arial", 16)).pack()
        ctk.CTkLabel(bal_frame, text=f"₱{u['bank_balance']:.2f}", font=("Arial", 42, "bold"),
                     text_color="#2ecc71").pack()
        ctk.CTkLabel(bal_frame, text=f"Account ID: {u['bank_id']}", font=("Arial", 12),
                     text_color="gray").pack()

        # Actions - responsive grid
        actions_frame = ctk.CTkFrame(content)
        actions_frame.pack(fill="both", expand=True, pady=10)
        
        actions = [
            ("Deposit", self.showDepositScreen, "#3498db"),
            ("Withdraw", self.showWithdrawScreen, "#9b59b6"),
            ("Transfer", self.showTransferScreen, "#e67e22"),
            ("Transaction History", self.showLogsScreen, "#16a085"),
        ]
        
        for txt, cmd, color in actions:
            btn_height = min(80, int(self.winfo_height() * 0.15))
            ctk.CTkButton(actions_frame, text=txt, height=btn_height, font=("Arial", 14),
                          fg_color=color, command=cmd).pack(pady=8, fill="x")

    def logout(self):
        self.bank.logged_in_user = None
        self.showWelcomeScreen()

    # Deposit
    def showDepositScreen(self):
        self.clearWindow()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="Deposit Money", font=("Arial", 32, "bold")).pack(pady=20)
        
        entry_width = min(350, int(self.winfo_width() * 0.9))
        
        amt = ctk.CTkEntry(frame, placeholder_text="Amount ₱", width=entry_width)
        amt.pack(pady=5, fill="x", padx=20)
        
        pin = ctk.CTkEntry(frame, placeholder_text="PIN", show="*", width=entry_width)
        pin.pack(pady=5, fill="x", padx=20)

        def dep():
            ok, msg = self.bank.deposit(amt.get(), pin.get())
            messagebox.showinfo("Result", msg)
            if ok:
                self.showDashboard()
                return
            # If the backend logged out the account after 3 wrong PINs, go to welcome
            if self.bank.logged_in_user is None:
                messagebox.showinfo("Session", "Your account has been logged out. Returning to start screen.")
                self.showWelcomeScreen()
                return
            # otherwise clear the PIN for retry
            pin.delete(0, 'end')

        ctk.CTkButton(frame, text="Deposit", width=entry_width, fg_color="#2ecc71", command=dep).pack(pady=20, fill="x", padx=20)
        ctk.CTkButton(frame, text="Back", width=150, fg_color="gray",
                      command=self.showDashboard).pack(pady=10)

    # Withdraw
    def showWithdrawScreen(self):
        self.clearWindow()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="Withdraw Money", font=("Arial", 32, "bold")).pack(pady=20)
        
        entry_width = min(350, int(self.winfo_width() * 0.9))
        
        amt = ctk.CTkEntry(frame, placeholder_text="Amount ₱", width=entry_width)
        amt.pack(pady=5, fill="x", padx=20)
        
        pin = ctk.CTkEntry(frame, placeholder_text="PIN", show="*", width=entry_width)
        pin.pack(pady=5, fill="x", padx=20)

        def wd():
            ok, msg = self.bank.withdraw(amt.get(), pin.get())
            messagebox.showinfo("Result", msg)
            if ok:
                self.showDashboard()
                return
            if self.bank.logged_in_user is None:
                messagebox.showinfo("Session", "Your account has been logged out. Returning to start screen.")
                self.showWelcomeScreen()
                return
            pin.delete(0, 'end')

        ctk.CTkButton(frame, text="Withdraw", width=entry_width, fg_color="#9b59b6", command=wd).pack(pady=20, fill="x", padx=20)
        ctk.CTkButton(frame, text="Back", width=150, fg_color="gray",
                      command=self.showDashboard).pack(pady=10)

    # Transfer
    def showTransferScreen(self):
        self.clearWindow()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="Transfer Money", font=("Arial", 32, "bold")).pack(pady=20)
        
        entry_width = min(350, int(self.winfo_width() * 0.9))
        
        rid = ctk.CTkEntry(frame, placeholder_text="Recipient Account ID", width=entry_width)
        rid.pack(pady=5, fill="x", padx=20)
        
        amt = ctk.CTkEntry(frame, placeholder_text="Amount ₱", width=entry_width)
        amt.pack(pady=5, fill="x", padx=20)
        
        pin = ctk.CTkEntry(frame, placeholder_text="PIN", show="*", width=entry_width)
        pin.pack(pady=5, fill="x", padx=20)

        def send():
            ok, msg = self.bank.transfer(rid.get(), amt.get(), pin.get())
            messagebox.showinfo("Result", msg)
            if ok:
                self.showDashboard()
                return
            if self.bank.logged_in_user is None:
                messagebox.showinfo("Session", "Your account has been logged out. Returning to start screen.")
                self.showWelcomeScreen()
                return
            pin.delete(0, 'end')

        ctk.CTkButton(frame, text="Transfer", width=entry_width, fg_color="#e67e22", command=send).pack(pady=20, fill="x", padx=20)
        ctk.CTkButton(frame, text="Back", width=150, fg_color="gray",
                      command=self.showDashboard).pack(pady=10)

    # Transaction Logs
    def showLogsScreen(self):
        self.clearWindow()
        header = ctk.CTkFrame(self, height=80)
        header.pack(fill="x", padx=0, pady=0)
        ctk.CTkLabel(header, text="Transaction History", font=("Arial", 28, "bold")).pack(side="left", padx=20, pady=15)
        ctk.CTkButton(header, text="Back", width=100, fg_color="gray",
                      command=self.showDashboard).pack(side="right", padx=20, pady=15)

        # Filter buttons
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        # Track which filter is active
        self.active_filter = "all"
        
        def update_logs(filter_type):
            self.active_filter = filter_type
            logs = self.bank.getLogs()
            
            # Clear logs_frame
            for widget in logs_frame.winfo_children():
                widget.destroy()
            
            # Filter logs based on type
            if filter_type == "all":
                filtered_logs = logs
            else:
                filtered_logs = [log for log in logs if filter_type.lower() in log['action_type'].lower()]
            
            if not filtered_logs:
                ctk.CTkLabel(logs_frame, text=f"No {filter_type.lower()} transactions yet.", font=("Arial", 16)).pack(pady=30)
                return
            
            for log in filtered_logs:
                item = ctk.CTkFrame(logs_frame)
                item.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(item, text=f"{log['action_type']}", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
                ctk.CTkLabel(item, text=f"Amount: ₱{log['amount']:.2f} | Balance: ₱{log['balance_after']:.2f} | Time: {log['log_time']}",
                             font=("Arial", 11), text_color="gray").pack(anchor="w", padx=10, pady=3)
        
        btn_width = min(150, int(self.winfo_width() * 0.25))
        
        ctk.CTkButton(filter_frame, text="Deposit", width=btn_width, fg_color="#3498db",
                      command=lambda: update_logs("deposit")).pack(side="left", padx=5)
        ctk.CTkButton(filter_frame, text="Withdrawal", width=btn_width, fg_color="#9b59b6",
                      command=lambda: update_logs("withdrawal")).pack(side="left", padx=5)
        ctk.CTkButton(filter_frame, text="Transfer", width=btn_width, fg_color="#e67e22",
                      command=lambda: update_logs("transfer")).pack(side="left", padx=5)
        ctk.CTkButton(filter_frame, text="All", width=btn_width, fg_color="#16a085",
                      command=lambda: update_logs("all")).pack(side="left", padx=5)

        logs_frame = ctk.CTkScrollableFrame(self)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        logs = self.bank.getLogs()

        if not logs:
            ctk.CTkLabel(logs_frame, text="No transactions yet.", font=("Arial", 16)).pack(pady=30)
            return

        for log in logs:
            item = ctk.CTkFrame(logs_frame)
            item.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(item, text=f"{log['action_type']}", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
            ctk.CTkLabel(item, text=f"Amount: ₱{log['amount']:.2f} | Balance: ₱{log['balance_after']:.2f} | Time: {log['log_time']}",
                         font=("Arial", 11), text_color="gray").pack(anchor="w", padx=10, pady=3)

if __name__ == "__main__":
    app = SwiftBankApp()
    app.mainloop()