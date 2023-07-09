import numpy

from dimensionality_reduction import DimensionalityReduction
from gaussian_classifier import MultivariateGaussianClassifier
from logistic_regression import LogisticRegression
from svm import SupportVectorMachine
from GMM import GMM
from mlFunc import *
class Validation:
    def __init__(self):
        self.MVG = MultivariateGaussianClassifier()
        self.LR = LogisticRegression()
        self.svm = SupportVectorMachine()
        self.GMM = GMM()
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


    def MVG_validation(self, DTR, LTR, pi, C_fn, C_fp, DTE, LTE):
        #SU DTE
        # llrs = self.MVG.predict_MVG(DTR.T, LTR, DTE.T)
        # minDCF_MVG_test = compute_min_DCF(llrs,LTE, pi, C_fn, C_fp)
        # #s_MVG = self.MVG.predict_MVG(DTR.T,LTR , DTR.T)
        # actDCF_MVG_test = compute_act_DCF(llrs,LTE, pi, C_fn, C_fp)
        # #actDCF_MVG = compute_act_DCF(s_MVG, LTR, pi, C_fn, C_fp)
        # print("############MVG###############")
        # print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_MVG_test)
        # print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_MVG_test)


        llrMVG, llrNV, llrTCV,llrTNV, labelMVG = self.k_fold_MVG(5,DTR,LTR)

        minDCF_MVG = compute_min_DCF(numpy.hstack(llrMVG),numpy.hstack(labelMVG), pi, C_fn, C_fp)
        #s_MVG = self.MVG.predict_MVG(DTR.T,LTR , DTR.T)
        actDCF_MVG = compute_act_DCF(numpy.hstack(llrMVG), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        #actDCF_MVG = compute_act_DCF(s_MVG, LTR, pi, C_fn, C_fp)
        print("############MVG###############")
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_MVG)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_MVG)
        #bayes_error_min_act_plot(numpy.hstack(llrMVG),numpy.hstack(labelMVG), 1)

        print("############NAIVE BAYES#############")
        minDCF_NV = compute_min_DCF(numpy.hstack(llrNV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        actDCF_NV = compute_act_DCF(numpy.hstack(llrNV), numpy.hstack(labelMVG),pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_NV)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_NV)
        #bayes_error_min_act_plot(numpy.hstack(llrNV),LTR, 1)

        print("############TIED COV#############")
        minDCF_TCV = compute_min_DCF(numpy.hstack(llrTCV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        actDCF_TCV = compute_act_DCF(numpy.hstack(llrTCV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_TCV)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_TCV)
       # bayes_error_min_act_plot(numpy.hstack(llrTCV), numpy.hstack(labelMVG), 1)

        print("############TIED COV BAYES#############")
        minDCF_TNV = compute_min_DCF(numpy.hstack(llrTNV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        s_TNV = self.MVG.predict_MVG_Tied_Cov_Naive(DTR.T, LTR, DTR.T)
        actDCF_TNV = compute_act_DCF(numpy.hstack(llrTNV), numpy.hstack(labelMVG), pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_TNV)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_TNV)
       # bayes_error_min_act_plot(numpy.hstack(llrTNV), LTR, 1)

    def k_fold_LR(self,k,DTR,LTR):
        lr_score = []
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

            # Train the model
            labelLR = numpy.append(labelLR, Lte, axis=0)
            lr_score.append(self.LR.preditc_Logistic_Regression(D, L, Dte, 0.00001))


        return lr_score, labelLR

    def LR_validation(self,DTR, LTR, pi, C_fn, C_fp):
        lr, labelLr = self.k_fold_LR(5,DTR,LTR)
        print("############LOGISTIC REGRESSION#############")
        minDCF_LR = compute_min_DCF(numpy.hstack(lr), numpy.hstack(labelLr), pi, C_fn, C_fp)
        actDCF_LR = compute_act_DCF(numpy.hstack(lr), numpy.hstack(labelLr),pi, C_fn, C_fp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % minDCF_LR)
        print(f'- with prior = {pi} -> actDCF = %.3f' % actDCF_LR)

        #bayes_error_min_act_plot(s_LR, LTR, 1)

        #########################################################
        #                     BOH
        #########################################################


        # print("---------------MVG WITH LDA--------------------------")
        # self.MVG.setup_MVG(DP, LTR)
        # s1 = self.MVG.predict_MVG(DPE, LTE)
        # #DFC1 = evaluation(s1, LTE, 0.5, 1, 10)
        #bayes_error_min_act_plot(DTE.T, LTE, 2)

        #
        # print("---------------MVG NAIVE BAYES WITHOUT LDA--------------------------")
        # self.MVG.setup_MVG_Naive_Bayes(DTR.T, LTR)
        # s2 = self.MVG.predict_MVG_Naive_Bayes(DTE.T, LTE)
        # DFC2 = evaluation(s2, LTE, 0.5, 1, 10)
        # print(DFC2)
        # print("---------------MVG NAIVE BAYES WITH LDA--------------------------")
        #
        # self.MVG.setup_MVG_Naive_Bayes(DP, LTR)
        # s3 = self.MVG.predict_MVG_Naive_Bayes(DPE, LTE)
        # DFC3 = evaluation(s3, LTE, 0.5, 1, 10)
        # print(DFC3)
        # print("---------------MVG TIED COV WITHOUT LDA--------------------------")
        #
        # self.MVG.setup_MVG_Tied_Cov(DTR.T, LTR)
        # s4 = self.MVG.predict_MVG_Tied_Cov(DTE.T, LTE)
        # DFC4 = evaluation(s4, LTE, 0.5, 1, 10)
        #
        # print(DFC4)
        # print("---------------MVG TIED COV WITH LDA--------------------------")
        #
        # self.MVG.setup_MVG_Tied_Cov(DP, LTR)
        # self.MVG.predict_MVG_Tied_Cov(DPE, LTE)
        #
        # print("---------------MVG TIED COV + NAIVE WITHOUT LDA--------------------------")
        #
        # self.MVG.setup_MVG_Tied_Cov_Naive(DTR.T, LTR)
        # self.MVG.predict_MVG_Tied_Cov_Naive(DTE.T, LTE)
        #
        # print("---------------MVG TIED COV + NAIVE WITH LDA--------------------------")
        # self.MVG.setup_MVG_Tied_Cov_Naive(DP, LTR)
        # self.MVG.predict_MVG_Tied_Cov_Naive(DPE, LTE)
        #
        # print("---------------LOGISTIC REGRESSION WITHOUT LDA--------------------------")
        # self.LR.setup_Logistic_Regression(DTR.T, LTR, 0.1)
        # self.LR.preditc_Logistic_Regression(DTE.T, LTE, 0.1)
        #
        # print("---------------LOGISTIC REGRESSION WITH LDA--------------------------")
        # self.LR.setup_Logistic_Regression(DP, LTR, 0.1)
        # self.LR.preditc_Logistic_Regression(DPE, LTE, 0.1)

        #print("---------------SVM Linear REGRESSION WITHOUT LDA--------------------------")
        #self.svmLin.validation_SVM(DTR.T, LTR, [0.1], [1], "validation svm")
        #self.svmLin.evaluation_SVM(DTR.T, LTR, DTE.T, LTE, [0.1], [1], "ev svm")
        #self.svmLin.predict_primal_svm(DTE.T, LTE, 0.1)

        #print("---------------SVM Kernel Poly REGRESSION WITHOUT LDA--------------------------")
        #self.svmLin.setup_kernelPoly_svm(DTR.T, LTR, DTE.T, LTE)

        #print("---------------SVM Kernel RBG REGRESSION WITHOUT LDA--------------------------")
        #self.svmLin.setup_kernelRBF_svm(DTR.T, LTR, DTE.T, LTE)

    def get_scores_SVM(self, D, L, Dte, Lte, C, K, costant, degree, gamma, scoresLin_append, scoresPol_append, scoresRBF_append, balanced, pi):    

        scoresLin_append.append(self.svm.predict_SVM_Linear(D, L, C, K, Dte, balanced, pi))
        scoresPol_append.append(self.svm.predict_SVM_Pol(D, L, C, K, Dte, costant, degree))
        scoresRBF_append.append(self.svm.predict_SVM_RBF(D, L, C, K, Dte, gamma))

    def kfold_SVM(self, DTR, LTR, K, C, balanced, pi):
        k = 5
        Dtr = numpy.split(DTR, k, axis=1)
        Ltr = numpy.split(LTR, k)

        scoresLin_append = []
        scoresPol_append = []
        scoresRBF_append = []
        SVM_labels = []
        PCA_SVM_scoresLin_append = []
        PCA2_SVM_scoresLin_append = []

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

            costant = 0
            degree = 2
            gamma=0.001
            SVM_labels = numpy.append(SVM_labels, Lte, axis=0)
            SVM_labels = numpy.hstack(SVM_labels)

            self.get_scores_SVM(D, L, Dte, Lte, C, K, costant, degree, gamma, scoresLin_append, scoresPol_append, scoresRBF_append, balanced, pi)
        
        return scoresLin_append, scoresPol_append, scoresRBF_append, SVM_labels

        # plot_ROC(scoresLin_append, SVM_labels, appendToTitle + 'SVM, K=' + str(K) + ', C=' + str(C))

        # Cfn and Ctp are set to 1
        #bayes_error_min_act_plot(scoresLin_append, SVM_labels, appendToTitle + 'SVM, K=' + str(K) + ', C=' + str(C), 0.4)

        ###############################

        # π = 0.1
        #scores_tot = compute_min_DCF(scoresLin_append, SVM_labels, 0.1, 1, 1)
        #print(scores_tot)
        ###############################

        # π = 0.9
        #scores_tot = compute_min_DCF(scoresLin_append, SVM_labels, 0.9, 1, 1)
        #print(scores_tot)
    def kfold_calibration_SVM(self, DTR, LTR, K, C):
        k = 5
        Dtr = numpy.split(DTR, k, axis=1)
        Ltr = numpy.split(LTR, k)
        scoresLin_append = []
        scoresPol_append = []
        scoresRBF_append = []
        PCA_SVM_scoresLin_append = []
        PCA2_SVM_scoresLin_append = []
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

            Dte = Dtr[i]
            Lte = Ltr[i]

            costant = 0
            degree = 2
            gamma=0.001
            SVM_labels = numpy.append(SVM_labels, Lte, axis=0)
            SVM_labels = numpy.hstack(SVM_labels)

            scoresT_Lin = self.svm.predict_SVM_Linear(D, L, C, K, D)
            a,b = self.LR.compute_scores_param(scoresT_Lin, L, 1e-4 ,0.5)
            scoresV_Lin = self.svm.predict_SVM_Linear(D, L, C, K, Dte)
            computeLLR = a * scoresV_Lin + b - numpy.log(0.5 / (1 - 0.5))

            scoresLin_append.append(computeLLR)

            scoresT_Pol = self.svm.predict_SVM_Pol(D, L, C, K, D, costant, degree)
            a,b = self.LR.compute_scores_param(scoresT_Pol, L, 1e-4 ,0.5)
            scoresV_Pol = self.svm.predict_SVM_Pol(D, L, C, K, Dte, costant, degree)
            computeLLR = a * scoresV_Pol + b - numpy.log(0.5 / (1 - 0.5))

            scoresPol_append.append(computeLLR)

            scoresT_RBF = self.svm.predict_SVM_RBF(D, L, C, K, D, gamma)
            a,b = self.LR.compute_scores_param(scoresT_RBF, L, 1e-4 ,0.5)
            scoresV_RBF = self.svm.predict_SVM_RBF(D, L, C, K, Dte, gamma)
            computeLLR = a * scoresV_RBF + b - numpy.log(0.5 / (1 - 0.5))

            scoresRBF_append.append(computeLLR)           


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


    def SVM_validation(self, DTR, LTR, pi, Cfn, Cfp, K, C, balanced):
        scoresLin_append = []
        scoresPol_append = []
        scoresRBF_append = []
        SVM_labels = []
        DTR = DTR.T

        scoresLin_append, scoresPol_append, scoresRBF_append, SVM_labels = self.kfold_SVM(DTR, LTR, K, C, balanced, pi)

        print("##########LINEAR##########")
        scores_tot = compute_min_DCF(numpy.hstack(scoresLin_append), SVM_labels, pi, Cfn, Cfp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % scores_tot)

        rettt = compute_act_DCF(numpy.hstack(scoresLin_append), SVM_labels, pi, Cfn, Cfp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)

        print("##########POLYNOMIAL##########")
        scores_tot = compute_min_DCF(numpy.hstack(scoresPol_append), SVM_labels, pi, Cfn, Cfp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % scores_tot)

        rettt = compute_act_DCF(numpy.hstack(scoresPol_append), SVM_labels, pi, Cfn, Cfp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)


        print("##########RBF##########")
        scores_tot = compute_min_DCF(numpy.hstack(scoresRBF_append), SVM_labels, pi, Cfn, Cfp)
        print(f'- with prior = {pi} -> minDCF = %.3f' % scores_tot)

        rettt = compute_act_DCF(numpy.hstack(scoresRBF_append), SVM_labels, pi, Cfn, Cfp, None)
        print(f'- with prior = {pi} -> actDCF = %.3f' % rettt)

        cal_score_Lin, cal_score_Pol, cal_score_RBF, cal_label = self.kfold_calibration_SVM(DTR, LTR, K, C)
        rettt = compute_act_DCF(numpy.hstack(cal_score_Lin), cal_label, 0.5, 1, 10, None)
        print("ACT DFC ON TRAIN SVM Lin - CAL", rettt)
        rettt = compute_act_DCF(numpy.hstack(cal_score_Pol), cal_label, 0.5, 1, 10, None)
        print("ACT DFC ON TRAIN SVM Pol - CAL", rettt)
        rettt = compute_act_DCF(numpy.hstack(cal_score_RBF), cal_label, 0.5, 1, 10, None)
        print("ACT DFC ON TRAIN SVM RBF - CAL", rettt)

        K_arr = [0.1, 1.0, 10.0]
        C_arr = [0.01, 0.1, 1.0, 10.0]
        #C_arr = [0.1, 1.0, 10.0]
        #self.SVM_score_calibration(DTR, LTR, K_arr, C_arr, pi, Cfn, Cfp)

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

            # Train the model
            labelGMM = numpy.append(labelGMM, Lte, axis=0)
            self._getScoreGMM(D,L,Dte,components,componentsNT, a,p, llr_GMM_full, llr_GMM_naive, llr_GMM_Tied,llr_GMM_TiedNaive)

        return llr_GMM_full, llr_GMM_naive,llr_GMM_Tied, llr_GMM_TiedNaive, labelGMM


            #llr_GMM_full.append(self.LR.preditc_Logistic_Regression(D, L, Dte, 0.00001))

    def GMM_validation(self,DTR,LTR, pi, Cfn, Cfp,comp, compNT,a,p ):

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
