from Ramka import Ramka


class Odbiornik:

    def odbierz(self, ramka_bajty: bytes):

        ramka = Ramka.rozpakuj(ramka_bajty)

        print(f"[ODBIORNIK] Odebrano: {ramka}")

        if ramka.czy_poprawna():
            print("   CRC poprawne → dane OK")
            return ramka.dane
        else:
            print("   BŁĄD: CRC niepoprawne → dane uszkodzone!")
            return None
