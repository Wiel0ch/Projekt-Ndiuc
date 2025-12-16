from Nadajnik import Nadajnik
from Odbiornik import Odbiornik
from Kanal import BSCKanal


def run_test():
    print("=================================================")
    print("   SYMULACJA ARQ STOP-AND-WAIT")
    print("=================================================\n")

    # --- KONFIGURACJA ---
    NAZWA_PLIKU_WEJ = "test_data.txt"
    MTU = 20  # Małe ramki -> dużo wysłanych paczek

    # Realistyczne parametry (aby widzieć ~3-5% błędów)
    P_BLAD_DANYCH = 0.0001  # 1 błąd na 10,000 bitów
    P_BLAD_ACK = 0.0001

    # Generowanie dużej ilości danych (ok. 5KB) aby statystyka była rzetelna
    tresc_do_wyslania = b"A" * 3000 + b"END"

    with open(NAZWA_PLIKU_WEJ, "wb") as f:
        f.write(tresc_do_wyslania)

    # --- INICJALIZACJA ---
    kanal_tam = BSCKanal(p_error=P_BLAD_DANYCH)
    kanal_powrot = BSCKanal(p_error=P_BLAD_ACK)

    nadajnik = Nadajnik(moj_adres=10, adres_celu=20, mtu=MTU)
    odbiornik = Odbiornik(moj_adres=20, adres_nadajnika=10)

    # --- START ---
    nadajnik.wyslij_plik(kanal_tam, kanal_powrot, tresc_do_wyslania, odbiornik)

    # --- WYNIKI ---
    odebrane_dane = odbiornik.pobierz_dane()

    total = nadajnik.total_transmissions
    retry = nadajnik.retransmissions
    loss_rate = (retry / total * 100) if total > 0 else 0

    print("\n=== RAPORT ===")
    print(f"Dane wysłane: {len(tresc_do_wyslania)} B")
    print(f"Dane odebrane: {len(odebrane_dane)} B")
    print(f"Liczba prób:   {total}")
    print(f"Retransmisje:  {retry}")
    print(f"Stopa błędów:  {loss_rate:.2f}%")

    if tresc_do_wyslania == odebrane_dane:
        print("\nWYNIK: POZYTYWNY (Sukces!)")
    else:
        print("\n WYNIK: NEGATYWNY (Błąd danych)")


if __name__ == "__main__":
    run_test()