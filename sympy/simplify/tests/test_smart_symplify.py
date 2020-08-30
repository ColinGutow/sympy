from sympy.simplify.smart_simplify import presimpstst
from sympy.core.symbol import var
from sympy.solvers.solvers import solve
from sympy.functions.elementary.trigonometric import sin, cos
from sympy.functions.elementary.miscellaneous import sqrt
import copy


def quad():
    var('A B C D X')
    return A * X ** 2 + B * X + C


def quadsol():
    return solve(quad(), X)[0]


def eq1():
    return sin(quadsol()) + cos(quad())


def test_samehash():
    """
    artifically produces two different expressions with identical hashes in
    order to check that presimpstst doesn't wrongly substitue some expressions

    """
    tempquad = copy.deepcopy(quad())
    tempquadsol = copy.deepcopy(quadsol())
    tempquad._mhash = 1234
    tempquadsol._mhash = 1234
    assert (presimpstst((sin(tempquadsol) + cos(tempquad))) == (
    sin((-B + sqrt(-4 * A * C + B ** 2)) / (2 * A)) + cos(
        A * X ** 2 + B * X + C), []))
    pass


def differenthash():
    eq1()
    return presimpstst(eq1())


def test_sub():
    """
    simple example checking that presimpstst works as intended on non-edge
    cases

    """
    quad()
    quadsol()
    var('sub_0')
    assert (presimpstst(sin(quad()) + cos(quad())) == (
    sin(sub_0) + cos(sub_0), [True, False, False, False]))
    pass
