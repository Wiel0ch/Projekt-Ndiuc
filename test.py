from Nadajnik import Nadajnik
from Odbiornik import Odbiornik
from Kanal import BSCKanal, GilbertElliottKanal

nadajnik = Nadajnik()
odbiornik = Odbiornik()

#Użycie kanału BSC
print("--- TEST KANAŁU BSC ---")
kanal_bsc = BSCKanal(p_error=0.002)
dane = b"Test kanalu BSC, czy wszystko dziala poprawnie?"
wyslane = nadajnik.wyslij(kanal_bsc, dane)
odebrane = odbiornik.odbierz(wyslane)
print("-" * 20 + "\n")


#Użycie kanału Gilberta-Elliotta
print("TEST KANAŁU GILBERTA-ELLIOTTA")

kanal_ge = GilbertElliottKanal(
    p_G=0.0001,   # Prawie idealnie w stanie G
    p_B=0.1,      # 10% błędów w stanie B
    p_GB=0.005,   # Średnio po 1/0.005 = 200 bitach przejście do B
    p_BG=0.1      # Średnio po 1/0.1 = 10 bitach powrót do G
)
daneGE = b"aa."

print("\n--- Transmisja 1 ---")
wyslane1 = nadajnik.wyslij(kanal_ge, daneGE)
odebrane1 = odbiornik.odbierz(wyslane1)

print("\n--- Transmisja 2 ---")
wyslane2 = nadajnik.wyslij(kanal_ge, daneGE)
odebrane2 = odbiornik.odbierz(wyslane2)