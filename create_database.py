"""
    this code on local hast...
    soo please tern on your MySql first(XAMPP Control Panel)
    then run server 1- ServerseitigesSkript.py and 2- ClientseitigesSkript.py

"""

import mysql.connector

import banner


def create_database():
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password=""
    )

    mycursor = mydb.cursor()

    mycursor.execute("CREATE DATABASE chat_app")


def create_table():
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="chat_app"
    )
    # my banner
    banner.banner()

    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE userconnect (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")
