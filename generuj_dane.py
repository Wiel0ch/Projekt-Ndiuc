import os
import random

def generuj_pliki():
    print("--- Generowanie plików testowych ---")

    # 1. PROSTY TEKST (Sanity Check)
    # Służy do sprawdzenia, czy system w ogóle działa.
    nazwa_prosty = "test_prosty.txt"
    with open(nazwa_prosty, "wb") as f:
        f.write(b"Czesc! To jest prosty test transmisji.")
    print(f"Utworzono: {nazwa_prosty} (Test podstawowy)")

    # 2. DŁUGI TEKST (Test Fragmentacji i MTU)
    # Wymusza podział na wiele ramek. Jeśli masz MTU=20, a plik ma 500 bajtów,
    # system musi wysłać 25 ramek i poprawnie obsłużyć numery sekwencyjne.
    nazwa_dlugi = "test_dlugi.txt"
    tekst = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 10
    with open(nazwa_dlugi, "wb") as f:
        f.write(tekst)
    print(f"Utworzono: {nazwa_dlugi} (Test fragmentacji, {len(tekst)} bajtów)")

    # 3. TEST BINARNY "KILLER" (Test Byte Stuffing)
    # Zawiera znaki specjalne 0x7E (Flaga) i 0x7D (Escape).
    # Jeśli Twój mechanizm 'stuffingu' w Ramka.py nie działa, ten plik nie przejdzie,
    # ponieważ odbiornik uzna '0x7E' w środku danych za koniec ramki!
    nazwa_trudny = "test_trudny.bin"
    # Tworzymy pułapkę: Flaga w środku danych
    dane_trudne = b"Start" + b"\x7E" + b"Srodek" + b"\x7D" + b"Koniec" + b"\x7E" * 5
    with open(nazwa_trudny, "wb") as f:
        f.write(dane_trudne)
    print(f"Utworzono: {nazwa_trudny} (Test znaków specjalnych/binarnych)")

    # 4. SZUM LOSOWY (Test Stabilności)
    # 1 KB losowych bajtów. Dobre do testowania statystyk błędów.
    nazwa_random = "test_random.bin"
    dane_random = random.randbytes(1024)
    with open(nazwa_random, "wb") as f:
        f.write(dane_random)
    print(f"Utworzono: {nazwa_random} (Test obciążeniowy)")

if __name__ == "__main__":
    generuj_pliki()