from Ramka import Ramka


class NadajnikGBN:
    def __init__(self, moj_adres, adres_celu, mtu=20, window_size=4, crc_type=Ramka.CRC16):
        self.addr_src = moj_adres
        self.addr_dst = adres_celu
        self.mtu = mtu
        self.window_size = window_size
        self.crc_type = crc_type
        self.total_transmissions = 0
        self.retransmissions = 0
        self.attempts_history = []

    def wyslij_plik(self, kanal_tam, kanal_powrot, dane: bytes, odbiornik_obj):
        chunks = [dane[i:i + self.mtu] for i in range(0, len(dane), self.mtu)]
        total_chunks = len(chunks)
        base = 0
        next_seq = 0
        print(f"[GBN] Rozmiar: {total_chunks} ramek. Okno: {self.window_size}. CRC: {self.crc_type}")
        while base < total_chunks:
            while next_seq < base + self.window_size and next_seq < total_chunks:
                chunk = chunks[next_seq]
                is_last = (next_seq == total_chunks - 1)
                seq_byte = next_seq & 0xFF
                ramka = Ramka(self.addr_src, self.addr_dst, seq_byte, chunk,
                              msg_type=Ramka.TYPE_DATA, is_eof=is_last,
                              crc_type=self.crc_type)

                pakiet = ramka.pakuj()
                self.total_transmissions += 1
                dane_w_kanale = kanal_tam.przeslij(pakiet)
                odpowiedz_bajty = odbiornik_obj.odbierz_i_odpisz(dane_w_kanale)

                if odpowiedz_bajty:
                    dane_ack_kanal = kanal_powrot.przeslij(odpowiedz_bajty)
                    ack_ramka = Ramka.rozpakuj(dane_ack_kanal)

                    if ack_ramka and ack_ramka.czy_poprawna() and ack_ramka.msg_type == Ramka.TYPE_ACK:
                        ack_seq = ack_ramka.seq
                        base_seq_byte = base & 0xFF
                        offset = (ack_seq - base_seq_byte) & 0xFF

                        if offset < self.window_size:
                            potential_base = base + offset + 1

                            if potential_base > base:
                                base = potential_base

                next_seq += 1

            if base < next_seq:
                lost_count = next_seq - base
                self.retransmissions += lost_count
                next_seq = base

        print(f"[GBN] Koniec. Total: {self.total_transmissions}, Retransmisje: {self.retransmissions}")