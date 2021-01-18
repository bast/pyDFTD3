#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from dftd3.ccParse import get_simple_data, getinData, getoutData
from dftd3.constants import AU_TO_KCAL
from dftd3.dftd3 import calcD3

HERE = Path(__file__).parents[1]


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
    "data",
    [
        (get_simple_data(HERE / "examples/formic_acid_dimer.txt")),
        (getinData(HERE / "examples/formic_acid_dimer.com")),
        (getoutData(HERE / "examples/formic_acid_dimer.log")),
    ],
    ids=["from_txt", "from_com", "from_log"],
)
def test_CO2H2_2(data, damping, ref):
    d3out = calcD3(
        data=data,
        functional=data.FUNCTIONAL,
        s6=0.0,
        rs6=0.0,
        s8=0.0,
        a1=0.0,
        a2=0.0,
        damp=damping,
        abc=False,
        intermolecular=False,
        pairwise=False,
        verbose=False,
    )

    d3_au = (d3out.attractive_r6_vdw + d3out.attractive_r8_vdw) / AU_TO_KCAL

    assert d3_au == pytest.approx(ref, rel=1.0e-5)
