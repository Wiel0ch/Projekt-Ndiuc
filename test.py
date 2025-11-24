from Nadajnik import Nadajnik
from Odbiornik import Odbiornik
from Kanal import BSCKanal

# Lista plików do wysłania
pliki_do_wyslania = ["wejscie.txt", "wejscie2.txt", "wejscie3.txt"]

# Inicjalizacja nadajnika, odbiornika i kanału
nadajnik = Nadajnik(addr_src=1, addr_dst=2)
odbiornik = Odbiornik(adres=2)
kanal = BSCKanal(p_error=0.001)  # 2% prawdopodobieństwo błędu

print("\ntransmisja wielu plikow \n")

for idx, plik in enumerate(pliki_do_wyslania, start=1):
    print(f"Transmisja pliku {idx}: {plik}")

    # Wczytanie pliku
    try:
        with open(plik, "rb") as f:
            dane = f.read()
    except FileNotFoundError:
        print(f" Plik {plik} nie znaleziony! Pomijam...")
        continue

    # Wysyłanie ramki
    ramka_po_kanale = nadajnik.wyslij(kanal, dane)

    # Odbiór ramki
    odebrane = odbiornik.odbierz(ramka_po_kanale)

    # Zapis do pliku wynikowego jeśli wszystko OK
    if odebrane:
        plik_wyj = "odb_" + plik
        with open(plik_wyj, "wb") as f:
            f.write(odebrane)
        print(f" Zapisano do: {plik_wyj}\n")
    else:
        print("️ Nic nie zapisano\n")
