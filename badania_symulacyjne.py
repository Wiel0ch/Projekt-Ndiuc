import matplotlib.pyplot as plt
import numpy as np

from Nadajnik import Nadajnik
from Odbiornik import Odbiornik
from Kanal import BSCKanal

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


if __name__ == "__main__":
    badanie_ber()
    histogram()
    limit_retransmisji()
