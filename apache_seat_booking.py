import customtkinter as ctk  #imports customtkinter for GUI
from tkinter import messagebox, simpledialog #imports messagebox and simpledialog from tkinter for errors and user information
import sqlite3 #imports SQL for data management
import random #imports random and string for reference number generation
import string

class SeatBookingApp: # a class for the GUI and base functionalities
    def __init__(self):
        self.root = ctk.CTk() #creates a window
        self.root.title("Apache Airlines - Seat Booking") #gives the window a title
        self.root.geometry("600x600") #determines the size of window
        ctk.set_appearance_mode("dark") #sets the appearence mode to dark
        
        self.passenger_db = PassengerDatabase() #initializes a database to store passenger information
        
        self.seats = {} #a dictionary that stores reference numbers in seats
        for row in range(1, 81): #iterate from 1 to 80
            for col in "ABCDEF": #creates columns of letters for seats until the 77th row
                if col in "D" and row >= 77:
                    self.seats[f"{row}{col}"] = "S" #places storage areas after 77th row
                elif col in "E" and row >= 77:
                    self.seats[f"{row}{col}"] = "S"  
                elif col == "X":
                    self.seats[f"{row}{col}"] = "X"  #places aisles
                else:
                    self.seats[f"{row}{col}"] = "F"  #sets all seats to free
                    
        self.selected_seats = [] # a list that stores selected seats
        self.original_states = {} #a dictionary that stores the original states of seats if anything is canceled 
        self.booking_mode = False #keeps track of booking mode
        self.freeing_mode = False #keeps track of freeing mode
        self.create_widgets() #creates all the widgets
        self.load_booked_seats() #loads the information stored in the dataset

    def create_widgets(self):
        self.menu_frame = ctk.CTkFrame(self.root, width=150) #creates a menu frame on the left and packs it
        self.menu_frame.pack(side="left", fill="y")
        
        #Labels and buttons on the menu frame
        ctk.CTkLabel(self.menu_frame, text="Menu", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="Check Availability", command=self.check_availability).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="Book Seat", command=self.book_seat).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="Free Seat", command=self.free_seat).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="Show Booking Status", command=self.show_status).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="Exit", command=self.root.destroy).pack(pady=5)
        #a label that displays the current selected seat
        self.selected_label = ctk.CTkLabel(self.menu_frame, text="Selected: None", wraplength=140)
        self.selected_label.pack(pady=10)
        #confirm and cancel buttons for bookings and freeings (not packed yet)
        self.confirm_button = ctk.CTkButton(self.menu_frame, text="Confirm Booking", command=self.confirm_booking)
        self.cancel_button = ctk.CTkButton(self.menu_frame, text="Cancel Booking", command=self.cancel_booking)
        self.confirm_free_button = ctk.CTkButton(self.menu_frame, text="Confirm Freeing", command=self.confirm_freeing)
        self.cancel_free_button = ctk.CTkButton(self.menu_frame, text="Cancel Freeing", command=self.cancel_freeing)
        #creates a scrollable frame on the right to display the seating plan
        self.canvas = ctk.CTkCanvas(self.root, width=400, height=500)
        self.scrollbar = ctk.CTkScrollbar(self.root, command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        #allows user to scroll on the canvas
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        #gives the canvas the command of scrolling
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.buttons = {}
        for row in range(1, 81):
            row_frame = ctk.CTkFrame(self.scrollable_frame)
            row_frame.pack(pady=2)
            for col in "ABCXDEF": #iterates through the letters and determines a seat id
                seat_id = f"{row}{col}"
                if col == "X": #if it encounters X or S it creates labels because no bookings should be made there
                    btn = ctk.CTkLabel(row_frame, text="X", width=50, fg_color="gray")
                elif seat_id in self.seats and self.seats[seat_id] == "S":
                    btn = ctk.CTkLabel(row_frame, text="S", width=50, fg_color="yellow")
                else: #creates every button with the toggle seat command and adds it to self.buttons
                    btn = ctk.CTkButton(row_frame, text=seat_id, width=50, fg_color="green", command=lambda s=seat_id: self.toggle_seat(s))
                    self.buttons[seat_id] = btn
                btn.pack(side="left", padx=5) #packs all buttons
        
        self.canvas.pack(side="left", fill="both", expand=True) #packs the canavs and scrollbar
        self.scrollbar.pack(side="right", fill="y")

    def toggle_seat(self, seat): 
        if self.booking_mode: #if the app is on booking mode when a seat is clicked
            if seat in self.selected_seats: #if the seat is in selected seats already
                self.selected_seats.remove(seat) #removes the seat from selected seats
                self.buttons[seat].configure(fg_color=self.original_states[seat]) #switches its colour back to its original state
            else:
                self.original_states[seat] = "green" if self.seats[seat] == "F" else "red" 
                self.selected_seats.append(seat) #adds it to selected seats to keep track 
                self.buttons[seat].configure(fg_color="red") #sets the colour to red 

        elif self.freeing_mode: #if the app is on freeing mode when a seat is clicked
            if seat in self.selected_seats: #if the seat is in selected seats already
                self.selected_seats.remove(seat)#removes the seat from selected seats
                self.buttons[seat].configure(fg_color=self.original_states[seat])#switches its colour back to its original state
            else:
                self.original_states[seat] = "red" if self.seats[seat] != "F" else "green"
                self.selected_seats.append(seat) #adds it to selected seats
                self.buttons[seat].configure(fg_color="green") #changes colour to green

        self.update_selected_label() #updates label every time a seat is clicked
    
    def book_seat(self):
        self.booking_mode = True #sets booking mode to true and waits for seat selection
        self.freeing_mode = False #sets freeing mode to false to prevent intersection of functionalities
        self.cancel_freeing()
        self.selected_seats.clear() #clears selected seats
        self.original_states.clear() #clears original states
        self.update_selected_label() #updates the selected lable
        self.confirm_button.pack(pady=5) #packs the confirm and cancel buttons for booking
        self.cancel_button.pack(pady=5)

    def free_seat(self):
        self.freeing_mode = True #sets freeing mode to true and waits for seat selection
        self.booking_mode = False #sets booking mode to false to prevent intersection of functionalities
        self.cancel_booking()
        self.selected_seats.clear() #clears everything again
        self.original_states.clear()
        self.update_selected_label()
        self.confirm_free_button.pack(pady=5) #packs the confirm and cancel buttons for freeing
        self.cancel_free_button.pack(pady=5)

    def confirm_booking(self):
        #asks the user for their information when a booking is confirmed
        passport = simpledialog.askstring("Passenger Info", "Enter Passport Number:", parent=self.root) 
        first_name = simpledialog.askstring("Passenger Info", "Enter First Name:", parent=self.root)
        last_name = simpledialog.askstring("Passenger Info", "Enter Last Name:", parent=self.root)
    
        if not self.selected_seats: #if no seats are selected an error is shown
            messagebox.showwarning("No Selection", "Please select at least one seat to book.")
            return
        
        for seat in self.selected_seats: #iterates through the selected seats
            if self.passenger_db.is_seat_booked(seat): #uses the is_seat_booked function to check if the seat is already booked in the database
                messagebox.showerror("Booking Error", f"Seat {seat} is already booked. Booking canceled.")
                self.cancel_booking() #shows an error and cancels booking if seat is already booked
                return 
        
        for seat in self.selected_seats: #iterates through selected seats
            booking_ref = self.passenger_db.generate_booking_reference() #generates a booking reference for each seat
            self.passenger_db.book_seat(booking_ref, passport, first_name, last_name, seat) #books a seat for the passenger and stores it in the database
            self.seats[seat] = booking_ref #stores the bookinf reference in the data structure
            self.buttons[seat].configure(fg_color="red") #changes the colour of seat to red
    
        self.selected_seats.clear() #clears selected seats 
        self.booking_mode = False #sets booking mode to false
        self.update_selected_label() #updates label
        self.confirm_button.pack_forget() #confirm and cancel buttons disappear
        self.cancel_button.pack_forget()
    
        messagebox.showinfo("Booking Success", "Seats booked successfully!") #success message is shown

    def confirm_freeing(self):
        passport = simpledialog.askstring("Passenger Info", "Enter Passport Number:", parent=self.root) #asks the user for their info 
        first_name = simpledialog.askstring("Passenger Info", "Enter First Name:", parent=self.root)
        last_name = simpledialog.askstring("Passenger Info", "Enter Last Name:", parent=self.root)
    
        if not self.selected_seats: #if no seat is selected error is shown
            messagebox.showwarning("No Selection", "Please select a seat to free.")
            return
        
        for seat in self.selected_seats: #iterates through the selected seats
            booking = self.passenger_db.get_booking_info(seat) #gets the booking info from the database
            
            if booking and (booking[0] == passport and booking[1] == first_name and booking[2] == last_name):
                #if the info of the user matches the info stored, it frees the seat 
                self.passenger_db.free_seat(seat)
                self.seats[seat] = "F"
                self.buttons[seat].configure(fg_color="green")#changes colour to green and stores F
            else:
                messagebox.showerror("Error", f"Incorrect details for seat {seat}. Freeing canceled.")
                self.cancel_freeing() #shows error and cancels freeing if info does not match
                return
    
        self.selected_seats.clear() #clears all and buttons disappear
        self.freeing_mode = False
        self.update_selected_label()
        self.confirm_free_button.pack_forget()
        self.cancel_free_button.pack_forget()

    def cancel_booking(self):
        #if a booking is canceled buttons revert back to their original states
        for seat in self.selected_seats:
            self.buttons[seat].configure(fg_color=self.original_states[seat])

        self.selected_seats.clear()
        self.booking_mode = False #everything is cleared and booking mode is set back to false
        self.update_selected_label()
        self.confirm_button.pack_forget()
        self.cancel_button.pack_forget()

    def cancel_freeing(self):
        for seat in self.selected_seats: #seats revert back to their original states if freeing is canceled
            self.buttons[seat].configure(fg_color=self.original_states[seat])

        self.selected_seats.clear()
        self.freeing_mode = False #everything is cleared and freeing mode is set back to false
        self.update_selected_label()
        self.confirm_free_button.pack_forget()
        self.cancel_free_button.pack_forget()

    def update_selected_label(self): #updates the label every time a seat is clicked
        self.selected_label.configure(text=f"Selected: {', '.join(self.selected_seats) if self.selected_seats else 'None'}")

    def check_availability(self): #iterates through all the seats
        available_seats = [seat for seat, status in self.seats.items() if status == "F"]
        booked_seats = [seat for seat, status in self.seats.items() if status != "F" and status != "S"]
        #displays a message showing the number of available seats and booked seats
        message = f"Available Seats: {len(available_seats)}\nBooked Seats: {len(booked_seats)}"
        messagebox.showinfo(title="Seat Availability", message=message)


    def show_status(self): 
        booked_seats = [seat for seat, status in self.seats.items() if status != "F" and status != "S"]
        #iterates through the booked seats and shows the user which seats are booked by name
        if booked_seats:
            message = f"Booked Seats:\n{', '.join(booked_seats)}"
        else: #says no seats are booked if none are booked
            message = "No seats are booked yet."
        #a message box that shows the current status
        messagebox.showinfo(title="Booking Status", message=message)
        
    def load_booked_seats(self): 
        booked_seats = self.passenger_db.get_booked_seats() #gets the stored booked seats and booking references
        booking_refs = self.passenger_db.get_booking_references()
        for seat in booked_seats: #loads all the stored data of booked seats, stores booking references and changes their colours 
            self.seats[seat] = booking_refs
            self.buttons[seat].configure(fg_color="red")
   
class PassengerDatabase:
    def __init__(self): #creates a database that stores the information
        self.conn = sqlite3.connect('passenger_info.db')
        self.create_tables() #creates tables in the dataset
    
    def create_tables(self):
        cursor = self.conn.cursor() 
        cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
            booking_ref TEXT PRIMARY KEY,
            passport_number TEXT NOT NULL,  
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            seat TEXT NOT NULL UNIQUE)''') #a SQL query that creates a table that will store the info of passengers
        self.conn.commit()
    
    def get_booked_seats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT seat FROM bookings") #gets the booked seats from the database
        return [row[0] for row in cursor.fetchall()]

    def generate_booking_reference(self):
        while True: #generates a random booking reference with 8 alphanumeric characters
            reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not self.conn.execute("SELECT * FROM bookings WHERE booking_ref = ?", (reference,)).fetchone():
                return reference
    
    def get_booking_references(self):
        cursor = self.conn.cursor() 
        cursor.execute("SELECT booking_ref FROM bookings") #gets all booking references from the database to load them
        return [row[0] for row in cursor.fetchall()]
    
    def book_seat(self, ref, passport, first_name, last_name, seat):
        self.conn.execute("INSERT INTO bookings VALUES (?, ?, ?, ?, ?)", (ref, passport, first_name, last_name, seat))
        self.conn.commit() #inserts the information of the user to the database when the user confirms a booking
    
    def free_seat(self, seat):
        self.conn.execute("DELETE FROM bookings WHERE seat = ?", (seat,))
        self.conn.commit() #deletes the information of the user from the seat if the user frees a seat
        
    def get_booking_info(self, seat):
        cursor = self.conn.cursor() #gets the passport number, first name and last name of user
        cursor.execute("SELECT passport_number, first_name, last_name FROM bookings WHERE seat = ?", (seat,))
        return cursor.fetchone() #used in freeing a seat, checks if the user info matches the info stored on the booked seat
    
    def is_seat_booked(self, seat):
        cursor = self.conn.cursor() #checks if the seat is already booked in the database
        cursor.execute("SELECT seat FROM bookings WHERE seat = ?", (seat,))
        return cursor.fetchone() is not None  
    
app = SeatBookingApp()
app.root.mainloop() #runs the app