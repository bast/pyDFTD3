#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pyDFTD3 -- Python implementation of Grimme's D3 dispersion correction.
# Copyright (C) 2020 Rob Paton and contributors.
#
# This file is part of pyDFTD3.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# For information on the complete list of contributors to the
# pyDFTD3, see: <http://github.com/bobbypaton/pyDFTD3/>
#

import json
from pathlib import Path

import pytest

from dftd3.ccParse import get_simple_data, getinData, getoutData
from dftd3.constants import AU_TO_ANG, AU_TO_KCAL
from dftd3.dftd3 import d3

HERE = Path(__file__).parents[1]


def _from_json(inp):
    with open(inp, "r") as j:
        data = json.load(j)

    atomtypes = data["molecule"]["symbols"]

    # reshape coordinates as (nat, 3) and convert to angstrom
    cartesians = [coordinate * AU_TO_ANG for coordinate in data["molecule"]["geometry"]]

    functional = data["model"]["method"]

    return atomtypes, cartesians, functional


def _from_txt(inp):
    data = get_simple_data(inp)
    return data.ATOMTYPES, data.CARTESIANS, data.FUNCTIONAL


def _from_com(inp):
    data = getinData(inp)
    return data.ATOMTYPES, data.CARTESIANS, data.FUNCTIONAL


def _from_log(inp):
    data = getoutData(inp)
    return data.ATOMTYPES, data.CARTESIANS, data.FUNCTIONAL


# reference numbers from canonical repo
@pytest.mark.parametrize(
    "damping,ref",
    [("zero", -0.005259458983232145), ("bj", -0.009129484886543590)],
    ids=[
        "zero",
        "bj",
    ],
)
@pytest.mark.parametrize(
    "atoms,coordinates,functional",
    [
        (_from_txt(HERE / "examples/formic_acid_dimer.txt")),
        (_from_com(HERE / "examples/formic_acid_dimer.com")),
        (_from_log(HERE / "examples/formic_acid_dimer.log")),
        (_from_json(HERE / "examples/formic_acid_dimer.json")),
    ],
    ids=["from_txt", "from_com", "from_log", "from_json"],
)
def test_CO2H2_2(atoms, coordinates, functional, damping, ref):
    r6, r8, _ = d3(
        atoms,
        coordinates,
        functional=functional,
        s6=0.0,
        rs6=0.0,
        s8=0.0,
        a1=0.0,
        a2=0.0,
        damp=damping,
        threebody=False,
        intermolecular=False,
        pairwise=False,
        verbose=0,
    )

    d3_au = (r6 + r8) / AU_TO_KCAL

    assert d3_au == pytest.approx(ref, rel=1.0e-5)
