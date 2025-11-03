from Nadajnik import Nadajnik
from Odbiornik import Odbiornik
from Kanal import BSCKanal

nadajnik = Nadajnik()
odbiornik = Odbiornik()

kanal = BSCKanal(p_error=0.002)

dane = b"skibidibi sigma 67 b"
wyslane = nadajnik.wyslij(kanal, dane)
odebrane = odbiornik.odbierz(wyslane)
