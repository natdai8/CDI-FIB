import sys
import os
import time
from collections import Counter
from operator import itemgetter
import pickle

#######################
### BURROWS-WHEELER ###
#######################

def compare_idx_rec(x, y, txt, n):
    if txt[x] != txt[y] or n == len(txt):
        return txt[x] < txt[y]
    
    return compare_idx_rec((x+1)%len(txt), (y+1)%len(txt), txt, n+1)

def compare_idx(x, y, txt):
    return compare_idx_rec(x, y, txt, 0)

def merge_sort(arr, txt):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]

    left = merge_sort(left, txt)
    right = merge_sort(right, txt)

    return merge(left, right, txt)


def merge(left, right, txt):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if compare_idx(left[i], right[j], txt):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    while i < len(left):
        result.append(left[i])
        i += 1

    while j < len(right):
        result.append(right[j])
        j += 1

    return result

def sorted_permutations(txt):
    perms = list(range(len(txt)))
    perms = merge_sort(perms, txt)
    return perms

def encode_burrows_wheeler(txt):
    sorted_perms = sorted_permutations(txt)
    last_col = ''.join(txt[x-1] for x in sorted_perms)
    pos = sorted_perms.index(0)

    return last_col, pos


#####################
### MOVE TO FRONT ###
#####################

def encode_move_to_front(txt):
    alphabet = list(set(txt))
    alphabet.sort()
    q = len(alphabet)
    sequence = []
    for char in txt:
        index = alphabet.index(char)
        sequence.append(index)
        alphabet.pop(index)
        alphabet.insert(0, char)
    return sequence


###########################
### RUN-LENGTH ENCODING ###
###########################

def rle_encoding(txt):
    c = 0
    lre_code = ''
    
    if (txt[0] == 0):
        c = 1
    else:
        lre_code += chr(txt[0])
    
    for i in range(1,len(txt)):
        if (txt[i] == 0):
            c += 1
        elif (c > 1):
            lre_code += (chr(1000) + chr(c) + chr(txt[i]))
            c = 0
        elif (c == 1):
            lre_code += (chr(0) + chr(txt[i]))
            c = 0
        else:
            lre_code += chr(txt[i])
            c = 0
            
    if (c > 1):
        lre_code += (chr(1000) + chr(c))
        c = 0
    elif (c == 1):
        lre_code += (chr(0))
    
    return ''.join(lre_code)

###############
### HUFFMAN ###
###############

def source_fromtext(txt, n=1):
    freq_packs = {}
    for i in range(len(txt) - n + 1):
        packs = txt[i:i+n]
        if packs in freq_packs:
            freq_packs[packs] += 1
        else:
            freq_packs[packs] = 1
    if (len(txt)%n != 0):
        ini = len(txt)-len(txt)%n
        freq_packs[txt[ini:len(txt)]] = 1
    
    freq_list = [(k, v) for k, v in freq_packs.items()]
    return sorted(freq_list, key=lambda x: x[0])

def kraft_inequality(lengths, q):
    s = 0
    for l in lengths:
        s += q**-l

    return s <= 1

def format_to_alf(number, base, length, alf):
    if number == 0:
        res = alf[0]
        if length == 1:
            return res
        else:
            count = 1
            digits = []
            digits.append(res)
            while (count < length):
                digits.insert(0, alf[0])
                count +=1
            res = ''.join(str(e) for e in digits[::-1])
            return res

    digits = []
    while number > 0:
        digits.append(alf[int(number % base)])
        number //= base
    count = len(digits)
    while (count < length):
                digits.append(alf[0])
                count +=1        
    res = ''.join(str(e) for e in digits[::-1])
    return res

def canonical_code(L,q=2, alf = [0,1]):
    if not kraft_inequality(L, q):
        return 'The entry does not satisfy Kraft-McMillan inequality.'
    
    bl_count = Counter(L)
    code = 0
    bl_count[0] = 0
    next_code = {}
    maximum = max(L) + 1       
    for l in range (0, maximum):
        code = (code + bl_count[l-1])*q
        next_code[l] = code 
    def_code = []
    lengths = {}
    for l in L:
        length = l
        def_code.append(next_code[length])
        lengths[next_code[length]] = length
        next_code[length] += 1
    def_code = list(map(lambda x: format_to_alf(x,q,lengths[x], alf),def_code))
    return def_code

def huffman_code(txt, src, package_size=1):
    d_nodes = {}
    for c in src:
        d_nodes[c[0]] = 0
    
    sorted_d = sorted(src, key=lambda x: x[1]) 

    while len(sorted_d) > 1:
        new_c = sorted_d[0][0] + sorted_d[1][0]
        new_f = sorted_d[0][1] + sorted_d[1][1]
        
        i = 0
        while i < len(sorted_d[0][0]):
            package = sorted_d[0][0][i:i+package_size]
            if (package not in d_nodes.keys()):
                package = sorted_d[0][0][i:i+len(sorted_d[0][0])%package_size]
                i += len(sorted_d[0][0])%package_size
            else:
                i += package_size
            d_nodes[package] += 1
        
        i = 0
        while i < len(sorted_d[1][0]):
            package = sorted_d[1][0][i:i+package_size]
            if (package not in d_nodes.keys()):
                package = sorted_d[1][0][i:i+len(sorted_d[1][0])%package_size]
                i += len(sorted_d[1][0])%package_size
            else:
                i += package_size
            d_nodes[package] += 1
        
        sorted_d[1] = (new_c,new_f)
        sorted_d.pop(0)
        sorted_d = sorted(sorted_d, key=lambda x: x[1])
    
    result = [(key,value) for key, value in zip(d_nodes.keys(), canonical_code(d_nodes.values(), 2, ['0','1']))]
    return result

##############
### ENCODE ###
##############

def encode(txta,corr):
    corr = dict(corr)
    txt_encoded = ''
    i, j = 0, 0
    while j<=len(txta):
        substring = txta[i:j]
        if substring in corr:
            txt_encoded += corr[substring]
            i = j
        j += 1
        
    if i != len(txta): # all the text could not be processed
        return 'Message could not be encoded'
    return txt_encoded


#########################
### SAVE FILE PROCESS ###
#########################

def write_coded_text_to_file(alp, src, index, coded_txt, filename):
    # Encode and write alp
    alp_string = ''.join(alp)
    alp_string = alp_string.encode('utf-8')

    # Encode and write src
    #src_string = ''.join([ str(x)+" "+str(y)+" " for (x,y) in src])
    #src_string = src_string.encode('utf-8')

    # Encode and write index
    index = index.to_bytes((index.bit_length() + 7) // 8, byteorder='big')

    # Encode and write bits to recover
    n_bits = len(coded_txt)
    recover_bits = n_bits.to_bytes((n_bits.bit_length() + 7) // 8, byteorder='big')

    # Encode and write coded text
    coded_txt = int(coded_txt, 2).to_bytes((len(coded_txt) + 7) // 8, byteorder='big')

    data = {'a': alp_string, 's': src, 'i': index, 'b': recover_bits, 'c': coded_txt}

    with open(filename+'.cdi', 'wb') as f:
        pickle.dump(data, f)
    f.close()

###########################
### COMPRESSION PROCESS ###
###########################

def compressor(filename, txt):

    # Alphabet of text
    alp = sorted(list(set(txt)))

    # Burrows-Wheeler Transform
    bw = encode_burrows_wheeler(txt)
    bw_code = bw[0]
    index = bw[1]

    # Move-to-Front
    mtf_code = encode_move_to_front(bw_code)

    # Run-Length Encoding
    rle_code = rle_encoding(mtf_code)

    # Huffman
    src = source_fromtext(rle_code,1)
    huf = huffman_code(rle_code, src, 1)
    corr = dict(huf)

    # Encoding
    huf_code = encode(rle_code,corr)

    # Write paramteres and coded text to file
    write_coded_text_to_file(alp, src, index, huf_code, filename)

############
### MAIN ###
############

def main():
    # Start execution time
    start_time = time.time()

    # Read input file
    filename = sys.argv[1]
    txt = open(filename+'.txt','r',encoding='utf-8').read()

    # Encode text and write it to file
    compressor(filename, txt)
    
    # Calculate encoding performance
    unicode_chars = len(txt)
    coded_bytes = os.path.getsize(filename+'.cdi')
    performance = (coded_bytes / unicode_chars) * 8
    print('Performance (bits/symbol):', performance)

    # Execution time
    end_time = time.time()
    print('Execution time (in seconds):', end_time - start_time)

if __name__ == "__main__":
    main()
