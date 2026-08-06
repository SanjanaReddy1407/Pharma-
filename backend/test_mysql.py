import mysql.connector

try:
    db = mysql.connector.connect(
         host="127.0.0.1",    # Aap 'localhost' bhi likh sakti hain, dono same hain
         user="root",         # Aapke screenshot ke hisaab se
         password="root@1234S",         # Agar 'sanju_tsd' connection banate waqt password dala tha, toh yahan likhiye
         database="pharma"    # Aapka banaya hua naya database
    )
    print("✅ Connected successfully!")
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM medicine;")
    print("Medicine count:", cursor.fetchone()[0])
    db.close()
except mysql.connector.Error as err:
    print("❌ Error:", err)