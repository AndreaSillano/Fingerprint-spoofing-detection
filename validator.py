import numpy

from dimensionality_reduction import DimensionalityReduction
from gaussian_classifier import MultivariateGaussianClassifier
from logistic_regression import LogisticRegression
from svm import SupportVectorMachine
from dimensionality_reduction import DimensionalityReduction
from GMM import GMM
from mlFunc import *
from plotter import Plotter
class Validation:
    def __init__(self):
        self.MVG = MultivariateGaussianClassifier()
        self.LR = LogisticRegression()
        self.svm = SupportVectorMachine()
        self.GMM = GMM()
        self.PLT = Plotter()
        self.dimRed = DimensionalityReduction()
    '''MVG VALIDATION'''
    def k_fold_MVG(self, k,DTR, LTR):
        llrMVG = []
        llrNV = []
        llrTCV =[]
        llrTNV =[]
        labelMVG = []

        Dtr = numpy.split(DTR.T, k, axis=1)
        Ltr = numpy.split(LTR, k)

        for i in range(k):
            Dte = Dtr[i]
            Lte = Ltr[i]
            D = []
            L = []

            for j in range(k):
                if j != i:
                    D.append(Dtr[j])
                    L.append(Ltr[j])

            D = numpy.hstack(D)
            L = numpy.hstack(L)
            #IF Z-NORM
            #D, Dte = znorm(D, Dte)
            # Train the model
            self._getScoresMVG(Dte, D, L, llrMVG, llrNV, llrTCV, llrTNV)
            labelMVG = numpy.append(labelMVG, Lte, axis=0)

        return llrMVG,llrNV,llrTCV,llrTNV,labelMVG

    def _getScoresMVG(self, Dte, D, L, llrMVG, llrNV,llrTCV, llrTNV):
        llrs = self.MVG.predict_MVG(D, L, Dte)
        llrsNV = self.MVG.predict_MVG_Naive_Bayes(D,L,Dte)
        llrsTCV  = self.MVG.predict_MVG_Tied_Cov(D,L,Dte)
        llrsTNV = self.MVG.predict_MVG_Tied_Cov_Naive(D,L,Dte)
        llrMVG.append(llrs)
        llrNV.append(llrsNV)
        llrTCV.append(llrsTCV)
        llrTNV.append(llrsTNV)


    def MVG_validation(self, DTR, LTR, pi, C_fn, C_fp):

        llrMVG, llrNV, llrTCV,llrTNV, labelMVG = self.k_fold_MVG(5,DTR,LTR)

        minDCF_MVG = compute_min_DCF(numpy.hstack(llrMVG),numpy.hstack(labelMVG), pi, C_fn, C_fp)
        actDCF_MVG = compute_act_DCF(numpy.hstack(llrMVG), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        print("############MVG###############")
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_MVG)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_MVG)

        print("############NAIVE BAYES#############")
        minDCF_NV = compute_min_DCF(numpy.hstack(llrNV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        actDCF_NV = compute_act_DCF(numpy.hstack(llrNV), numpy.hstack(labelMVG),pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_NV)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_NV)

        print("############TIED COV#############")
        minDCF_TCV = compute_min_DCF(numpy.hstack(llrTCV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        actDCF_TCV = compute_act_DCF(numpy.hstack(llrTCV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_TCV)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_TCV)

        print("############TIED COV BAYES#############")
        minDCF_TNV = compute_min_DCF(numpy.hstack(llrTNV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        actDCF_TNV = compute_act_DCF(numpy.hstack(llrTNV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_TNV)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_TNV)

    '''LOGISTIC REGRESSION VALIDATION'''
    def vecxxT(self, x):
        x = x[:, None]
        xxT = x.dot(x.T).reshape(x.size ** 2, order='F')
        return xxT
    
    def k_fold_LR(self,k,DTR,LTR, pi, l, norm=False):
        lr_score = []
        lr_score_quad =[]
        labelLR = []
        Dtr = numpy.split(DTR.T, k, axis=1)
        Ltr = numpy.split(LTR, k)

        for i in range(k):
            Dte = Dtr[i]
            Lte = Ltr[i]
            D = []
            L = []

            for j in range(k):
                if j != i:
                    D.append(Dtr[j])
                    L.append(Ltr[j])

            D = numpy.hstack(D)
            L = numpy.hstack(L)

            if norm:
                D, Dte = znorm(D, Dte)

            expanded_DTR = numpy.apply_along_axis(self.vecxxT, 0, D)
            expanded_DTE = numpy.apply_along_axis(self.vecxxT, 0, Dte)
            phi = numpy.vstack([expanded_DTR, D])

            phi_DTE = numpy.vstack([expanded_DTE, Dte])

            labelLR = numpy.append(labelLR, Lte, axis=0)
            lr_score.append(self.LR.predict_Logistic_Regression_weigthed(D, L, Dte, l, pi))
            lr_score_quad.append(self.LR.predict_quad_Logistic_Regression(phi, L, phi_DTE, l, pi))


        return lr_score, lr_score_quad,labelLR
    def k_fold_LR_Cal(self,k,DTR,LTR, pi, l, norm=False):
        lr_score = []
        lr_score_quad =[]
        labelLR = []
        Dtr = numpy.split(DTR.T, k, axis=1)
        Ltr = numpy.split(LTR, k)

        for i in range(k):
            Dte = Dtr[i]
            Lte = Ltr[i]
            D = []
            L = []

            for j in range(k):
                if j != i:
                    D.append(Dtr[j])
                    L.append(Ltr[j])

            D = numpy.hstack(D)
            L = numpy.hstack(L)

            if norm:
                D, Dte = znorm(D, Dte)

            expanded_DTR = numpy.apply_along_axis(self.vecxxT, 0, D)
            expanded_DTE = numpy.apply_along_axis(self.vecxxT, 0, Dte)
            phi = numpy.vstack([expanded_DTR, D])

            phi_DTE = numpy.vstack([expanded_DTE, Dte])

            labelLR = numpy.append(labelLR, Lte, axis=0)
            lr_score.append(self.LR.predict_Logistic_Regression_weigthed(D, L, Dte, l, pi))
            lr_score_quad.append(self.LR.predict_quad_Logistic_Regression(phi, L, phi_DTE, l, pi))
        return lr_score, lr_score_quad,labelLR

    def plot_DCF_lamda_prior(self, DTR, LTR, C_fn,C_fp):
        '''Plot minDCF on different lambda and prior'''
        lam = numpy.logspace(-5, 1, 30)
        #lam = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10]
        minDCF_LR_0_5 = []
        minDCF_LR_0_1 = []
        minDCF_LR_0_9 = []
        for l in lam:
            lr1, _,labelLr1 = self.k_fold_LR(5, DTR, LTR, 0.5, l,True)

            minDCF_LR_0_5 = numpy.hstack(
                (minDCF_LR_0_5, compute_min_DCF(numpy.hstack(lr1), numpy.hstack(labelLr1), 0.5, C_fn, C_fp)))

            lr2, _,labelLr2 = self.k_fold_LR(5, DTR, LTR, 0.1, l,True)

            minDCF_LR_0_1 = numpy.hstack(
                (minDCF_LR_0_1, compute_min_DCF(numpy.hstack(lr2), numpy.hstack(labelLr2), 0.1, C_fn, C_fp)))

            lr3, _,labelLr3 = self.k_fold_LR(5, DTR, LTR, 0.9, l,True)
            minDCF_LR_0_9 = numpy.hstack(
                (minDCF_LR_0_9, compute_min_DCF(numpy.hstack(lr3), numpy.hstack(labelLr3), 0.9, C_fn, C_fp)))

        self.PLT.plot_DCF_lambda(lam, numpy.hstack(minDCF_LR_0_5), numpy.hstack(minDCF_LR_0_1),
                                 numpy.hstack(minDCF_LR_0_9), 'lambda')
    def plot_DCF_PCA(self,DTR, LTR, pi, C_fn, C_fp):
        '''Plot PCA LOG'''
        #lam = numpy.logspace(-5, 1, 30)
        lam =[1e-5,1e-4, 1e-3, 1e-2, 1e-1, 1, 10]
        minDCF_9 = []
        minDCF_8 = []
        minDCF_7 = []
        minDCF_LR = []
        DP_9 = self.dimRed.PCA(DTR, 9)
        DP_8 = self.dimRed.PCA(DTR, 8)
        DP_7 = self.dimRed.PCA(DTR, 7)
        for l in lam:
            lr1,_, labelLr1 = self.k_fold_LR(5, DTR, LTR, pi, l)

            minDCF_LR = numpy.hstack(
                (minDCF_LR, compute_min_DCF(numpy.hstack(lr1), numpy.hstack(labelLr1), pi, C_fn, C_fp)))

            lr9,_, labelLr9 = self.k_fold_LR(5, DP_9.T, LTR, pi, l)

            minDCF_9 = numpy.hstack(
                (minDCF_9, compute_min_DCF(numpy.hstack(lr9), numpy.hstack(labelLr9), pi, C_fn, C_fp)))

            lr8,_, labelLr8 = self.k_fold_LR(5, DP_8.T, LTR, pi, l)

            minDCF_8 = numpy.hstack(
                (minDCF_8, compute_min_DCF(numpy.hstack(lr8), numpy.hstack(labelLr8), pi, C_fn, C_fp)))

            lr7, _,labelLr7 = self.k_fold_LR(5, DP_7.T, LTR, pi, l)

            minDCF_7 = numpy.hstack(
                (minDCF_7, compute_min_DCF(numpy.hstack(lr7), numpy.hstack(labelLr7), pi, C_fn, C_fp)))

        self.PLT.plot_DCF_compare_PCA(lam, numpy.hstack(minDCF_LR), numpy.hstack(minDCF_9), numpy.hstack(minDCF_8),
                                      numpy.hstack(minDCF_7))

    def plot_minDCF_Z(self, DTR, LTR, pi, C_fn, C_fp):
        '''Plot min DCF vs minDCF with z-norm'''
        lam = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10]
        minDCF_LR = []
        minDCF_LR_Z = []

        for l in lam:
            lr1,_, labelLr1 = self.k_fold_LR(5, DTR, LTR, pi, l)

            minDCF_LR = numpy.hstack(
                (minDCF_LR, compute_min_DCF(numpy.hstack(lr1), numpy.hstack(labelLr1), pi, C_fn, C_fp)))

            lr2, _,labelLr2 = self.k_fold_LR(5, DTR, LTR, pi, l, True)

            minDCF_LR_Z = numpy.hstack(
                (minDCF_LR_Z, compute_min_DCF(numpy.hstack(lr2), numpy.hstack(labelLr2), pi, C_fn, C_fp)))

        self.PLT.plot_DCF_compare(lam, numpy.hstack(minDCF_LR), numpy.hstack(minDCF_LR_Z))

    def plot_DCF_PCA_Q(self,DTR, LTR, pi, C_fn, C_fp):
        '''Plot PCA Q-LOG'''
        #lam = numpy.logspace(-5, 1, 30)
        lam = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10]
        minDCF_9 = []
        minDCF_8 = []
        minDCF_7 = []
        minDCF_6 = []
        minDCF_LR = []
        DP_9 = self.dimRed.PCA(DTR, 9)
        DP_8 = self.dimRed.PCA(DTR, 8)
        DP_7 = self.dimRed.PCA(DTR, 7)
        DP_6 = self.dimRed.PCA(DTR, 6)
        for l in lam:
            _, lr1,labelLr1 = self.k_fold_LR(5, DTR, LTR, pi, l)

            minDCF_LR = numpy.hstack(
                (minDCF_LR, compute_min_DCF(numpy.hstack(lr1), numpy.hstack(labelLr1), pi, C_fn, C_fp)))

            _,lr9, labelLr9 = self.k_fold_LR(5, DP_9.T, LTR, pi, l)

            minDCF_9 = numpy.hstack(
                (minDCF_9, compute_min_DCF(numpy.hstack(lr9), numpy.hstack(labelLr9), pi, C_fn, C_fp)))

            _,lr8, labelLr8 = self.k_fold_LR(5, DP_8.T, LTR, pi, l)

            minDCF_8 = numpy.hstack(
                (minDCF_8, compute_min_DCF(numpy.hstack(lr8), numpy.hstack(labelLr8), pi, C_fn, C_fp)))

            _, lr7,labelLr7 = self.k_fold_LR(5, DP_7.T, LTR, pi, l)

            minDCF_7 = numpy.hstack(
                (minDCF_7, compute_min_DCF(numpy.hstack(lr7), numpy.hstack(labelLr7), pi, C_fn, C_fp)))

            _, lr6, labelLr6 = self.k_fold_LR(5, DP_6.T, LTR, pi, l)

            minDCF_6 = numpy.hstack(
                (minDCF_6, compute_min_DCF(numpy.hstack(lr6), numpy.hstack(labelLr6), pi, C_fn, C_fp)))

        self.PLT.plot_DCF_compare_PCA_Q(lam, numpy.hstack(minDCF_LR), numpy.hstack(minDCF_9), numpy.hstack(minDCF_8),
                                      numpy.hstack(minDCF_7),numpy.hstack(minDCF_6))
    def plot_minDCF_Z_Q(self, DTR, LTR, pi, C_fn, C_fp):
        '''Plot min DCF vs minDCF with z-norm QUAD'''
        lam = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10]
        minDCF_LR = []
        minDCF_LR_Z = []

        for l in lam:
            _, lr1, labelLr1 = self.k_fold_LR(5, DTR, LTR, pi, l)

            minDCF_LR = numpy.hstack(
                (minDCF_LR, compute_min_DCF(numpy.hstack(lr1), numpy.hstack(labelLr1), pi, C_fn, C_fp)))

            _, lr2, labelLr2 = self.k_fold_LR(5, DTR, LTR, pi, l, True)

            minDCF_LR_Z = numpy.hstack(
                (minDCF_LR_Z, compute_min_DCF(numpy.hstack(lr2), numpy.hstack(labelLr2), pi, C_fn, C_fp)))

        self.PLT.plot_DCF_compare_QUAD(lam, numpy.hstack(minDCF_LR), numpy.hstack(minDCF_LR_Z))
    def plot_minDCF_Z_PCA(self,DTR, LTR, pi, C_fn, C_fp):
        '''Plot PCA Q-LOG'''
        lam = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10]
        minDCF_7 = []
        minDCF_7_Z = []
        DP_7 = self.dimRed.PCA(DTR, 7)
        for l in lam:
            _, lr7, labelLr7 = self.k_fold_LR(5, DP_7.T, LTR, pi, l)

            minDCF_7 = numpy.hstack(
                (minDCF_7, compute_min_DCF(numpy.hstack(lr7), numpy.hstack(labelLr7), pi, C_fn, C_fp)))

            _, lr7_z, labelLr7_z = self.k_fold_LR(5, DP_7.T, LTR, pi, l, True)

            minDCF_7_Z = numpy.hstack(
                (minDCF_7_Z, compute_min_DCF(numpy.hstack(lr7_z), numpy.hstack(labelLr7_z), pi, C_fn, C_fp)))

        self.PLT.plot_DCF_compare_PCA_Z(lam, numpy.hstack(minDCF_7), numpy.hstack(minDCF_7_Z))
    

    def LR_validation(self,DTR, LTR, pi, C_fn, C_fp, plot):
        lr,lrQ, labelLr = self.k_fold_LR(5,DTR,LTR,pi, 0.01, False)
        print("############LOGISTIC REGRESSION#############")
        minDCF_LR = compute_min_DCF(numpy.hstack(lr), numpy.hstack(labelLr), pi, C_fn, C_fp)
        actDCF_LR = compute_act_DCF(numpy.hstack(lr), numpy.hstack(labelLr),pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_LR)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_LR)

        print("############LOGISTIC REGRESSION QUADRATIC#############")
        minDCF_LRQ = compute_min_DCF(numpy.hstack(lrQ), numpy.hstack(labelLr), pi, C_fn, C_fp)
        actDCF_LRQ = compute_act_DCF(numpy.hstack(lrQ), numpy.hstack(labelLr), pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_LRQ)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_LRQ)
        bayes_error_min_act_plot(numpy.hstack(lrQ),numpy.hstack(labelLr), 1)


        if plot:
            print("Start Plotting it can take a while")
            self.plot_DCF_lamda_prior(DTR, LTR, C_fn,C_fp)
            self.plot_DCF_PCA(DTR, LTR, pi, C_fn, C_fp)
            self.plot_minDCF_Z(DTR, LTR, pi, C_fn, C_fp)
            self.plot_minDCF_Z_Q(DTR, LTR, pi, C_fn, C_fp)
            self.plot_DCF_PCA_Q(DTR,LTR,pi,C_fn,C_fp)
            self.plot_minDCF_Z_PCA(DTR, LTR, pi, C_fn, C_fp)

        print("score calibartion")
        _w,_b = self.LR.compute_scores_param(numpy.hstack(lrQ), labelLr, 0.01, 0.7)
        cal_score = _w*lrQ + _b -numpy.log(pi/(1-pi))
        if plot:
            bayes_error_min_act_plot(numpy.hstack(cal_score), numpy.hstack(labelLr), 1)

    '''SVM VALIDATION'''
    def get_scores_SVM(self, D, L, Dte, Lte, C, K, costant, degree, gamma, scoresLin_append, scoresPol_append, scoresRBF_append, balanced, pi, method):    

        if method == 'linear' or method == 'all':
            scoresLin_append.append(self.svm.predict_SVM_Linear(D, L, C, K, Dte, balanced, pi))
        if method == 'pol' or method == 'all':
            scoresPol_append.append(self.svm.predict_SVM_Pol(D, L, C, K, Dte, costant, degree, balanced, pi))
        if method == 'rbf' or method == 'all':
            scoresRBF_append.append(self.svm.predict_SVM_RBF(D, L, C, K, Dte, gamma, balanced, pi))

    def kfold_SVM(self, DTR, LTR, K, C, balanced, pi, method, norm=False):
        k = 5
        Dtr = numpy.split(DTR, k, axis=1)
        Ltr = numpy.split(LTR, k)

        scoresLin_append = []
        scoresPol_append = []
        scoresRBF_append = []
        SVM_labels = []

        for i in range(k):
            Dte = Dtr[i]
            Lte = Ltr[i]
            D = []
            L = []

            for j in range(k):
                if j != i:
                    D.append(Dtr[j])
                    L.append(Ltr[j])

            D = numpy.hstack(D)
            L = numpy.hstack(L)   

            if norm:
                D, Dte = znorm(D, Dte)

            costant = 0
            degree = 2
            gamma=0.001
            SVM_labels = numpy.append(SVM_labels, Lte, axis=0)
            SVM_labels = numpy.hstack(SVM_labels)

            self.get_scores_SVM(D, L, Dte, Lte, C, K, costant, degree, gamma, scoresLin_append, scoresPol_append, scoresRBF_append, balanced, pi, method)
        
        return scoresLin_append, scoresPol_append, scoresRBF_append, SVM_labels

    def SVM_score_calibration(self, DTR, LTR, K_arr, C_arr, pi, Cfn, Cfp):
        actDFCLin = []
        actDFCPol = []
        actDFCRBF = []

        print("SVM Calibration for 3 models:\n")
        for K in K_arr:
            for C in C_arr:
                scoresLin_append, scoresPol_append, scoresRBF_append, SVM_labels = self.kfold_SVM(DTR, LTR, K, C)

                scoresLin_append = numpy.hstack(scoresLin_append)
                scores_tot = compute_act_DCF(scoresLin_append, SVM_labels, pi, Cfn, Cfp)
                actDFCLin.append(scores_tot)

                scoresPol_append = numpy.hstack(scoresPol_append)
                scores_tot = compute_act_DCF(scoresPol_append, SVM_labels, pi, Cfn, Cfp)
                actDFCPol.append(scores_tot)

                scoresRBF_append = numpy.hstack(scoresRBF_append)
                scores_tot = compute_act_DCF(scoresRBF_append, SVM_labels, pi, Cfn, Cfp)
                actDFCRBF.append(scores_tot)

        print("DFC Calibrated Linear: ", min(actDFCLin), "\nDFC Calibrated Polynomial: ", min(actDFCPol), "\nDFC Calibrated RBF: ", min(actDFCRBF))


    def SVM_validation(self, DTR, LTR, pi, C_fn, C_fp, K, C, balanced):
        scoresLin_append = []
        scoresPol_append = []
        scoresRBF_append = []
        SVM_labels = []
        DTR = DTR.T
        print("start")
        scoresLin_append, scoresPol_append, scoresRBF_append, SVM_labels = self.kfold_SVM(DTR, LTR, K, C, balanced, pi, "rbf", False)

        print("##########LINEAR##########\nbalanced= ",balanced,"\n")
        scores_tot = compute_min_DCF(numpy.hstack(scoresLin_append), SVM_labels, pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % scores_tot)

        rettt = compute_act_DCF(numpy.hstack(scoresLin_append), SVM_labels, pi, C_fn, C_fp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)

        print("##########POLYNOMIAL##########")
        scores_tot = compute_min_DCF(numpy.hstack(scoresPol_append), SVM_labels, pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % scores_tot)

        rettt = compute_act_DCF(numpy.hstack(scoresPol_append), SVM_labels, pi, C_fn, C_fp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)


        print("##########RBF##########")
        scores_tot = compute_min_DCF(numpy.hstack(scoresRBF_append), SVM_labels, pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % scores_tot)
        #bayes_error_min_act_plot(numpy.hstack(scoresRBF_append), numpy.hstack(SVM_labels), 1)

        rettt = compute_act_DCF(numpy.hstack(scoresRBF_append), SVM_labels, pi, C_fn, C_fp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)

        print("SMV RBF Calibration")
        _w, _b = self.LR.compute_scores_param(numpy.hstack(scoresRBF_append), SVM_labels, 0.01, 0.7)
        cal_score = _w*scoresRBF_append + _b - numpy.log(pi/(1-pi))
        bayes_error_min_act_plot(numpy.hstack(cal_score), numpy.hstack(SVM_labels), 1)

        K_arr = [0.1, 1.0, 10.0]
        C_arr = [0.01, 0.1, 1.0, 10.0]
        C_arr = [0.1, 1.0, 10.0]
        self.SVM_score_calibration(DTR, LTR, K_arr, C_arr, pi, C_fn, C_fp)

        self.plot_DCF_SVM(DTR, LTR, C_fn, C_fp, K, C, balanced)

    def plot_DCF_SVM(self, DTR, LTR, C_fn, C_fp, K, C, balanced):
        C_arr = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 100]
        minDCF_LR_0_5 = []
        minDCF_LR_0_1 =[]
        minDCF_LR_0_9 =[]
        minDCF_pol_0_5 = []
        minDCF_pol_0_1 =[]
        minDCF_pol_0_9 =[]
        minDCF_rbf_0_5 = []
        minDCF_rbf_0_1 =[]
        minDCF_rbf_0_9 =[]
        for c in C_arr:
            K=1
            lr1, _, _, labelLr1 = self.kfold_SVM(DTR, LTR, K, c, balanced, 0.5, 'linear')
            K=10
            _, pol1, _, labelLr1 = self.kfold_SVM(DTR, LTR, K, c, balanced, 0.5, 'pol')
            K=0.1
            _, _, rbf1, labelLr1 = self.kfold_SVM(DTR, LTR, K, c, balanced, 0.5, 'rbf')

            minDCF_LR_0_5 = numpy.hstack((minDCF_LR_0_5,compute_min_DCF(numpy.hstack(lr1), numpy.hstack(labelLr1), 0.5, C_fn, C_fp)))
            minDCF_pol_0_5 = numpy.hstack((minDCF_pol_0_5,compute_min_DCF(numpy.hstack(pol1), numpy.hstack(labelLr1), 0.5, C_fn, C_fp)))
            minDCF_rbf_0_5 = numpy.hstack((minDCF_rbf_0_5,compute_min_DCF(numpy.hstack(rbf1), numpy.hstack(labelLr1), 0.5, C_fn, C_fp)))

            lr2, pol2, rbf2, labelLr2 = self.kfold_SVM(DTR, LTR, K, c, balanced, 0.1)

            minDCF_LR_0_1 = numpy.hstack((minDCF_LR_0_1,compute_min_DCF(numpy.hstack(lr2), numpy.hstack(labelLr2), 0.1, C_fn, C_fp)))
            minDCF_pol_0_1 = numpy.hstack((minDCF_pol_0_1,compute_min_DCF(numpy.hstack(pol2), numpy.hstack(labelLr1), 0.1, C_fn, C_fp)))
            minDCF_rbf_0_1 = numpy.hstack((minDCF_rbf_0_1,compute_min_DCF(numpy.hstack(rbf2), numpy.hstack(labelLr1), 0.1, C_fn, C_fp)))

            lr2, pol2, rbf2, labelLr2 = self.kfold_SVM(DTR, LTR, K, c, balanced, 0.9)
            minDCF_LR_0_9 = numpy.hstack((minDCF_LR_0_9,compute_min_DCF(numpy.hstack(lr2), numpy.hstack(labelLr2), 0.9, C_fn, C_fp)))
            minDCF_pol_0_9 = numpy.hstack((minDCF_pol_0_9,compute_min_DCF(numpy.hstack(pol2), numpy.hstack(labelLr1), 0.9, C_fn, C_fp)))
            minDCF_rbf_0_9 = numpy.hstack((minDCF_rbf_0_9,compute_min_DCF(numpy.hstack(rbf2), numpy.hstack(labelLr1), 0.9, C_fn, C_fp)))

        self.PLT.plot_DCF_SVM_C(C_arr, numpy.hstack(minDCF_LR_0_5), numpy.hstack(minDCF_pol_0_5), numpy.hstack(minDCF_rbf_0_5), 'C', 'comp')
        self.PLT.plot_DCF_lambda(C_arr, numpy.hstack(minDCF_pol_0_5), numpy.hstack(minDCF_pol_0_1),numpy.hstack(minDCF_pol_0_9), 'C', 'Pol')
        self.PLT.plot_DCF_lambda(C_arr, numpy.hstack(minDCF_rbf_0_5), numpy.hstack(minDCF_rbf_0_1),numpy.hstack(minDCF_rbf_0_9), 'C', 'RBF')

        DP_9 = self.dimRed.PCA(DTR.T, 9)
        DP_8 = self.dimRed.PCA(DTR.T, 8)
        minDCF_9 = []
        minDCF_8 = []
        minDCF_z = []
        minDCF_LR = []
        for c in C_arr:
            lr1, _, _, labelLr1 = self.kfold_SVM(DTR, LTR, K, c, balanced, 0.5)

            minDCF_LR = numpy.hstack(
                    (minDCF_LR, compute_min_DCF(numpy.hstack(lr1), numpy.hstack(labelLr1), 0.5, C_fn, C_fp)))

            lr9, _, _, labelLr9 = self.kfold_SVM(DP_9, LTR, K, c, balanced, 0.5)

            minDCF_9 = numpy.hstack(
                (minDCF_9, compute_min_DCF(numpy.hstack(lr9), numpy.hstack(labelLr9), 0.5, C_fn, C_fp)))

            lr8, _, _, labelLr8 = self.kfold_SVM(DP_8, LTR, K, c, balanced, 0.5) #prova con pca sempre 9 ma con true su znorm

            minDCF_8 = numpy.hstack(
                (minDCF_8, compute_min_DCF(numpy.hstack(lr8), numpy.hstack(labelLr8), 0.5, C_fn, C_fp)))

            lrz, _, _, labelLrz = self.kfold_SVM(DTR, LTR, K, c, balanced, 0.5, True)

            minDCF_z = numpy.hstack(
                (minDCF_z, compute_min_DCF(numpy.hstack(lrz), numpy.hstack(labelLrz), 0.5, C_fn, C_fp)))

        self.PLT.plot_DCF_compare_PCA_SVM(C_arr, numpy.hstack(minDCF_LR), numpy.hstack(minDCF_9), numpy.hstack(minDCF_8),
                                          numpy.hstack(minDCF_z))
        self.PLT.plot_DCF_lambda(C_arr, numpy.hstack(minDCF_pol_0_5), numpy.hstack(minDCF_pol_0_1),numpy.hstack(minDCF_pol_0_9), 'C', 'Pol')
        self.PLT.plot_DCF_lambda(C_arr, numpy.hstack(minDCF_rbf_0_5), numpy.hstack(minDCF_rbf_0_1),numpy.hstack(minDCF_rbf_0_9), 'C', 'RBF')

    def _getScoreGMM(self, D, L, Dte, components, componentsNT, a, p, llrGMM_full, llr_GMM_naive, llr_GMM_Tied, llr_GMM_TiedNaive):
        llrGMM_f = self.GMM.predict_GMM_full(D, L, Dte, components, componentsNT, a, p)
        llrGMM_n = self.GMM.predict_GMM_naive(D, L, Dte, components, componentsNT, a, p)
        llrGMM_t = self.GMM.predict_GMM_TiedCov(D, L, Dte, components, componentsNT, a, p)
        llrGMM_tn = self.GMM.predict_GMM_TiedNaive(D, L, Dte, components, componentsNT, a, p)
        llrGMM_full.append(llrGMM_f)
        llr_GMM_naive.append(llrGMM_n)
        llr_GMM_Tied.append(llrGMM_t)
        llr_GMM_TiedNaive.append(llrGMM_tn)
        

    def kfold_GMM(self,k, DTR, LTR, components, componentsNT,a,p,):

        llr_GMM_full = []
        llr_GMM_naive = []
        llr_GMM_Tied = []
        llr_GMM_TiedNaive = []
        labelGMM = []
        Dtr = numpy.split(DTR.T, k, axis=1)
        Ltr = numpy.split(LTR, k)

        for i in range(k):
            Dte = Dtr[i]
            Lte = Ltr[i]
            D = []
            L = []

            for j in range(k):
                if j != i:
                    D.append(Dtr[j])
                    L.append(Ltr[j])

            D = numpy.hstack(D)
            L = numpy.hstack(L)

            labelGMM = numpy.append(labelGMM, Lte, axis=0)
            self._getScoreGMM(D,L,Dte,components,componentsNT, a,p, llr_GMM_full, llr_GMM_naive, llr_GMM_Tied,llr_GMM_TiedNaive)

        return llr_GMM_full, llr_GMM_naive,llr_GMM_Tied, llr_GMM_TiedNaive, labelGMM

    '''GMM VALIDATION'''

    def plot_GMM_full(self, DTR, LTR,pi, a,p, Cfn,Cfp):
        data = {
            "Non-target K = 1": [],
            "Non-target K = 2": [],
            "Non-target K = 4": [],
            "Non-target K = 8": [],
            "Non-target K = 16": [],
            "Non-target K = 32": []
        }
        for i in range(0, 6):
            # TARGET 1
            llr_GMM_Full, _, _, _, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 1, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_Full)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))
            # TARGET 2
            llr_GMM_Full, _, _, _, _ = self.kfold_GMM(5, DTR, LTR, 2, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_Full)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))
            # TARGET 4
            llr_GMM_Full, _, _, _, _ = self.kfold_GMM(5, DTR, LTR, 4, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_Full)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))

        self.PLT.plot_bar_GMM(data)
    def plot_GMM_NAIVE(self, DTR, LTR,pi, a,p, Cfn,Cfp):
        data = {
            "Non-target K = 1": [],
            "Non-target K = 2": [],
            "Non-target K = 4": [],
            "Non-target K = 8": [],
            "Non-target K = 16": [],
            "Non-target K = 32": []
        }
        for i in range(0, 6):
            # TARGET 1
            _, llr_GMM_Naive, _, _, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 1, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_Naive)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))
            # TARGET 2
            _, llr_GMM_Naive, _, _, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 2, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_Naive)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))
            # TARGET 4
            _, llr_GMM_Naive, _, _, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 4, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_Naive)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))

        self.PLT.plot_bar_GMM(data)
    def plot_GMM_TIED(self, DTR, LTR,pi, a,p, Cfn,Cfp):
        data = {
            "Non-target K = 1": [],
            "Non-target K = 2": [],
            "Non-target K = 4": [],
            "Non-target K = 8": [],
            "Non-target K = 16": [],
            "Non-target K = 32": []
        }
        for i in range(0, 6):
            # TARGET 1
            _, _, llr_GMM_Tied, _, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 1, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_Tied)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))
            # TARGET 2
            _, _, llr_GMM_Tied, _, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 2, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_Tied)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))
            # TARGET 4
            _, _, llr_GMM_Tied, _, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 4, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_Tied)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))

        self.PLT.plot_bar_GMM(data)

    def plot_GMM_NAIVETIED(self, DTR, LTR,pi, a,p, Cfn,Cfp):
        data = {
            "Non-target K = 1": [],
            "Non-target K = 2": [],
            "Non-target K = 4": [],
            "Non-target K = 8": [],
            "Non-target K = 16": [],
            "Non-target K = 32": []
        }
        for i in range(0, 6):
            # TARGET 1
            _, _, _, llr_GMM_TiedNaive, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 1, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_TiedNaive)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))
            # TARGET 2
            _, _, _, llr_GMM_TiedNaive, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 2, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_TiedNaive)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))
            # TARGET 4
            _, _, _, llr_GMM_TiedNaive, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 4, 2 ** i, a, p)
            llr = numpy.hstack(llr_GMM_TiedNaive)
            scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
            data["Non-target K = " + str(2 ** i)].append(round(scores_tot, 3))

        self.PLT.plot_bar_GMM(data)

    def GMM_validation(self,DTR,LTR, pi, Cfn, Cfp,comp, compNT,a,p, plot=False ):

        llr_GMM_Full, llr_GMM_Naive, llr_GMM_Tied,llr_GMM_TiedNaive,llr_GMM_labels= self.kfold_GMM(5, DTR, LTR, comp,compNT, a, p)
        print("##########GMM FULL##########")
        llr = numpy.hstack(llr_GMM_Full)
        scores_tot = compute_min_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp)
        print(f'- components  %1i | with prior = {pi} -> minDCF = %.3f ' % (comp,scores_tot))
        rettt = compute_act_DCF(llr, llr_GMM_labels, pi, Cfn, Cfp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)

        print("##########GMM NAIVE##########")
        llrN = numpy.hstack(llr_GMM_Naive)
        scores_totN = compute_min_DCF(llrN, llr_GMM_labels, pi, Cfn, Cfp)
        print(f'- components  %1i | with prior = {pi} -> minDCF = %.3f ' % (comp, scores_totN))
        rettt = compute_act_DCF(llrN, llr_GMM_labels, pi, Cfn, Cfp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)

        print("##########GMM TIED##########")
        llrT = numpy.hstack(llr_GMM_Tied)
        scores_totT = compute_min_DCF(llrT, llr_GMM_labels, pi, Cfn, Cfp)
        print(f'- components  %1i | with prior = {pi} -> minDCF = %.3f ' % (comp, scores_totT))
        rettt = compute_act_DCF(llrT, llr_GMM_labels, pi, Cfn, Cfp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)

        print("##########GMM TIED NAIVE##########")
        llrTN = numpy.hstack(llr_GMM_TiedNaive)
        scores_totTN = compute_min_DCF(llrTN, llr_GMM_labels, pi, Cfn, Cfp)
        print(f'- components  %1i | with prior = {pi} -> minDCF = %.3f ' % (comp, scores_totTN))
        rettt = compute_act_DCF(llrTN, llr_GMM_labels, pi, Cfn, Cfp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)


        if plot:
            print("Plotting it may take a while")
            bayes_error_min_act_plot(numpy.hstack(llr_GMM_Naive), llr_GMM_labels, 1)
            self.plot_GMM_full(DTR,LTR,pi,a,p, Cfn,Cfp)
            self.plot_GMM_NAIVE(DTR,LTR,pi,a,p,Cfn,Cfp)
            self.plot_GMM_TIED(DTR,LTR,pi,a,p,Cfn,Cfp)
            self.plot_GMM_NAIVETIED(DTR,LTR,pi,a,p, Cfn, Cfp)


    def plot_minDCF_cal_score(self,DTR,LTR, pi):
        #MVG
        DP_8 = self.dimRed.PCA(DTR, 8)
        llrMVG,_, _,_, labelMVG = self.k_fold_MVG(5, DP_8.T, LTR)
        #qlog
        DP_7 = self.dimRed.PCA(DTR,7)
        _, lrQ, labelLr = self.k_fold_LR(5, DP_7.T, LTR, pi, 0.01, False)
        _w, _b = self.LR.compute_scores_param(numpy.hstack(lrQ), labelLr, 0.01, 0.7)
        cal_score_lr = _w * lrQ + _b - numpy.log(pi / (1 - pi))
        #svm
        _, _, scoresRBF_append, SVM_labels = self.kfold_SVM(DTR.T, LTR, 0.1, 10, False, pi, "rbf")
        _w, _b = self.LR.compute_scores_param(numpy.hstack(scoresRBF_append), SVM_labels, 0.01, 0.7)
        cal_score_RBF = _w * scoresRBF_append + _b - numpy.log(pi / (1 - pi))
        #gmm
        _, llr_GMM_Naive, _, _, llr_GMM_labels = self.kfold_GMM(5, DTR, LTR, 1, 8, 0.1, 0.01)

        bayes_error_min_act_plot_compare(numpy.hstack(llrMVG), numpy.hstack(cal_score_lr), numpy.hstack(cal_score_RBF), numpy.hstack(llr_GMM_Naive), labelMVG, labelLr, SVM_labels, llr_GMM_labels, 1)




    def plot_ROC(self, DTR, LTR, pi):
        #MVG
        DP_8 = self.dimRed.PCA(DTR, 8)
        llrMVG, _, _, _, labelMVG = self.k_fold_MVG(5, DP_8.T, LTR)
        #minDCF_MVG = compute_min_DCF(numpy.hstack(llrMVG),numpy.hstack(labelMVG), pi, 1, 10)
        #qlog
        DP_7 = self.dimRed.PCA(DTR, 7)
        _, lrQ, labelLR = self.k_fold_LR(5, DP_7.T, LTR, pi, 0.01, False)
        #minDCF_LRQ = compute_min_DCF(numpy.hstack(lrQ), numpy.hstack(labelLR), pi, 1, 10)
        #svm rbf
        _, _, lRBF, labelRBF = self.kfold_SVM(DP_7, LTR, 0.1, 10, False, pi, "rbf")
        #minDCF_RBF = compute_min_DCF(numpy.hstack(lRBF), numpy.hstack(labelRBF), pi, 1, 10)
        #gmm naive
        _, llrGMMN, _, _, labelGMM = self.kfold_GMM(5, DP_7.T, LTR, 1, 8, 0.1, 0.01)
        #minDCF_GMMN = compute_min_DCF(numpy.hstack(llrGMMN), numpy.hstack(labelGMM), pi, 1, 10)
        self.PLT.ROC_curve(numpy.hstack(llrMVG), numpy.hstack(lrQ), numpy.hstack(lRBF), numpy.hstack(llrGMMN), labelMVG, labelLR, labelRBF, labelGMM)
