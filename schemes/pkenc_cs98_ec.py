'''
Cramer-Shoup Public Key Encryption Scheme (Decisional Diffie-Hellman Assumption in groups of prime order)
 
| From: "R. Cramer, V. Shoup: A practical public key cryptosystem provably secure against adaptive chosen ciphertext attack"
| Published in: CRYPTO 1998
| Available from: http://knot.kaist.ac.kr/seminar/archive/46/46.pdf
| Notes: 

* type:			encryption (public key)
* setting:		DDH-hard EC groups of prime order (F_p)
* assumption:	DDH
* Name:         PKEnc_DDH_CCA_CS98

:Authors:	Matthew Green
:Date:			1/2011


'''
from toolbox.ecgroup import *
from toolbox.PKEnc import *
from toolbox.eccurve import prime192v1

# type definitions
pk_t = { 'g1' : G, 'g2' : G, 'c' : G, 'd' : G, 'h' : G }
sk_t = { 'x1' : ZR, 'x2' : ZR, 'y1' : ZR, 'y2' : ZR, 'z' : ZR }
c_t = { 'u1' : G, 'u2' : G, 'e' : G, 'v' : G }
str_t = str

debug = False
class EC_CS98(PKEnc):	
    def __init__(self, builtin_cv):
        PKEnc.__init__(self)
        global group
        group = ECGroup(builtin_cv)
        self.groupObj = group

    @output(pk_t, sk_t)
    def keygen(self, secparam=0):
        group.paramgen(secparam)
        g1, g2 = group.random(G), group.random(G)
        
        x1, x2, y1, y2, z = group.random(), group.random(), group.random(), group.random(), group.random()		
        c = ((g1 ** x1) * (g2 ** x2))
        d = ((g1 ** y1) * (g2 ** y2)) 
        h = (g1 ** z)
		
        pk = { 'g1' : g1, 'g2' : g2, 'c' : c, 'd' : d, 'h' : h }
        sk = { 'x1' : x1, 'x2' : x2, 'y1' : y1, 'y2' : y2, 'z' : z }
        return (pk, sk)

    @input(pk_t, bytes)
    @output(c_t)
    def encrypt(self, pk, M):
        r     = group.random()
        u1    = (pk['g1'] ** r)
        u2    = (pk['g2'] ** r)
        e     = group.encode(M) * (pk['h'] ** r)
        alpha = group.hash((u1, u2, e))
        v     = (pk['c'] ** r) * (pk['d'] ** (r * alpha))		
		# Assemble the ciphertext
                
        c = { 'u1' : u1, 'u2' : u2, 'e' : e, 'v' : v }
        return c
    
    @input(pk_t, sk_t, c_t)
    @output(bytes)
    def decrypt(self, pk, sk, c):
        alpha = group.hash((c['u1'], c['u2'], c['e']))
        v_prime = (c['u1'] ** (sk['x1'] + (sk['y1'] * alpha))) * (c['u2'] ** (sk['x2'] + (sk['y2'] * alpha)))
        if (c['v'] != v_prime):
            return 'ERROR' 

        if debug: print("c['v'] => %s" % c['v'])
        if debug: print("v' => %s" % v_prime)
        return group.decode(c['e'] / (c['u1'] ** sk['z']))

def main():
    pkenc = EC_CS98(prime192v1)
    
    (pk, sk) = pkenc.keygen()
    M = b"hello world!!!"

    ciphertext = pkenc.encrypt(pk, M)
    
    message = pkenc.decrypt(pk, sk, ciphertext)
    
    assert M == message, "Failed Decryption!!!"
    if debug: print("SUCCESSFUL DECRYPTION!!! => %s" % message)
   
if __name__ == "__main__":
    debug=True
    main()
   
