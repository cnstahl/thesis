import numpy as np
import quantum as qm
import asymmetric as asym
import scipy.sparse.linalg as spla
import glob

runs = 1
L = 15
end = 20
n = 5
tot = end*n
field_strength = .2

prefix = "data/zotocs_L"+str(L)+"end"+str(end)+"n"+str(n)+"_"+ \
          str(field_strength)+"#"

_,x_list,y_list, z_list = qm.get_sigma_lists(L, half=False)
H = asym.dense_H(L)
Z0 = z_list[0]
if (not field_strength is None):
    h = field_strength/2 # Take into account spin-1/2
    H = H + qm.get_local_field(z_list, np.random.rand(L)*2*h - h)

Hlist  = asym.mat2list(H)
Zlists = [asym.mat2list(Z) for Z in z_list]
Z0list = Zlists[0]

vec = qm.get_vec_Haar(2**L)
vecs = asym.arr2list(vec)

# Break into small and large blocks
cutoff = 500

s_Hlist  =  [H for H in Hlist  if H.shape[0]<cutoff]
s_Zlists = [[Z for Z in z_list if Z.shape[0]<cutoff] for z_list in Zlists]
s_Z0list =  [Z for Z in Z0list if Z.shape[0]<cutoff]

l_Hlist  =  [H for H in Hlist  if H.shape[0]>=cutoff]
l_Zlists = [[Z for Z in z_list if Z.shape[0]>=cutoff] for z_list in Zlists]
l_Z0list =  [Z for Z in Z0list if Z.shape[0]>=cutoff]
l_vecs  =   [v for v in vecs   if len(v)>=cutoff]

# Use different methods for small and large blocks
OTOCs = asym.zotoc_mat_exact(L, s_Hlist, s_Z0list, s_Zlists, end=20, n=3) + \
        asym.zotoc_vec_expm( L, l_Hlist, l_Z0list, l_vecs, l_Zlists)

# Save data
existing = glob.glob(prefix + "*.npy")
highest=-1
for fname in existing:
    current = int(fname.replace(prefix, "").replace(".npy", ""))
    if current>highest: highest=current
np.save(prefix+str(highest+1), OTOCs)
