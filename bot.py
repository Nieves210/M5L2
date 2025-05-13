from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN

# Veri tabanı yöneticisini başlatma
manager = DB_Map("database.db")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot başlatıldı!")

@bot.command()
async def start(ctx: commands.Context):
    await ctx.send(f"Merhaba, {ctx.author.name}. Mevcut komutların listesini keşfetmek için !help_me yazın.")

@bot.command()
async def help_me(ctx: commands.Context):
    await ctx.send(
        "!start - Botu başlatın ve hoş geldiniz mesajı alın.\n"
        "!help_me - Mevcut komutların listesini alın.\n"
      "!show_city <şehir_adı>- Verilen şehri haritada görüntüleyin.\n"
       "!remember_city <şehir_adı> - Verilen şehri kaydedin.")

@bot.command()
async def show_city(ctx: commands.Context, *, city_name:str ="", marker_color:str =""):
    if not city_name:
        await ctx.send("Hatalı format. Lütfen şehir adını İngilizce ve komuttan sonra bir boşluk bırakarak girin.")
        return
    manager.create_graph(f'{ctx.author.id}.png', [city_name], marker_color)
    await ctx.send(file=discord.File(f'{ctx.author.id}.png'))
                   
@bot.command()
async def show_my_cities(ctx: commands.Context):
    cities = manager.select_cities(ctx.author.id)  # Kullanıcının kaydettiği şehirlerin listesini alma
    if cities:
        manager.create_graph(f'{ctx.author.id}.png', cities)
    await ctx.send(file=discord.File(f'{ctx.author.id}_cities.png'))
    # Kullanıcının şehirleriyle birlikte haritayı gösterecek komutu yazın

@bot.command()
async def remember_city(ctx: commands.Context, *, city_name=""):
    if manager.add_city(ctx.author.id, city_name):  # Şehir adının format uygunluğunu kontrol etme. Başarılıysa şehri kaydet!
        await ctx.send(f'{city_name} şehri başarıyla kaydedildi!')
    else:
        await ctx.send("Hatalı format. Lütfen şehir adını İngilizce olarak ve komuttan sonra bir boşluk bırakarak girin.")





if __name__ == "__main__":
    bot.run(TOKEN)
