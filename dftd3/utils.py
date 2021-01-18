# -*- coding: utf-8 -*-


from math import exp, sqrt

from qcelemental import periodictable

from .parameters import RCOV


def E_to_index(element):
    """Convert element symbol to 0-based index."""
    return periodictable.to_Z(element) - 1


def getMollist(bondmatrix, startatom):
    """From connectivity, establish if there is more than one molecule."""

    # The list of atoms in a molecule
    atomlist = []
    atomlist.append(startatom)
    count = 0

    while count < 100:
        for atom in atomlist:
            for i in range(0, len(bondmatrix[atom])):
                if bondmatrix[atom][i] == 1:
                    alreadyfound = 0
                    for at in atomlist:
                        if i == at:
                            alreadyfound = 1
                    if alreadyfound == 0:
                        atomlist.append(i)
        count = count + 1

    return atomlist


def ncoord(natom, atomtype, xco, yco, zco, k1=16, k2=4 / 3):
    """Calculation of atomic coordination numbers.

    Notes
    -----
    The constants ``k1`` and ``k2`` are used to determine fractional connectivities between 2 atoms:

      - ``k1`` is the exponent used in summation
      - ``k2`` is used a fraction of the summed single-bond radii

    These values are copied verbatim from Grimme's code.
    """

    cn = []
    for i in range(0, natom):
        xn = 0.0
        for iat in range(0, natom):
            if iat != i:
                dx = xco[iat] - xco[i]
                dy = yco[iat] - yco[i]
                dz = zco[iat] - zco[i]
                r = sqrt(dx * dx + dy * dy + dz * dz)

                Zi = E_to_index(atomtype[i])
                Ziat = E_to_index(atomtype[iat])

                rco = k2 * (RCOV[Zi] + RCOV[Ziat])
                rr = rco / r
                damp = 1.0 / (1.0 + exp(-k1 * (rr - 1.0)))
                xn = xn + damp
        cn.append(xn)

    return cn


def lin(i1, i2):
    """Linear interpolation."""

    idum1 = max(i1, i2)
    idum2 = min(i1, i2)
    lin = idum2 + idum1 * (idum1 - 1) / 2

    return lin


def getc6(c6ab, mxc, atomtype, cn, a, b, k3=-4.0):
    """Obtain the C6 coefficient for the interaction between atoms A and B.

    Notes
    -----
    The constant ``k3`` is copied verbatim from Grimme's code.
    """

    # atomic charges for atoms A and B, respectively
    iat = E_to_index(atomtype[a])
    jat = E_to_index(atomtype[b])

    c6mem = None
    rsum = 0.0
    csum = 0.0
    c6 = 0.0

    for i in range(0, mxc[iat]):
        for j in range(0, mxc[jat]):
            if isinstance(c6ab[iat][jat][i][j], (list, tuple)):
                c6 = c6ab[iat][jat][i][j][0]
                if c6 > 0:
                    c6mem = c6
                    cn1 = c6ab[iat][jat][i][j][1]
                    cn2 = c6ab[iat][jat][i][j][2]

                    r = (cn1 - cn[a]) ** 2 + (cn2 - cn[b]) ** 2
                    tmp1 = exp(k3 * r)
                    rsum = rsum + tmp1
                    csum = csum + tmp1 * c6

    if rsum > 0:
        c6 = csum / rsum
    else:
        c6 = c6mem

    if c6 is None:
        raise RuntimeError("Computation of C6 failed.")

    return c6
