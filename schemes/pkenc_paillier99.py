'''
Pascal Paillier (Public-Key)
 
| From: "Public-Key Cryptosystems Based on Composite Degree Residuosity Classes" 
| Published in: EUROCRYPT 1999
| Available from: http://eprint.iacr.org/2009/309.pdf
| Notes: 

* type:           public-key encryption (public key)
* setting:        Integer

:Authors:    J Ayo Akinyele
:Date:            4/2011
'''
#from charm.integer import *
from toolbox.integergroup import RSAGroup,lcm,integer
from toolbox.PKEnc import PKEnc
from charm.engine.util import *

debug = False
"""A ciphertext class with homomorphic properties"""
class Ciphertext(dict):
    def __init__(self, ct, pk, key):
        dict.__init__(self, ct)
        self.pk, self.key = pk, key
    
    def __add__(self, other):
        if type(other) == int: # rhs must be Cipher
           lhs = dict.__getitem__(self, self.key)
           return Ciphertext({self.key:lhs * ((self.pk['g'] ** other) % self.pk['n2']) }, 
                             self.pk, self.key)        
        else: # neither are plain ints
           lhs = dict.__getitem__(self, self.key)
           rhs = dict.__getitem__(other, self.key)
        return Ciphertext({self.key:(lhs * rhs) % self.pk['n2']}, 
                          self.pk, self.key) 
        
    def __mul__(self, other):
        if type(other) == int:
            lhs = dict.__getitem__(self, self.key)
            return Ciphertext({self.key:(lhs ** other)}, self.pk, self.key)
    
    def randomize(self, r): # need to provide random value
        lhs = dict.__getitem__(self, self.key)
        rhs = (integer(r) ** self.pk['n']) % self.pk['n2']
        return Ciphertext({self.key:(lhs * rhs) % self.pk['n2']})
    
    def __str__(self):
        value = dict.__str__(self)
        return value # + ", pk =" + str(pk)
    
class Pai99(PKEnc):
    def __init__(self, groupObj):
        PKEnc.__init__(self)
        global group
        group = groupObj
    
    def L(self, u, n):
        return integer(int(u - 1)) / n
                
    def keygen(self, secparam=1024):
        (p, q, n) = group.paramgen(secparam)
        g = n + 1
        lam = lcm(p - 1, q - 1)
        n2 = n ** 2
        u = (self.L(((g % n2) ** lam), n) % n) ** -1
        pk, sk = {'n':n, 'g':g, 'n2':n2}, {'lamda':lam, 'u':u}
        return (pk, sk)

    def encrypt(self, pk, m):
        g, n, n2 = pk['g'], pk['n'], pk['n2']
        r = group.random(pk['n'])
        c = ((g % n2) ** m) * ((r % n2) ** n)
        return Ciphertext({'c':c}, pk, 'c')
    
    def decrypt(self, pk, sk, ct):
        n, n2 = pk['n'], pk['n2']
        return ((self.L(ct['c'] ** sk['lamda'], n) % n) * sk['u']) % n
    
    def encode(self, modulus, message):
        # takes a string and represents as a bytes object
        elem = integer(message)
        return elem % modulus
        
    def decode(self, pk, element):
        pass

def main():
    group = RSAGroup()
    pai = Pai99(group)
        
    (pk, sk) = pai.keygen()
    
    m1 = pai.encode(pk['n'], 12345678987654321)
    m2 = pai.encode(pk['n'], 12345761234123409)
    m3 = pai.encode(pk['n'], 24691440221777730) # target
    c1 = pai.encrypt(pk, m1)
    c2 = pai.encrypt(pk, m2)
        
    if debug: print("c1 =>", c1, "\n")
    if debug: print("c2 =>", c2, "\n")
    c3 = c1 + c2
    if debug: print("Homomorphic Add Test...\nc1 + c2 =>", c3, "\n")
            
    orig_m = pai.decrypt(pk, sk, c3)
    if debug: print("orig_m =>", orig_m)
    
    # m3 = m1 + m2
    assert m3 == orig_m, "FAILED Decryption!!!" 
    if debug: print("Successful Decryption!")
    
    if debug: print("Homomorphic Mul Test...\n")
    c4 = c1 + 200
    if debug: print("c4 = c1 + 200 =>", c4, "\n")        
    orig_m = pai.decrypt(pk, sk, c4)
    if debug: print("m4 =>", orig_m, "\n")
    
    c5 = c2 * 20201
    if debug: print("c5 = c2 * 2021 =>", c5, "\n")
    orig_m = pai.decrypt(pk, sk, c5)
    if debug: print("m5 =>", orig_m, "\n")
    
if __name__ == "__main__":
    debug = True
    main()
    
