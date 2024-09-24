import random
import socket

class Hamming_CRC:
    def __init__(self):
        pass
        
    @staticmethod
    def xor(x , y):
        answer = ''
        shortest_len = len(y)
        if(len(x) < len(y)):
            shortest_len = len(x)
        
        for i in range(0, shortest_len):
            if x[i] == y[i]:
                answer += '0'
            else:
                answer += '1'
        return answer

    @staticmethod
    def redundant_bit_calc(m):
        # 2^r >= m + r + 1
        for i in range(m):
            if(2**i >= (m + i + 1)):
                return i

    @staticmethod
    def get_rawData(data):
        raw_data = []
        j = 0
        for i in range(1, len(data) + 1):
            if i != 2 ** j:
                raw_data.append(data[-i])
            else:
                j += 1
        
        return ''.join(str(bit) for bit in reversed(raw_data))
        
    @staticmethod
    def hamming_codification(data):
        n = len(data)
        n_parity = Hamming_CRC.redundant_bit_calc(n)
        
        hamming_code = []
        j = 0
        k = 1
        
        for i in range (1, n + n_parity + 1):
            if i == 2 ** j:
                hamming_code.append(0)
                j += 1
            else:
                hamming_code.append(int(data[-k]))
                k += 1
        
        # calculate parity bits value
        for parity_bit in range(n_parity):
            parity_pos = (1 << parity_bit)
            parity_val = 0
            for i in range(1, len(hamming_code) + 1):
                if i & parity_pos == parity_pos:
                    parity_val ^= hamming_code[i - 1]
            hamming_code[parity_pos - 1] = parity_val
        
        return ''.join(str(bit) for bit in reversed(hamming_code))

    @staticmethod
    def hamming_decode(data):
        data = list(map(int, data))
        
        n = len(data)
        n_parity = Hamming_CRC.redundant_bit_calc(n)
        
        error_pos = 0
        for parity_bit in range(n_parity):
            parity_pos = 2 ** parity_bit
            parity_val = 0
            for i in range(1, n + 1):
                if i & parity_pos == parity_pos:
                    parity_val ^= data[-i]
            if parity_val == 1:
                error_pos += parity_pos
        
        error_corrected = (error_pos != 0)
        if error_corrected:
            data[-error_pos] ^= 1 
        
        #error_idx = n - error_idx
        raw_data = []
        j = 0
        for i in range(1, n + 1):
            if i != 2 ** j:
                raw_data.append(data[-i])
            else:
                j += 1
                
        raw_data = ''.join(str(bit) for bit in reversed(raw_data))
        decode_data = ''.join(chr(int(raw_data[i:i+8], 2)) for i in range(0, len(raw_data), 8))
        return decode_data, error_corrected, error_pos

    @staticmethod
    def isPower2(i):
        return i > 0 and i & (i-1) == 0

    @staticmethod
    def generate_err(data):
        bin = list(data)
        n = 4
        while Hamming_CRC.isPower2(int(n)) and n < len(data):
            n = abs(random.randint(0, len(bin) - 1))
        print(f'error generado en: [{len(bin) - n}]')
        bin[n] = str(int(bin[n]) ^ 1)

        return ''.join(bin)

    @staticmethod
    def string_to_bin(data):
        return ''.join(format(ord(char), '08b') for char in data)

    @staticmethod
    def bin_to_string(data):
        it = int(len(data)/8)
        res = ''
        gnrl_idx = 0
        for i in range(it):
            current_char = ''
            for j in range(0,8):
                current_char += data[gnrl_idx]
                gnrl_idx += 1
            res += chr(int(current_char, 2))
        return res

    @staticmethod
    def filling(original, final_length):
        zero_str = ''
        for i in range(0, final_length-len(original)):
            zero_str += '0'
        return zero_str+original

    @staticmethod
    def CRC_div(data, key):
        #print(f'CRC_div     data: {data}    key: {key}')
        next_bit = len(key)
        current = ''
        for i in range(0,next_bit):
            current += data[i]
        
        while next_bit <= len(data):
            if current[0] == '1':
                current = Hamming_CRC.xor(key,current)
            else:
                current = Hamming_CRC.xor(Hamming_CRC.filling('0',len(current)),current)

            current = current[1: len(current)]
            if next_bit < len(data):
                current += data[next_bit]
            next_bit += 1
            
            
        return current

    @staticmethod
    def CRC_code(data, key): 
        append_zeros = ''
        for i in range(0, len(key)-1):
            append_zeros += '0'
        full_message = data + append_zeros
        crc_code = Hamming_CRC.CRC_div(full_message, key)
        #full_message = xor('0'+full_message, '0'+crc_code)
        #full_message = xor(full_message, crc_code)
        return crc_code
        #return full_message[len(data)-len(key)+1: len(data)]

    @staticmethod
    def decode_CRC(CRC_data, key):
        original_data = CRC_data[0: len(CRC_data)-len(key)+1]
        crc_code_received = CRC_data[len(CRC_data)-len(key)+1: len(CRC_data)]
        comprobation_code = Hamming_CRC.CRC_code(original_data, key)
        
        if crc_code_received == comprobation_code:
            print("¡Correcto! Transmisión sin errores")
            return True
        else:
            print('Errores en la comunicación')
            return False

    @staticmethod
    def string_to_bin(data):
        return ''.join(format(ord(char), '08b') for char in data)

    @staticmethod
    def bin_to_string(data):
        it = int(len(data)/8)
        res = ''
        gnrl_idx = 0
        for i in range(it):
            current_char = ''
            for j in range(0,8):
                current_char += data[gnrl_idx]
                gnrl_idx += 1
            res += chr(int(current_char, 2))
        return res