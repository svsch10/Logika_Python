# Онлайн-чат_клієнт вдосконалений

from customtkinter import *
from socket import *
from threading import Thread
from tkinter.messagebox import *
from emoji import *

#---Головне вікно програми---
class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        
        #---Головне вікно програми---
        self.geometry('400x300')
        self.title('Онлайн-чат')
        self.minsize(400, 300)
        
        #---Фрейм висувного меню налаштувань---
        self.frame = CTkFrame(self, width=200,
                              height=self.winfo_height())
        self.frame.pack_propagate(False)
        self.frame.configure(width=0)
        self.is_show_menu = False
        self.frame_speed = 20
        self.frame_width = 0
        self.frame.place(x=0, y=0)
        
        #---Кнопка виклику меню---
        self.btn = CTkButton(self, text='Меню ▶', width=30,
                             command=self.toggle_show_menu)
        self.btn.place(x=0, y=0)
        
        #---Меню програми---
        self.label = CTkLabel(self.frame, text='Налаштування:')
        self.label.pack(pady=30)
        self.name_entry = CTkEntry(self.frame, state='normal',
                              placeholder_text="Ім'я/нікнейм")
        self.name_entry.pack()
        self.signup_btn = CTkButton(self.frame, text='Зареєструватися',
                                    command=self.sign_up)
        self.signup_btn.pack(pady=10)
        self.signout_btn = CTkButton(self.frame, text='Вийти з чату',
                                     command=self.sign_out)
        self.signout_btn.pack(pady=10)
        self.theme = CTkOptionMenu(self.frame,
                                   values=['Темна тема', 'Світла тема'],
                                   command=self.change_theme)
        self.theme.pack(pady=10)
        
        #---Вікно чату---
        self.chat_text = CTkTextbox(self, state='disabled',
                                    wrap='word', font=('Arial', 16))
        self.chat_text.place(x=0, y=30)
        
        self.message_entry = CTkEntry(
            self, placeholder_text='Введіть повідомлення',
            width=200, state='disabled'
        )
        self.message_entry.bind('<1>', self.false_attempt)
        self.message_entry.place(x=0, y=250)
        
        self.emoji_button = CTkButton(
            self, text=f"{emojize(':grinning_face:')}",
            font=('Segoe UI Emoji', 14), width=50, height=30,
            command=self.enter_emoji
        )
        self.emoji_button.place(x=200, y=250)
        
        self.send_button = CTkButton(self, text='>>',
                                     width=50, height=30,
                                     state='disabled',
                                     command=self.send_message)
        
        self.send_button.place(x=250, y=250)
        
        self.username = ''
        self.registration = False
        
        self.adaptive_ui()
        
    #---ПРОЦЕДУРИ І ФУНКЦІЇ---
        
    #---Перемикання меню налаштувань чату---
    def toggle_show_menu(self):
        if self.is_show_menu == True:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()
    
    #---Відкрити меню---
    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += self.frame_speed
            self.frame.configure(
                width=self.frame_width, height=self.winfo_height()
            )
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='◀ Меню')
        if self.is_show_menu:
            self.after(20, self.show_menu)
    
    #---Закрити меню---
    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= self.frame_speed
            self.frame.configure(width=self.frame_width)
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='Меню ▶')
        if not self.is_show_menu:
            self.after(20, self.close_menu)

    #---Адаптивний інтерфейс---
    def adaptive_ui(self):
        self.chat_text.configure(
            width=self.winfo_width()-self.frame.winfo_width(),
            height=self.winfo_height()-self.send_button.winfo_height()-30
        )
        self.chat_text.place(x=self.frame.winfo_width())
        
        self.message_entry.configure(
            width=self.winfo_width()
            -self.frame.winfo_width()
            -self.send_button.winfo_width()
            -self.emoji_button.winfo_width()
        )
        self.message_entry.place(
            x=self.frame.winfo_width(),
            y=self.winfo_height()-self.message_entry.winfo_height()
        )
        
        self.send_button.place(
            x=self.winfo_width()-self.send_button.winfo_width(),
            y=self.winfo_height()-self.send_button.winfo_height()
        )
        
        self.emoji_button.place(
            x=self.winfo_width()
              -self.send_button.winfo_width()
              -self.emoji_button.winfo_width(),
            y=self.winfo_height()-self.send_button.winfo_height()
        )
        
        if self.frame.winfo_width() > self.btn.winfo_width():
            self.btn.place(x=self.frame.winfo_width()-self.btn.winfo_width())
 
        self.after(20, self.adaptive_ui)
    
    #---Зміна теми інтерфейсу---
    def change_theme(self, value):
        if value == 'Темна тема':
            set_appearance_mode('dark')
        elif value == 'Світла тема':
            set_appearance_mode('light')
        else:
            set_appearance_mode('system')    
    
    def false_attempt(self, event):
        if self.registration == False:
            showerror('ПОМИЛКА!', 'Ви не зареєстровані в чаті\nВідкрийте меню')
    
    def enter_emoji(self):
        message = self.message_entry.get()
        message = message + f"{emojize(':grinning_face:')}"
        # https://www.webfx.com/tools/emoji-cheat-sheet/
        self.message_entry.delete(0, END)
        self.message_entry.insert(END, message)
    
    #---Реєстрація в чаті---
    def sign_up(self):
        global registration
        try:
            if self.name_entry.get() == '':
                showerror('ПОМИЛКА!', 'Поле імені порожнє!')
            else:
                self.client_socket = socket(AF_INET, SOCK_STREAM)
                self.client_socket.connect((HOST, PORT))
                t = Thread(target=self.recv_message, daemon=True)
                t.start()
                self.username = self.name_entry.get().strip()
                hello = f'{self.username} приєднується'
                self.client_socket.sendall(hello.encode())
                self.name_entry.configure(state='disabled')
                self.signup_btn.configure(state='disabled')
                self.message_entry.configure(state='normal')
                self.send_button.configure(state='normal')
                self.add_message(f'Нікнейм: {self.username}')
                self.registration = True
                showinfo('ВІТАЄМО!', 'Реєстрація успішна')
        except Exception as e:
            self.add_message(f'Не вдалося приєднатися до чату: ' + str(e))
    
    #---Вихід з чату---
    def sign_out(self):
        global registration
        bye = f'{self.username} виходить з чату'
        self.client_socket.sendall(bye.encode())
        self.add_message('Ви вийшли з чату')
        self.registration = False
        self.name_entry.configure(state='normal')
        self.signup_btn.configure(state='normal')
        self.message_entry.configure(state='disabled')
        self.send_button.configure(state='disabled')
        self.client_socket.close()
    
    #---Надсилання повідомлення в чат---
    def send_message(self):
        message = self.message_entry.get()
        if message != '':
            text = f'{self.username}: {message}'
            try:
                self.client_socket.sendall(text.encode())
                if f'{self.username}:' in text:
                    text = text.replace(f'{self.username}:', 'Я:')
                self.add_message(text)
            except Exception as e:
                self.add_message(str(e))
                #pass
        self.message_entry.delete(0, END)

    #---Додати текст повідомлення в своє вікно чату---
    def add_message(self, text):
        self.chat_text.configure(state='normal')
        self.chat_text.insert(END, text + '\n')
        self.chat_text.configure(state='disabled')
    
    #---Отримати повідомлення---
    def recv_message(self):
        while True:
            try:
                message = self.client_socket.recv(4096).decode().strip()
                if message != '':
                    self.add_message(message)
            except:
                break
    
#---Взаємодія з програмою-сервером---
HOST = '127.0.0.1'
PORT = 8080

window = MainWindow()
window.mainloop()