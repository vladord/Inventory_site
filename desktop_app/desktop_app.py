import customtkinter as ctk
import requests

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x360")
        self.title("Inventory manager app")

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.database_ip = 'http://127.0.0.1:80'
        self.delivery_page()

    def enter_to_tab(self, event):
        event.widget.tk_focusNext().focus()  # отримуємо наступний віджет і ставимо фокус
        return "break"
            
    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def error_window(self, text):
        # Create a new top-level window
        new_window = ctk.CTkToplevel(self) 
        new_window.title("Помилка!")
        new_window.geometry("300x150")
        new_window.attributes('-topmost', True) 
        # Add a label to the new window
        label = ctk.CTkLabel(new_window, text=text)
        label.pack(pady=20)

        # Optional: Add a button to close the new window
        close_button = ctk.CTkButton(new_window, text="Закрити", command=new_window.destroy)
        close_button.pack(pady=10)


    def delivery_to_user(self, entry, textbox):
        user = entry.get()
        content = textbox.get("0.0", "end-1c")  # Get all text from the textbox
        lines = content.split("\n")    
        for i, line in enumerate(lines, start=1):
            if user == "":
                self.error_window("Введіть отримувача")
                break
            print(f"Row {i}: {line}")

            data = {"user": user, "id": line, "action": "from_stock", "api_user": "desktop_app"}
            try:
                patch_request = requests.patch(self.database_ip, json=data)
                if patch_request.status_code != 200:
                    self.error_window(f"Couldn't change row №{i} \n error code {patch_request} \n {patch_request.json()}")
            except Exception as e:
                self.error_window(f"Check if site is turned on")

            print (f"Response status code: {patch_request} \n Data: {patch_request.json()}")

    def return_to_stock(self, textbox):
        content = textbox.get("0.0", "end-1c")  # Get all text from the textbox
        lines = content.split("\n")    
        for i, line in enumerate(lines, start=1):
            print(f"Row {i}: {line}")

            data = {"id": line, "action": "to_stock", "api_user": "desktop_app"}
            patch_request = requests.patch(self.database_ip, json=data)
            print (f"Response status code: {patch_request} \n Data: {patch_request.json()}")

    def buttons(self):
        delivery_page_button = ctk.CTkButton(self.frame, text="Видача", command=lambda: self.delivery_page())
        delivery_page_button.place(relx=0.25, rely=0.2, anchor="center")

        return_page_button = ctk.CTkButton(self.frame, text="Повернення", command=lambda: self.return_page())
        return_page_button.place(relx=0.25, rely=0.3, anchor="center")

    def delivery_page(self):
        self.clear_frame()

        label = ctk.CTkLabel(self.frame, width=150, height=200, text="Форма видачі")
        label.place(relx=0.25, rely=0.07, anchor="center")

        item_textbox = ctk.CTkTextbox(self.frame, width=150, height=200)
        item_textbox.place(relx=0.7, rely=0.45, anchor="center")

        user_entry = ctk.CTkEntry(self.frame, placeholder_text="Отримувач")
        user_entry.bind("<Return>", self.enter_to_tab)
        user_entry.place(relx=0.7, rely=0.07, anchor="center")

        button = ctk.CTkButton(self.frame, text="Видати", command=lambda: self.delivery_to_user(user_entry, item_textbox))
        button.place(relx=0.7, rely=0.85, anchor="center")
        self.buttons()

    def return_page(self):
        self.clear_frame()

        label = ctk.CTkLabel(self.frame, width=150, height=200, text="Форма отримання")
        label.place(relx=0.25, rely=0.07, anchor="center")

        item_textbox = ctk.CTkTextbox(self.frame, width=150, height=200)
        item_textbox.place(relx=0.7, rely=0.45, anchor="center")

        button = ctk.CTkButton(self.frame, text="Повернути", command=lambda: self.return_to_stock(item_textbox))
        button.place(relx=0.7, rely=0.85, anchor="center")
        self.buttons()

if __name__ == "__main__":
    app = App()
    app.resizable(False, False)
    app.mainloop()