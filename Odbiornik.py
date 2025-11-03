from Ramka import Ramka


class Odbiornik:
    """Odbiornik odbiera i rozpakowuje ramki, sprawdza CRC."""

    def odbierz(self, ramka_bajty: bytes):
        """
        Przyjmuje odebrane bajty, rozpakowuje ramkę i sprawdza poprawność CRC.
        """
        ramka = Ramka.rozpakuj(ramka_bajty)

        print(f"[ODBIORNIK] Odebrano: {ramka}")

        if ramka.czy_poprawna():
            print("   CRC poprawne → dane OK")
            return ramka.dane
        else:
            print("   BŁĄD: CRC niepoprawne → dane uszkodzone!")
            return None
