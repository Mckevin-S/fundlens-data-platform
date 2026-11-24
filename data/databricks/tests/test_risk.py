import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from risk import historical_var, returns_from_navs


def test_rendements_depuis_les_vl():
    assert returns_from_navs([100, 110, 99]) == pytest.approx([0.10, -0.10])


def test_var_95_sur_100_rendements():
    returns = [-(i + 1) / 1000 for i in range(5)] + [0.001] * 95  # 5 pertes de 0,1 % à 0,5 %
    assert historical_var(returns, 0.95) == 0.001
    assert historical_var(returns, 0.99) == 0.005


def test_var_nulle_sans_perte():
    assert historical_var([0.01, 0.02], 0.95) == 0.0


@pytest.mark.parametrize("returns, confidence", [([], 0.95), ([0.1], 1.0), ([0.1], 0)])
def test_parametres_invalides(returns, confidence):
    with pytest.raises(ValueError):
        historical_var(returns, confidence)
