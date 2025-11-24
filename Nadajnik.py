from Ramka import Ramka

class Nadajnik:
    def __init__(self, addr_src=1, addr_dst=2):
        self.seq = 0
        self.addr_src = addr_src
        self.addr_dst = addr_dst

    def wyslij(self, kanal, dane: bytes):
        ramka = Ramka(self.addr_src, self.addr_dst, self.seq, dane)
        self.seq = (self.seq + 1) & 0xFF

        ramka_bajty = ramka.pakuj()
        print(f"[NADAJNIK] Wysyłam: {ramka}")
        return kanal.przeslij(ramka_bajty)
