from Ramka import Ramka

class Odbiornik:
    def __init__(self, adres=2):
        self.adres = adres

    def odbierz(self, ramka_bajty: bytes):
        ramka = Ramka.rozpakuj(ramka_bajty)
        print(f"[ODBIORNIK] Odebrano: {ramka}")

        if ramka.addr_dst != self.adres:
            print("❌ Ramka nie dla mnie!")
            return None

        if ramka.czy_poprawna():
            print("✅ CRC poprawne → dane OK")
            return ramka.dane
        else:
            print("❌ BŁĄD CRC! Dane uszkodzone!")
            return None
