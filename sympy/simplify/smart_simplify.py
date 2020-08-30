"""
Proof of principle using hashes to speed up simplification by substituting
symbols for equivalent expressions.

For some expressions this speeds up the process of simplification by
substituting in a variable for each part of the polynomial in order to reduce
the number of needed operations

"""
from sympy.core.expr import Expr
from sympy.core.symbol import Symbol
from sympy.core.numbers import *


def presimpstst(expr):
    """
    Create a new SymPy expression where equivalent sub-expressions have been
    substituted with a temporary symbol/variable to facilitate simplification.
    :param expr: SymPy expression
    :return: substituted SymPy expression, list of substitutions made.

    """

    def makehashtable(expr, hashtable=[]):
        """
        Find which parts of the expression have matching hashes and return a
        list of lists containing the matching objects sorted by hash.
        :param expr: SymPy expression to search
        :param hashtable: list of lists containing matching objects sorted by
        hash. Passed to allow recursion.
        :return: Nothing as updates go into the passed hashtable.

        """
        for obj in expr.args:
            if len(hashtable) == 0:
                hashtable.append([obj.__hash__(), obj])
            else:
                found = False
                for k in range(len(hashtable)):
                    if hashtable[k][0] == obj.__hash__():
                        (hashtable[k]).append(obj)
                        found = True
                if not (found):
                    hashtable.append([obj.__hash__(), obj])
            if isinstance(obj, Expr):
                makehashtable(obj, hashtable)
        pass

    def makesublst(expr):
        """
        Build the list of expressions to substitute a temporary symbol for.
        :param expr: The expression to be searched and substituted into.
        :return: list of expressions to substitute.

        """
        lst = []
        fnllst = []

        makehashtable(expr, lst)

        recurtest(lst, fnllst)

        return fnllst

    def recurtest(lst, fnllst=[]):
        """
        Recurses through the sublist and removes all expressions with matching
        hashes but mismatched values. fnllst will contain matching numbers
        which are ignored in the final substitution tests.
        :param lst: The list containing all matching hashes.
        :param fnllst: The recursive input to the  list used to track actual
        matches.
        :return: fnllst of its last recursion, which should contain all actual
        matches that can be substituted

        """

        for i in range(len(lst)):
            mtchlst = []
            newlst = []
            if len(lst[i]) > 2 and not (isinstance(lst[i][1], Integer)
                                        or isinstance(lst[i][1], float)
                                        or isinstance(lst[i][1], Symbol)
                                        or isinstance(lst[i][1], Number)):
                mtchlst.append(lst[i][0])
                if lst[i][1] != I:
                    for k in range(1, len(lst[i])):
                        if lst[i][1] == lst[i][k]:
                            mtchlst.append(lst[i][k])
                        else:
                            newlst.append(lst[i][k])

            if len(mtchlst) > 2:
                fnllst.append(mtchlst)

        if len(lst) >= 1:
            fnllst = recurtest(newlst, fnllst)
        else:
            return fnllst

    def crawlexprtree(expr, subhash, firstexpr, hashidx, didsubs=False):
        """
        Crawl the expression tree and substitute temporary variables for
        equivalent sub-expressions.
        :param expr: SymPy expression
        :param subhash: hash for the expression to be substituted
        :param firstexpr: object to compare to for substitution
        :param hashidx: index in the hash table for the hash
        :param didsubs: list to record which substitutions are done
        :return: newexpr a substituted SymPy expression, didsubs updated to
        reflect any substitutions.

        """
        exprtype = type(expr)
        tempargs = list(expr.args)
        for k in range(len(tempargs)):
            if tempargs[k].__hash__() == subhash and tempargs[k] == firstexpr \
                and not isinstance(tempargs[k], Number):
                tempsym = Symbol('sub_' + str(hashidx))
                tempargs[k] = tempsym
                didsubs = True
            if isinstance(tempargs[k], Expr):
                if tempargs[k] != I:
                    if not (isinstance(tempargs[k], Symbol)
                            or isinstance(tempargs[k], float)
                            or isinstance(tempargs[k], Integer)
                            or isinstance(tempargs[k], Number)):
                        tempargs[k], didsubs = crawlexprtree(tempargs[k],
                                                             subhash,
                                                             firstexpr,
                                                             hashidx,
                                                             didsubs)
        tempargs = tuple(tempargs)
        newexpr = exprtype(*tempargs)
        return newexpr, didsubs

    sublst = makesublst(expr)
    didsublst = [False] * len(sublst)
    exprtype = type(expr)
    temp = expr
    for k in range(len(sublst)):
        temp, didsublst[k] = crawlexprtree(temp, sublst[k][0], sublst[k][1], k)
    return temp, didsublst
