import matplotlib.pyplot as plt
import numpy as np
from Ramka import Ramka
from Nadajnik import Nadajnik
from Odbiornik import Odbiornik
from Kanal import BSCKanal
from NadajnikGBN import NadajnikGBN
from OdbiornikGBN import OdbiornikGBN

# PARAMETRY
MTU = 54
ROZMIAR_PLIKU = 5000
DANE = b"A" * ROZMIAR_PLIKU

LICZBA_POWTORZEN = 30        # ILE SYMULACJI NA JEDEN PUNKT
MAX_RETRIES = 50



# JEDNA SYMULACJA
def jedna_symulacja(p_error):
    kanal_tam = BSCKanal(p_error)
    kanal_powrot = BSCKanal(p_error)

    nadajnik = Nadajnik(1, 2, mtu=MTU)
    odbiornik = Odbiornik(2, 1)

    nadajnik.wyslij_plik(
        kanal_tam,
        kanal_powrot,
        DANE,
        odbiornik,
        max_retries=MAX_RETRIES
    )

    total = nadajnik.total_transmissions
    retry = nadajnik.retransmissions

    procent_retransmisji = retry / total * 100 if total > 0 else 0

    return procent_retransmisji, nadajnik.attempts_history


# BER ŚREDNIA RETRANSMISJI
def badanie_ber():
    p_errors = [1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2]

    srednie = []
    odchylenia = []

    for p in p_errors:
        wyniki = []

        for _ in range(LICZBA_POWTORZEN):
            wynik, _ = jedna_symulacja(p)
            wyniki.append(wynik)

        srednie.append(np.mean(wyniki))
        odchylenia.append(np.std(wyniki))

        print(f"BER={p:.5f} -> średnia={np.mean(wyniki):.2f}%")

    # WYKRES
    plt.figure(figsize=(9, 5))
    plt.errorbar(p_errors, srednie, yerr=odchylenia, marker='o')
    plt.xscale('log')
    plt.xlabel("BER")
    plt.ylabel("Procent retransmisji [%]")
    plt.title("Wpływ BER na retransmisje (średnia z 30 symulacji)")
    plt.grid(True)
    plt.savefig("ber_srednia.png")
    plt.show()



#HISTOGRAM LICZBY PRÓB
def histogram():
    BER_TEST = 0.002
    wszystkie_proby = []

    for _ in range(LICZBA_POWTORZEN):
        _, historia = jedna_symulacja(BER_TEST)
        wszystkie_proby.extend(historia)

    plt.figure(figsize=(8, 5))
    plt.hist(wszystkie_proby,
             bins=range(1, max(wszystkie_proby) + 2),
             align='left',
             rwidth=0.8)

    plt.xlabel("Liczba prób")
    plt.ylabel("Liczba ramek")
    plt.title("Histogram liczby prób (uśredniony)")
    plt.grid(True)
    plt.savefig("histogram.png")
    plt.show()
#WYZNACZENIE LIMITU RETRANSMISJI
def limit_retransmisji():
    BER_TEST = 0.002
    wszystkie = []

    for _ in range(LICZBA_POWTORZEN):
        _, historia = jedna_symulacja(BER_TEST)
        wszystkie.extend(historia)

    total = len(wszystkie)

    print("\n=== WYZNACZANIE LIMITU RETRANSMISJI ===")
    for n in range(1, max(wszystkie) + 1):
        success = sum(1 for x in wszystkie if x <= n)
        procent = success / total * 100

        print(f"Limit {n} -> {procent:.2f}%")

        if procent >= 99.5:
            print(f"\n REKOMENDOWANY LIMIT = {n}")
            break


def test_gbn_crc_comparison():
    LICZBA_PROB = 100  # Uśredniamy z 50 symulacji
    BER = 0.0001
    WINDOW = 5
    MTU = 54
    DANE = b"Test" * 5000  # ok 800 bajtów

    print(f"TRWA OBLICZANIE ŚREDNIEJ Z {LICZBA_PROB} SYMULACJI...")

    wyniki_crc8 = []
    wyniki_crc16 = []

    for _ in range(LICZBA_PROB):
        # --- CRC 8 ---
        n8 = NadajnikGBN(1, 2, mtu=MTU, window_size=WINDOW, crc_type=Ramka.CRC8)
        o8 = OdbiornikGBN(2, 1)
        k_tam = BSCKanal(BER)
        k_powrot = BSCKanal(BER)
        n8.wyslij_plik(k_tam, k_powrot, DANE, o8)
        wyniki_crc8.append(n8.retransmissions / n8.total_transmissions * 100)

        # --- CRC 16 ---
        n16 = NadajnikGBN(1, 2, mtu=MTU, window_size=WINDOW, crc_type=Ramka.CRC16)
        o16 = OdbiornikGBN(2, 1)
        k_tam2 = BSCKanal(BER)
        k_powrot2 = BSCKanal(BER)
        n16.wyslij_plik(k_tam2, k_powrot2, DANE, o16)
        wyniki_crc16.append(n16.retransmissions / n16.total_transmissions * 100)

    print("\n=== WYNIKI UŚREDNIONE ===")
    print(f"CRC-8  Średnia retransmisji: {np.mean(wyniki_crc8):.2f}% (Odchylenie: {np.std(wyniki_crc8):.2f})")
    print(f"CRC-16 Średnia retransmisji: {np.mean(wyniki_crc16):.2f}% (Odchylenie: {np.std(wyniki_crc16):.2f})")


def badanie_wplywu_okna():
    # KONFIGURACJA
    LICZBA_PROB = 50  # Ile razy powtarzamy test dla jednego okna
    BER = 0.0005  # Dobrany tak, by błędy były częste, ale nie zabijały transmisji
    DANE = b"Test" * 1000  # ok. 1.2 KB
    MTU = 50
    OKNA_DO_TESTU = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50]  # Punkty na osi X

    srednie_wyniki = []
    odchylenia = []

    print(f"\n=== BADANIE WPŁYWU OKNA (Uśrednione z {LICZBA_PROB} prób) ===")
    print(f"BER = {BER}, MTU = {MTU}")

    for w in OKNA_DO_TESTU:
        retransmisje_procenty = []

        for i in range(LICZBA_PROB):
            # Inicjalizacja obiektów dla nowej symulacji
            nadajnik = NadajnikGBN(1, 2, mtu=MTU, window_size=w, crc_type=Ramka.CRC16)
            odbiornik = OdbiornikGBN(2, 1)
            k_tam = BSCKanal(BER)
            k_powrot = BSCKanal(BER)  # Możesz dać 0.0 jeśli chcesz testować tylko forward channel

            nadajnik.wyslij_plik(k_tam, k_powrot, DANE, odbiornik)

            # Obliczanie procentu retransmisji
            if nadajnik.total_transmissions > 0:
                proc = (nadajnik.retransmissions / nadajnik.total_transmissions) * 100
            else:
                proc = 0
            retransmisje_procenty.append(proc)

        # Statystyka dla danego okna
        srednia = np.mean(retransmisje_procenty)
        std_dev = np.std(retransmisje_procenty)

        srednie_wyniki.append(srednia)
        odchylenia.append(std_dev)

        print(f"Okno {w:2d} -> Średnia retransmisji: {srednia:6.2f}% (std: {std_dev:.2f})")

    # RYSOWANIE WYKRESU
    plt.figure(figsize=(10, 6))

    # Wykres z "wąsami" (błąd standardowy)
    plt.errorbar(OKNA_DO_TESTU, srednie_wyniki, yerr=odchylenia,
                 fmt='-o', capsize=5, color='blue', ecolor='red', label='Go-Back-N')

    plt.title(f'Wpływ rozmiaru okna na retransmisje (GBN)\nBER={BER}, MTU={MTU}, Średnia z {LICZBA_PROB} prób')
    plt.xlabel('Rozmiar Okna (Window Size)')
    plt.ylabel('Procent Retransmisji [%]')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(OKNA_DO_TESTU)  # Wymuś pokazanie wszystkich testowanych okien na osi
    plt.legend()

    # Zapisz i pokaż
    plt.savefig("gbn_window_impact.png")
    plt.show()

def porownaj_crc_gbn():
        # --- KONFIGURACJA SYMULACJI ---
        LICZBA_PROB = 100  # Im więcej, tym dokładniejszy wynik (wygładza losowość)
        BER = 0.0001  # Prawdopodobieństwo błędu (1e-4)
        WINDOW = 5  # Rozmiar okna Go-Back-N
        MTU = 50  # Rozmiar ramki (bajty)
        DANE = b"Test" * 5000  # Ilość danych do wysłania (ok. 800 bajtów)

        print(f"\n=== PORÓWNANIE CRC-8 vs CRC-16 (Go-Back-N) ===")
        print(f"Parametry: BER={BER}, Window={WINDOW}, Prób={LICZBA_PROB}")
        print("Trwa symulacja... (to może chwilę potrwać)")

        wyniki_crc8 = []
        wyniki_crc16 = []

        # Pętla symulacyjna
        for i in range(LICZBA_PROB):
            if i % 10 == 0: print(f"Postęp: {i}/{LICZBA_PROB}...")  # Pasek postępu

            # --- SYMULACJA CRC-8 ---
            k_tam8 = BSCKanal(BER)
            k_powrot8 = BSCKanal(BER)
            n8 = NadajnikGBN(1, 2, mtu=MTU, window_size=WINDOW, crc_type=Ramka.CRC8)
            o8 = OdbiornikGBN(2, 1)

            n8.wyslij_plik(k_tam8, k_powrot8, DANE, o8)

            # Oblicz % retransmisji
            if n8.total_transmissions > 0:
                wynik8 = (n8.retransmissions / n8.total_transmissions) * 100
                wyniki_crc8.append(wynik8)

            # --- SYMULACJA CRC-16 ---
            k_tam16 = BSCKanal(BER)
            k_powrot16 = BSCKanal(BER)
            n16 = NadajnikGBN(1, 2, mtu=MTU, window_size=WINDOW, crc_type=Ramka.CRC16)
            o16 = OdbiornikGBN(2, 1)

            n16.wyslij_plik(k_tam16, k_powrot16, DANE, o16)

            # Oblicz % retransmisji
            if n16.total_transmissions > 0:
                wynik16 = (n16.retransmissions / n16.total_transmissions) * 100
                wyniki_crc16.append(wynik16)

        # --- OBLICZENIA STATYSTYCZNE ---
        avg_8 = np.mean(wyniki_crc8)
        std_8 = np.std(wyniki_crc8)

        avg_16 = np.mean(wyniki_crc16)
        std_16 = np.std(wyniki_crc16)

        print("\n=== WYNIKI KOŃCOWE ===")
        print(f"CRC-8:  Średnia retransmisji = {avg_8:.2f}%  (Odchylenie: +/- {std_8:.2f}%)")
        print(f"CRC-16: Średnia retransmisji = {avg_16:.2f}%  (Odchylenie: +/- {std_16:.2f}%)")

        diff = avg_16 - avg_8
        print(f"Różnica: {diff:.2f} p.p. (CRC-16 ma więcej retransmisji z powodu dłuższej ramki)")

        # --- GENEROWANIE WYKRESU ---
        labels = ['CRC-8', 'CRC-16']
        means = [avg_8, avg_16]
        stds = [std_8, std_16]

        plt.figure(figsize=(8, 6))
        # Słupki z 'yerr' tworzą wąsy błędów (odchylenie standardowe)
        bars = plt.bar(labels, means, yerr=stds, capsize=10, color=['#4CAF50', '#2196F3'], alpha=0.8)

        plt.ylabel('Średni procent retransmisji [%]')
        plt.title(
            f'Porównanie skuteczności CRC-8 vs CRC-16 w Go-Back-N\n(Średnia z {LICZBA_PROB} symulacji, BER={BER})')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Dodanie wartości liczbowych nad słupkami
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                     f'{height:.2f}%', ha='center', va='bottom', fontweight='bold')

        plt.savefig("porownanie_crc_gbn.png")
        plt.show()

if __name__ == "__main__":
    #badanie_ber()
    #histogram()
    #limit_retransmisji()
    #test_gbn_crc_comparison()
    #badanie_wplywu_okna()
    porownaj_crc_gbn()