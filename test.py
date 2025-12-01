import os
from Nadajnik import Nadajnik
from Odbiornik import Odbiornik
from Kanal import BSCKanal, GilbertElliottKanal


def run_test():
    print("=================================================")
    print("   SYMULACJA ARQ STOP-AND-WAIT (Python)")
    print("=================================================\n")

    # --- 1. KONFIGURACJA TESTU ---
    NAZWA_PLIKU_WEJ = "test_dlugi.txt"
    NAZWA_PLIKU_WYJ = "test_dlugi.txt"

    # Parametry symulacji
    MTU = 20  # Mały rozmiar ramki wymusza dużą ich liczbę (dobre do testów)
    P_BLAD_DANYCH = 0.0001  # 1 błąd na 10,000 bitów
    P_BLAD_ACK = 0.0001

    # --- 2. PRZYGOTOWANIE DANYCH ---
    # Tworzymy plik testowy, jeśli nie istnieje
    tresc_do_wyslania = b"A" * 5000
    # Możesz też dodać znaki specjalne, żeby przetestować escaping:
    tresc_do_wyslania += b"\x7E\x7D TEST_FLAG \x7E"

    with open(NAZWA_PLIKU_WEJ, "wb") as f:
        f.write(tresc_do_wyslania)

    print(f" [TEST] Przygotowano plik: {NAZWA_PLIKU_WEJ} ({len(tresc_do_wyslania)} bajtów)")

    # --- 3. INICJALIZACJA OBIEKTÓW ---

    # Wybór kanału (odkomentuj ten, którego chcesz użyć)

    # A) Kanał Binarny Symetryczny (szum losowy)
    kanal_tam = BSCKanal(p_error=P_BLAD_DANYCH)
    kanal_powrot = BSCKanal(p_error=P_BLAD_ACK)
    print(f" [TEST] Wybrano kanał BSC (p_data={P_BLAD_DANYCH}, p_ack={P_BLAD_ACK})")

    # B) Kanał Gilberta-Elliotta (błędy seryjne) - Opcjonalnie
    # kanal_tam = GilbertElliottKanal(p_G=0.01, p_B=0.8, p_GB=0.05, p_BG=0.2)
    # kanal_powrot = BSCKanal(p_error=0.0) # Zwrotny idealny dla uproszczenia

    # Nadajnik i Odbiornik
    # Adresy: Nadajnik=10, Odbiornik=20
    nadajnik = Nadajnik(moj_adres=10, adres_celu=20, mtu=MTU)
    odbiornik = Odbiornik(moj_adres=20, adres_nadajnika=10)

    # --- 4. URUCHOMIENIE TRANSMISJI ---
    print("\n [TEST] Rozpoczynam wysyłanie...")
    print("-" * 60)

    # Wywołujemy główną metodę nadajnika
    nadajnik.wyslij_plik(kanal_tam, kanal_powrot, tresc_do_wyslania, odbiornik)

    print("-" * 60)
    print(" [TEST] Transmisja zakończona.\n")

    # --- 5. WERYFIKACJA WYNIKÓW ---
    odebrane_dane = odbiornik.pobierz_dane()

    # Zapis do pliku wynikowego
    with open(NAZWA_PLIKU_WYJ, "wb") as f:
        f.write(odebrane_dane)

    print("=== RAPORT KOŃCOWY ===")
    print(f" 1. Rozmiar wysłany:  {len(tresc_do_wyslania)} bajtów")
    print(f" 2. Rozmiar odebrany: {len(odebrane_dane)} bajtów")

    # Statystyki z nadajnika
    total = nadajnik.total_transmissions
    retry = nadajnik.retransmissions
    if total > 0:
        loss_rate = (retry / total) * 100
    else:
        loss_rate = 0

    print(f" 3. Statystyki ARQ:")
    print(f"    - Całkowita liczba prób wysłania: {total}")
    print(f"    - Liczba retransmisji (błędów):   {retry}")
    print(f"    - Rzeczywista stopa błędów ramek: {loss_rate:.2f}%")

    # Porównanie zawartości
    if tresc_do_wyslania == odebrane_dane:
        print("\n ✅ WYNIK: POZYTYWNY (Pliki są identyczne)")
    else:
        print("\n ❌ WYNIK: NEGATYWNY (Pliki się różnią!)")
        # Pokaż różnicę (tylko dla małych plików)
        if len(tresc_do_wyslania) < 100:
            print(f"    Oczekiwano: {tresc_do_wyslania}")
            print(f"    Otrzymano:  {odebrane_dane}")


if __name__ == "__main__":
    run_test()