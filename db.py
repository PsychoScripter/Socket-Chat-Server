"""
    this code on local hast...
    soo please tern on your MySql first(XAMPP Control Panel)
    then run server 1- ServerseitigesSkript.py and 2- ClientseitigesSkript.py

"""

import mysql.connector


class my_db:
    def __init__(self):

        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chat_app"
        )

    def add_users(self, username, password):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO userconnect (username, password) VALUES (%s, %s)"
        val = (username, password)
        mycursor.execute(sql, val)
        self.mydb.commit()

    def login_page(self, username, password):
        mycursor = self.mydb.cursor()
        sql = "SELECT id, username, password FROM userconnect where username = %s and password = %s"
        val = (username, password)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        self.mydb.commit()
        return myresult

    def check_password(self, username, password):
        users = self.login_page(username, password)
        for user in users:
            if username == user[1] and password == user[2]:
                return True
            return False