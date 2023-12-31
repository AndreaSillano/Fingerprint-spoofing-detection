import numpy
from scipy.optimize import fmin_l_bfgs_b
from mlFunc import *
from itertools import repeat


def calculate_lbgf(H, DTR, C):
    def JDual(alpha):
        Ha = numpy.dot(H, vcol(alpha))
        aHa = numpy.dot(vrow(alpha), Ha)
        a1 = alpha.sum()
        return -0.5 * aHa.ravel() + a1, -Ha.ravel() + numpy.ones(alpha.size)

    def LDual(alpha):
        loss, grad = JDual(alpha)
        return -loss, -grad

    alphaStar, _x, _y = fmin_l_bfgs_b(
        LDual,
        numpy.zeros(DTR.shape[1]),
        bounds=C,
        factr=1.0,
        maxiter=10000,
        maxfun=100000,
    )

    return alphaStar, JDual, LDual

class SupportVectorMachine:
    def __init__(self):
        self.w = []
        self.pl = []
        self.dl = []
        self.dg = []

    def train_SVM_linear(self, DTR, LTR, C, K, balanced, pi):
        DTREXT = numpy.vstack([DTR, K * numpy.ones((1, DTR.shape[1]))])
        Z = numpy.zeros(LTR.shape)
        Z[LTR == 1] = 1
        Z[LTR == 0] = -1

        H = numpy.dot(DTREXT.T, DTREXT)
        H = vcol(Z) * vrow(Z) * H

        def JPrimal(w):
            S = numpy.dot(vrow(w), DTREXT)
            loss = numpy.maximum(numpy.zeros(S.shape), 1 - Z * S).sum()
            return 0.5 * numpy.linalg.norm(w) ** 2 + C * loss

        if(balanced):
            C1 = (C * pi) / (DTR[:, LTR == 1].shape[1] / DTR.shape[1])
            C0 = (C * (1 - pi)) / (DTR[:, LTR == 0].shape[1] / DTR.shape[1])
            bounds = [((0, C0) if x == 0 else (0, C1)) for x in LTR.tolist()]
        else:
            bounds = [(0, C)] * DTR.shape[1]

        alphaStar, JDual, LDual = calculate_lbgf(H, DTR, bounds)
        wStar = numpy.dot(DTREXT, vcol(alphaStar) * vcol(Z))
        return wStar, JPrimal(wStar)
    
    def train_SVM_polynomial(self, DTR, LTR, C, balanced, pi, K=1, constant=0, degree=2):
        Z = numpy.zeros(LTR.shape)
        Z[LTR == 1] = 1
        Z[LTR == 0] = -1

        H = (numpy.dot(DTR.T, DTR) + constant) ** degree + K ** 2

        H = vcol(Z) * vrow(Z) * H

        if(balanced):
            C1 = (C * pi) / (DTR[:, LTR == 1].shape[1] / DTR.shape[1])
            C0 = (C * (1 - pi)) / (DTR[:, LTR == 0].shape[1] / DTR.shape[1])
            bounds = [((0, C0) if x == 0 else (0, C1)) for x in LTR.tolist()]
        else:
            bounds = [(0, C)] * DTR.shape[1]

        alphaStar, JDual, LDual = calculate_lbgf(H, DTR, bounds)

        return alphaStar, JDual(alphaStar)[0]
    
    def train_SVM_RBF(self, DTR, LTR, C, balanced, pi, K=1, gamma=1.):
        Z = numpy.zeros(LTR.shape)
        Z[LTR == 1] = 1
        Z[LTR == 0] = -1

        # kernel function
        kernel = numpy.zeros((DTR.shape[1], DTR.shape[1]))
        for i in range(DTR.shape[1]):
            for j in range(DTR.shape[1]):
                kernel[i, j] = numpy.exp(-gamma * (numpy.linalg.norm(DTR[:, i] - DTR[:, j]) ** 2)) + K * K
        H = vcol(Z) * vrow(Z) * kernel

        if(balanced):
            C1 = (C * pi) / (DTR[:, LTR == 1].shape[1] / DTR.shape[1])
            C0 = (C * (1 - pi)) / (DTR[:, LTR == 0].shape[1] / DTR.shape[1])
            bounds = [((0, C0) if x == 0 else (0, C1)) for x in LTR.tolist()]
        else:
            bounds = [(0, C)] * DTR.shape[1]

        alphaStar, JDual, LDual = calculate_lbgf(H, DTR, bounds)

        return alphaStar, JDual(alphaStar)[0]

    def predict_SVM_Linear(self, D, L, C, K, Dte, balanced, pi):
        wStar, primal = self.train_SVM_linear(D, L, C, K, balanced, pi)
        DTEEXT = numpy.vstack([Dte, K * numpy.ones((1, Dte.shape[1]))])

        scores = numpy.dot(wStar.T, DTEEXT).ravel()
        return scores
    
    def predict_SVM_Pol(self, D, L, C, K, Dte, costant, degree, balanced, pi):

        aStar, primal = self.train_SVM_polynomial(D, L, C, balanced, pi, K, costant, degree)
        Z = numpy.zeros(L.shape)
        Z[L == 1] = 1
        Z[L == 0] = -1
        kernel = (numpy.dot(D.T, Dte) + costant) ** degree + K * K
        scores = numpy.sum(numpy.dot(aStar * vrow(Z), kernel), axis=0)
        return scores
    
    def predict_SVM_RBF(self, D, L, C, K, Dte, gamma, balanced, pi):
        Z = L * 2 - 1
        aStar, loss = self.train_SVM_RBF(D, L, C, balanced, pi, K, gamma)
        kern = numpy.zeros((D.shape[1], Dte.shape[1]))
        for i in range(D.shape[1]):
            for j in range(Dte.shape[1]):
                kern[i, j] = numpy.exp(-gamma * (numpy.linalg.norm(D[:, i] - Dte[:, j]) ** 2)) + K * K
        scores = numpy.sum(numpy.dot(aStar * vrow(Z), kern), axis=0)
        return scores

        