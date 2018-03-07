import numpy as np
import scipy.linalg as  la
import scipy.special

I = np.array([[ 1,  0],[ 0,  1]])
X = np.array([[ 0,  1],[ 1,  0]])
Y = np.array([[ 0,-1j],[1j,  0]])
Z = np.array([[ 1,  0],[ 0, -1]])
H3mult = np.array([[0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0],
               [0 ,  0 ,  1 ,  0 , -1 ,  0 ,  0 , 0],
               [0 , -1 ,  0 ,  0 ,  1 ,  0 ,  0 , 0],
               [0 ,  0 ,  0 ,  0 ,  0 , -1 ,  1 , 0],
               [0 ,  1 , -1 ,  0 ,  0 ,  0 ,  0 , 0],
               [0 ,  0 ,  0 ,  1 ,  0 ,  0 , -1 , 0],
               [0 ,  0 ,  0 , -1 ,  0 ,  1 ,  0 , 0],
               [0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , 0]])

def sparse_Hmult(l):
    if (l==3): return H3mult
#     print(np.shape(np.kron(sparse_Hmult(l-2),I2)))
#     print(np.shape(np.kron(np.eye(l-3), H3mult)))
    return (np.kron(sparse_Hmult(l-2), np.eye(4)) + 
            np.kron(np.eye(2**(l-3)), H3mult))

def sparse_H(l):
    if (l%2 != 1): assert False, "l must be odd"
    H = sparse_Hmult(l)
    return H * (2j * np.pi)/(3 * np.sqrt(3))

def dense_Hmult(l):
    if (l==3): return H3mult
#     print(np.shape(np.kron(sparse_Hmult(l-2),I2)))
#     print(np.shape(np.kron(np.eye(l-3), H3mult)))
    return (np.kron(dense_Hmult(l-1), np.eye(2)) + 
            np.kron(np.eye(2**(l-3)), H3mult))

def dense_H(l):
    if (l < 3): assert False, "l must be >=3"
    H = dense_Hmult(l)
    return H * (2j * np.pi)/(3 * np.sqrt(3))

def chop(a):
    if not np.all(np.isclose(np.imag(a),0)): 
        print("\nchop() removed the imaginary part\n ")
    A = np.round(np.real(a),3)
    if np.all(np.isclose(A.astype(int), A)): return A.astype(int)
    else: return A

def norm(A):
    norm = np.trace(np.matmul(A, A.T.conj()))/(len(A))
#    print("here")
    assert np.isclose(np.imag(norm),0)
    return np.real(norm)

# Trace out the last/first i spins
def end_trace(x, i):
    N = len(x)
    untraced = (int) (N/2**i)
    traced = 2**i
    x = x.reshape((untraced, traced, untraced, traced))
    return np.trace(x, axis1=1, axis2=3)/2**i

def front_trace(x, i):
    N = len(x)
    untraced = (int) (N/2**i)
    traced = 2**i
    x = x.reshape((traced, untraced, traced, untraced))
    return np.trace(x, axis1=0, axis2=2)/2**i

def tensor(*args):
    A = 1
    for arg in args:
        A = np.kron(A, arg)
    return A

def par_tr(x,i):
    N = len(x)
    assert 2**i < N
    
    indices = np.array(range(N))
    bit = int((N/2)/2**i)
    mask = N - (bit) - 1
    indices = indices & mask
    return (x[:,np.unique(indices)][np.unique(indices)] + 
            x[:,np.unique(indices + bit)][np.unique(indices + bit)])/2
def permutations(L):
    alph2Sz = np.zeros(2**L, dtype=int)
    for i in range(2**L):
        alph2Sz[i] = bin(i).count('1')
    alph2Sz = alph2Sz.argsort()
    Sz2alph = np.zeros(2**L, dtype=int)
    for idx, val in enumerate(alph2Sz):
        Sz2alph[val] = idx
    return alph2Sz, Sz2alph

def mat2list(matrix):
    assert (len(np.shape(matrix)) == 2)
    L = (int) (np.log2(len(matrix)))
    alph2Sz, Sz2alph = permutations(L)
    diag = matrix[alph2Sz]
    diag = diag[:,alph2Sz]
    A = []
    j = 0
    for i in range(L+1):
        k = j + (int) (scipy.special.comb(L,i))
        A.append(diag[j:k, j:k])
        j = k
    return A

def list2mat(A):
    L = len(A) - 1
    alph2Sz, Sz2alph = permutations(L)
    diag = la.block_diag(*A)
    mat = diag[Sz2alph]
    return mat[:,Sz2alph]

def arr2list(array):
    assert (len(np.shape(array)) == 1)
    L = (int) (np.log2(len(array)))
    alph2Sz, Sz2alph = permutations(L)
    perm = array[alph2Sz]
    A = []
    j = 0
    for i in range(L+1):
        k = j + (int) (scipy.special.comb(L,i))
        A.append(perm[j:k])
        j = k
    return A

# def list2arr(A):
#     L = len(A) - 1
#     alph2Sz, Sz2alph = permutations(L)
#     diag = la.block_diag(*A)
#     mat = diag[Sz2alph]
#    return mat[:,Sz2alph]

# Get weights at only some sites at a given time
# Pass (vals, vecs) for faster performance
def get_weights(L, t, sites, here=True, H=None, vals=None, vecs=None):
    # make sure we have vals, vecs
    if (vals is None or vecs is None):
        assert not (H is None)
        vals, vecs = la.eigh(H)
    vecsd = vecs.T.conj()
    
    if (here == False): assert False, 'Only implemented for here'
    
    # Get preliminary stuff
    A = np.array([Z[0,0], Z[1,1]])
    for i in range(L-1):
        A = np.kron(A,np.array([1,1]))
    Alist = arr2list(A)
    B = np.array([Z[0,0], Z[1,1]])
    for i in range(L-1):
        B = np.kron(np.array([1,1]),B)
    Blist = arr2list(B)


    weightfore = np.empty(len(sites))
    weightback = np.empty(len(sites))
    
    unitt = np.matmul(vecs * np.exp(-1j*vals*t), vecsd)
    uninv = np.matmul(vecs * np.exp( 1j*vals*t), vecsd)
    
    ulist = mat2list(unitt)
    uinvlist = mat2list(uninv)
    
    Atlist = []
    for idx, val in enumerate(Alist):
        Atlist.append(np.matmul(uinvlist[idx] * val, ulist[idx]))
    Btlist = []
    for idx, val in enumerate(Blist):
        Btlist.append(np.matmul(uinvlist[idx] * val, ulist[idx]))
    At = list2mat(Atlist)
    Bt = list2mat(Btlist)
    
    front = 1
    back  = 1
    
    for j, site in enumerate(sites):
        Aj = par_tr(At,site)
        Bj = par_tr(Bt,site)
        fronthere = norm(Aj)
        backhere  = norm(Bj)
        weightfore[j] = 1 - fronthere
        weightback[j]     = 1 - backhere
    
    return np.array([weightfore, weightback])