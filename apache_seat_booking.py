import customtkinter as ctk 
from tkinter import messagebox
import sqlite3

class SeatBookingApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Apache Airlines - Seat Booking")
        self.root.geometry("600x600")
        ctk.set_appearance_mode("dark")

        # Seat status: "F" = Free, "R" = Reserved, "S" = Special, "X" = Not available
        self.seats = {}
        for row in range(1, 81):
            for col in "ABCDEF":
                if col in "D" and row >= 77:
                    self.seats[f"{row}{col}"] = "S"
                elif col in "E" and row >= 77:
                    self.seats[f"{row}{col}"] = "S"  
                elif col == "X":
                    self.seats[f"{row}{col}"] = "X"  
                else:
                    self.seats[f"{row}{col}"] = "F"  
                    
        self.selected_seats = []
        self.original_states = {}
        self.booking_mode = False
        self.freeing_mode = False
        self.create_widgets()

    def create_widgets(self):
        self.menu_frame = ctk.CTkFrame(self.root, width=150)
        self.menu_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.menu_frame, text="Menu", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="Check Availability", command=self.check_availability).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="Book Seat", command=self.book_seat).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="Free Seat", command=self.free_seat).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="Show Booking Status", command=self.show_status).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="Exit", command=self.root.destroy).pack(pady=5)

        self.selected_label = ctk.CTkLabel(self.menu_frame, text="Selected: None", wraplength=140)
        self.selected_label.pack(pady=10)

        self.confirm_button = ctk.CTkButton(self.menu_frame, text="Confirm Booking", command=self.confirm_booking)
        self.cancel_button = ctk.CTkButton(self.menu_frame, text="Cancel Booking", command=self.cancel_booking)
        
        self.confirm_free_button = ctk.CTkButton(self.menu_frame, text="Confirm Freeing", command=self.confirm_freeing)
        self.cancel_free_button = ctk.CTkButton(self.menu_frame, text="Cancel Freeing", command=self.cancel_freeing)
        
        self.canvas = ctk.CTkCanvas(self.root, width=400, height=500)
        self.scrollbar = ctk.CTkScrollbar(self.root, command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.buttons = {}
        for row in range(1, 81):
            row_frame = ctk.CTkFrame(self.scrollable_frame)
            row_frame.pack(pady=2)
            for col in "ABCXDEF":  
                seat_id = f"{row}{col}"
                if col == "X":
                    btn = ctk.CTkLabel(row_frame, text="X", width=50, fg_color="gray")
                elif seat_id in self.seats and self.seats[seat_id] == "S":
                    btn = ctk.CTkLabel(row_frame, text="S", width=50, fg_color="yellow")
                else:
                    btn = ctk.CTkButton(row_frame, text=seat_id, width=50, fg_color="green", command=lambda s=seat_id: self.toggle_seat(s))
                    self.buttons[seat_id] = btn
                btn.pack(side="left", padx=5)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def toggle_seat(self, seat):
        if self.booking_mode:
            if seat in self.selected_seats:
                self.selected_seats.remove(seat)
                self.buttons[seat].configure(fg_color=self.original_states[seat])
            else:
                self.original_states[seat] = "green" if self.seats[seat] == "F" else "red"
                self.selected_seats.append(seat)
                self.buttons[seat].configure(fg_color="red")

        elif self.freeing_mode:
            if seat in self.selected_seats:
                self.selected_seats.remove(seat)
                self.buttons[seat].configure(fg_color=self.original_states[seat])
            else:
                self.original_states[seat] = "red" if self.seats[seat] == "R" else "green"
                self.selected_seats.append(seat)
                self.buttons[seat].configure(fg_color="green")

        self.update_selected_label()
    
    def book_seat(self):
        self.booking_mode = True
        self.freeing_mode = False
        self.cancel_freeing()
        self.selected_seats.clear()
        self.original_states.clear()
        self.update_selected_label()
        self.confirm_button.pack(pady=5)
        self.cancel_button.pack(pady=5)

    def free_seat(self):
        self.freeing_mode = True
        self.booking_mode = False
        self.cancel_booking()
        self.selected_seats.clear()
        self.original_states.clear()
        self.update_selected_label()
        self.confirm_free_button.pack(pady=5)
        self.cancel_free_button.pack(pady=5)

    def confirm_booking(self):
        for seat in self.selected_seats:
            self.seats[seat] = "R"
            self.buttons[seat].configure(fg_color="red")
        self.selected_seats.clear()
        self.booking_mode = False
        self.update_selected_label()
        self.confirm_button.pack_forget()
        self.cancel_button.pack_forget()

    def confirm_freeing(self):
        for seat in self.selected_seats:
            self.seats[seat] = "F"
            self.buttons[seat].configure(fg_color="green")
        self.selected_seats.clear()
        self.freeing_mode = False
        self.update_selected_label()
        self.confirm_free_button.pack_forget()
        self.cancel_free_button.pack_forget()

    def cancel_booking(self):
        # Restore only the seats selected in the current session
        for seat in self.selected_seats:
            self.buttons[seat].configure(fg_color=self.original_states[seat])

        self.selected_seats.clear()
        self.booking_mode = False
        self.update_selected_label()
        self.confirm_button.pack_forget()
        self.cancel_button.pack_forget()

    def cancel_freeing(self):
        for seat in self.selected_seats:
            self.buttons[seat].configure(fg_color=self.original_states[seat])

        self.selected_seats.clear()
        self.freeing_mode = False
        self.update_selected_label()
        self.confirm_free_button.pack_forget()
        self.cancel_free_button.pack_forget()

    def update_selected_label(self):
        self.selected_label.configure(text=f"Selected: {', '.join(self.selected_seats) if self.selected_seats else 'None'}")

    def check_availability(self):
        available_seats = [seat for seat, status in self.seats.items() if status == "F"]
        booked_seats = [seat for seat, status in self.seats.items() if status == "R"]
    
        message = f"Available Seats: {len(available_seats)}\nBooked Seats: {len(booked_seats)}"
        messagebox.showinfo(title="Seat Availability", message=message)


    def show_status(self):
        booked_seats = [seat for seat, status in self.seats.items() if status == "R"]
    
        if booked_seats:
            message = f"Booked Seats:\n{', '.join(booked_seats)}"
        else:
            message = "No seats are booked yet."
    
        messagebox.showinfo(title="Booking Status", message=message)
        
app = SeatBookingApp()
app.root.mainloop()






