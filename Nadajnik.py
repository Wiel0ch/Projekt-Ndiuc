from Ramka import Ramka


class Nadajnik:

    def __init__(self):
        self.seq = 0   #numer sekwencyjny ramki (1 bajt)

    def wyslij(self, kanal, dane: bytes):
        ramka = Ramka(seq_num=self.seq, dane=dane)
        self.seq = (self.seq + 1) & 0xFF

        ramka_bajty = ramka.pakuj()
        print(f"[NADAJNIK] Wysyłam: {ramka}")
        return kanal.przeslij(ramka_bajty)
