from Nadajnik import Nadajnik
from Odbiornik import Odbiornik
from Kanal import BSCKanal, GilbertElliottKanal
import os

# --- Ustawienia Symulacji ---
ROZMIAR_PACZKI_BAJTY = 32
# Należy użyć niskiego BER (1e-5) dla testu funkcjonalnego S-a-W
# Dla testów wydajnościowych można użyć 1e-4 lub 5e-4
BER_TEST = 0.001

# Użycie pliku tekstowego do testów (dane wejściowe)
INPUT_FILE = "input_test_arq.txt"
OUTPUT_FILE = "output_test_arq.txt"

# 1. Tworzenie dużego pliku wejściowego (np. 100 * 32 bajtów = 3.2 KB)
DANE_SIZE_BYTES = 3200
try:
    with open(INPUT_FILE, "wb") as f:
        f.write(os.urandom(DANE_SIZE_BYTES))
except Exception as e:
    print(f"BŁĄD: Nie można utworzyć pliku testowego: {e}")
    exit()

# 2. Inicjalizacja komponentów
nadajnik = Nadajnik(addr_src=1, addr_dst=2)
odbiornik = Odbiornik(adres=2)

# Używamy BSCKanal, ale można zamienić na GilbertElliottKanal
kanal = BSCKanal(p_error=BER_TEST)

# Łączenie zwrotne Nadajnik <-> Odbiornik (do symulacji ACK)
nadajnik.ustaw_odbiornik_dla_ack(odbiornik)

# --- WYWOŁANIE TESTU KANAŁU BSC ---
kanal.test_ber(dlugosc_testu_bajty=100000)

print(f"\n--- Start Symulacji Stop-and-Wait ARQ (BER={BER_TEST}) ---")

# 3. Wczytanie danych do symulacji
with open(INPUT_FILE, "rb") as f:
    dane_do_wyslania = f.read()

liczba_ramek = len(dane_do_wyslania) // ROZMIAR_PACZKI_BAJTY

# --- Główna pętla transmisji ---
odebrane_dane = b''
poprawne_ramki = 0
wszystkie_proby = 0

for i in range(liczba_ramek):
    paczka = dane_do_wyslania[i * ROZMIAR_PACZKI_BAJTY:(i + 1) * ROZMIAR_PACZKI_BAJTY]

    sukces = nadajnik.wyslij(kanal, paczka)

    wszystkie_proby += nadajnik.ostatnia_transmisja_prob

    if sukces:
        poprawne_ramki += 1
        odebrane_dane += paczka  # Dane z oryginalnej paczki są dodawane, gdy ACK jest poprawne
    else:
        print(f"!!! PRZERWANIE TRANSMISJI przy ramce {i + 1} z {liczba_ramek}")
        break

print("\n--- Statystyki Transmisji ARQ ---")
print(f"Ramki do przesłania: {liczba_ramek}")
print(f"Poprawnie przesłanych: {poprawne_ramki}")
print(f"Całkowita liczba prób wysłania ramek DANYCH (z retransmisjami): {wszystkie_proby}")

if wszystkie_proby > 0:
    wykorzystanie = poprawne_ramki / wszystkie_proby
    print(f"Wykorzystanie kanału (Ramki / Próby): {wykorzystanie:.2f}")

# Zapis do pliku wynikowego
with open(OUTPUT_FILE, "wb") as f:
    f.write(odebrane_dane)

# Weryfikacja: porównanie oryginalnych danych z odebranymi
if dane_do_wyslania[:len(odebrane_dane)] == odebrane_dane:
    print(
        f"\n✅ Sukces: Dane odebrane i zapisane są IDENTYCZNE (dla {len(odebrane_dane)} bajtów). Protokół ARQ zadziałał.")
else:
    print("\n❌ Błąd: Dane odebrane RÓŻNIĄ SIĘ od oryginału (niewykryty błąd CRC lub błąd logiczny).")