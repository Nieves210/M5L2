import sqlite3
import matplotlib
import cartopy.feature as cfeature
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz


matplotlib.use('Agg')  # Matplotlib arka planını, pencere göstermeden dosyaları bellekte kaydetmek için ayarlama
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  # Harita projeksiyonlarıyla çalışmamızı sağlayacak modülü içe aktarma

class DB_Map():
    def __init__(self, database):
        self.database = database  # Veri tabanı yolunu belirleme

    def create_user_table(self):
        conn = sqlite3.connect(self.database)  # Veri tabanına bağlanma
        with conn:
            # Kullanıcı şehirlerini depolamak için bir tablo oluşturma (eğer yoksa)
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  # Değişiklikleri onaylama

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Veri tabanında şehir adına göre sorgulama yapma
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Şehri kullanıcının şehir listesine ekleme
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  # İşlemin başarılı olduğunu belirtme
            else:
                return 0  # Şehir bulunamadı

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Kullanıcının tüm şehirlerini seçme
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  # Kullanıcının şehir listesini döndürme

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Şehrin adına göre koordinatlarını alma
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  # Şehrin koordinatlarını döndürme
        
    def get_cities_by_country(self, country_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city FROM cities WHERE country = ?", (country_name,))
            return [row[0] for row in cursor.fetchall()]
        
    def get_cities_by_density(self, descending=True):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            order = "DESC" if descending else "ASC"
            cursor.execute(f"SELECT city, population_density FROM cities ORDER BY population_density {order}")
            return cursor.fetchall()

    def get_local_time(self, lat, lng):
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=lat, lng=lng)
        if not tz_name:
            return "Unknown"
        tz = pytz.timezone(tz_name)
        return datetime.now(tz).strftime("%H:%M")

    def create_graph(self, path, cities, marker_color):
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        ax.add_feature(cfeature.LAND, facecolor='lightgreen')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        for city in cities:
            coordinates=self.get_coordinates(city)
            if coordinates:
                lat, lng=coordinates
                time_str = self.get_local_time(lat, lng)
                plt.plot([lat],[lng], color= marker_color, marker="o", transform=ccrs.Geodetic(), linewidth=1)
                plt.text(lng+3, lat+12, city, horizontalallignment="left",transform=ccrs.Geodetic)
        plt.savefig(path)
        plt.close()
        

    def draw_distance(self, city1, city2):
        # İki şehir arasındaki mesafeyi göstermek için bir çizgi çizme
        city1_coords=self.get_coordinates(city1)
        city2_coords=self.get_coordinates(city2)
        fig,ax=plt.subplots(subplot_kw={"projection":ccrs.PlateCarree()})
        ax.stock_img()
        plt.plot([city1_coords[1], city2_coords[1]],[city1_coords[0], city2_coords[0]], color="red", marker="o", transform=ccrs.Geodetic(), linewidth=2)
        plt.text(city1_coords[1]+3, city1_coords[0]+12, city1, horizontalallignment="left",transform=ccrs.Geodetic)
        plt.text(city2_coords[1]+3, city2_coords[0]+12, city2, horizontalallignment="left",transform=ccrs.Geodetic)
        plt.savefig("distance_map.png")
        plt.close()

if __name__ == "__main__":
    m = DB_Map("database.db")  # Veri tabanıyla etkileşime geçecek bir nesne oluşturma
    m.create_user_table()   # Kullanıcı şehirleri tablosunu oluşturma (eğer zaten yoksa)
