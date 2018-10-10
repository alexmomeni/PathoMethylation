import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from datasets import DatasetML
from scipy import interp
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, precision_recall_curve, roc_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB, BernoulliNB
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV


class Model(object):
    
    def __init__(self, config):
        
        self.config = config
        self.data_init()
        self.model_init() 
        if os.path.isdir("output/%s/%s/%s/"%(self.config.source,self.config.folder,self.config.models)):
            pass
        else:
            os.makedirs("output/%s/%s/%s/"% (self.config.source,self.config.folder,self.config.models))
 
    def data_init(self):
        pass
    
    def model_init(self):
        pass
    
    def train_predict(self):
        pass

    def get_metrics(self, y_scores, y_preds):
        
        list_of_metrics = ["accuracy", "precision", "recall", "f1score", "AUC", "AP"]
        self.metrics = pd.DataFrame(data=np.zeros((len(self.tasks), len(list_of_metrics))), index=self.tasks,
                                    columns=list_of_metrics)
        for task in range(len(self.tasks)):
            y_true = self.y_test[task]
            y_pred = y_preds[task]
            y_score = y_scores[task]
            accuracy = accuracy_score(y_true, y_pred, normalize=True)
            precision = precision_score(y_true, y_pred, average='macro')
            recall = recall_score(y_true, y_pred, average='macro')
            f1score = f1_score(y_true, y_pred, average='macro')
            if len(np.unique(y_true)) != 1:
                auc = roc_auc_score(y_true, y_score)
                avg_precision = average_precision_score(y_true, y_score)
            else:
                auc = np.nan
                avg_precision = np.nan
            self.metrics.iloc[task,:] = [accuracy, precision, recall, f1score, auc, avg_precision]
        self.metrics.to_csv("output/%s/%s/%s/metrics"%(self.config.source,self.config.folder,self.config.models))

    def plot_ROCs(self, y_scores):
        
        fig = plt.figure(figsize=(10,10))
        tprs = []
        aucs = []
        mean_fpr = np.linspace(0, 1, 100)
        for task in range(len(self.tasks)):
            y_true = self.y_test[task]
            y_score = y_scores[task]
            if len(np.unique(y_true)) != 1:
                fpr, tpr, _ = roc_curve(y_true, y_score)
                tprs.append(interp(mean_fpr, fpr, tpr))
                tprs[-1][0] = 0.0
                aucs.append(roc_auc_score(y_true, y_score))
                plt.plot(fpr, tpr, lw=1, c='b', alpha=0.3)
        plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='black', label='Luck', alpha=.8)
        mean_tpr = np.mean(tprs, axis=0)
        mean_tpr[-1] = 1.0
        mean_auc = np.mean(aucs)
        std_auc = np.std(aucs)
        plt.plot(mean_fpr, mean_tpr, color='r',
                 label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
                 lw=2, alpha=.8)
        std_tpr = np.std(tprs, axis=0)
        tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
        tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
        plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                         label=r'$\pm$ 1 std. dev.')
        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title("Average ROC curve for %s"%self.config.models)
        plt.legend(loc="lower right")
        fig.savefig("output/%s/%s/%s/ROC_curve"%(self.config.source,self.config.folder,self.config.models))
        plt.close()
        
        self.config.ax1.plot(mean_fpr, mean_tpr,
                 label=r'%s (AUC = %0.2f)' % (self.config.models, mean_auc),
                 lw=2, alpha=.8)
        self.config.ax1.legend(loc="lower right")

    def plot_PRs(self, y_scores):
        
        fig = plt.figure(figsize=(10,10))
        precisions = []
        avg_precisions = []
        mean_recall = np.linspace(0, 1, 100)
        for task in range(len(self.tasks)):
            y_true = self.y_test[task]
            y_score = y_scores[task]
            if len(np.unique(y_true)) != 1:
                precision, recall, _ = precision_recall_curve(y_true, y_score)
                precisions.append(interp(mean_recall, recall[::-1], precision[::-1]))
                #precisions[-1][0] = 1.0
                avg_precisions.append(average_precision_score(y_true, y_score))
                plt.plot(recall, precision, lw=1, c='b', alpha=0.3)
        mean_precision = np.mean(precisions, axis=0)
        mean_avg_precision = np.mean(avg_precisions)
        std_avg_precision = np.std(avg_precisions)
        plt.plot(mean_recall, mean_precision, color='r',
                 label=r'Mean PR curve (AP = %0.2f $\pm$ %0.2f)' % (mean_avg_precision, std_avg_precision),
                 lw=2, alpha=.8)
        std_precision = np.std(precisions, axis=0)
        precisions_upper = np.minimum(mean_precision + std_precision, 1)
        precisions_lower = np.maximum(mean_precision - std_precision, 0)
        plt.fill_between(mean_recall, precisions_lower, precisions_upper, color='grey', alpha=.2,
                         label=r'$\pm$ 1 std. dev.')
        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title("Average PR curve for %s"%self.config.models)
        plt.legend(loc="lower right")
        fig.savefig("output/%s/%s/%s/PR_curve"%(self.config.source,self.config.folder,self.config.models))
        plt.close()
        
        self.config.ax2.plot(mean_recall, mean_precision,
                 label=r'%s (AP = %0.2f)' % (self.config.models, mean_avg_precision),
                 lw=2, alpha=.8)
        self.config.ax2.legend(loc="lower right")


class ModelML(Model):
    
    def __init__(self, config):
        Model.__init__(self, config)
 
    def data_init(self):
        
        self.dataset = DatasetML(self.config)
        self.tasks = list(self.dataset.DMvalues.columns)
        indices = np.random.permutation(self.dataset.morpho_context.index)
        self.dataset.morpho_context = self.dataset.morpho_context.loc[indices,:]
        self.dataset.DMvalues = self.dataset.DMvalues.loc[indices,:]
        self.dataset.DMvalues.to_csv("DM_values")
        idx_test = int((1-self.config.test_size)*len(self.dataset.DMvalues))
        self.X_train, self.X_test = np.split(self.dataset.morpho_context, [idx_test])
        print('Number of patients',self.dataset.DMvalues.shape[0])
        print('Number of genes', self.dataset.DMvalues.shape[1])
        self.y_train, self.y_test = np.split(self.dataset.DMvalues, [idx_test])
        self.y_train = [self.y_train[task].values for task in self.tasks]
        self.y_test = [self.y_test[task].values for task in self.tasks]

    def model_init(self):
        
        if self.config.classifier == "rf":
            parameters = {'n_estimators':[10,100,1000], 'criterion':['gini'], 'min_samples_split':[2], 'min_samples_leaf':[2]}
            self.model = GridSearchCV(RandomForestClassifier(), parameters, cv=5, n_jobs=10)            
            
        if self.config.classifier == "lr":
            parameters = {'penalty':['l1'], 'C':[100], 'fit_intercept':[True]}
            self.model = GridSearchCV(LogisticRegression(), parameters, cv=5, n_jobs=10)
        if self.config.classifier == "svm":
            parameters = {'C':[1], 'kernel':['linear'], 'probability':[True]}
            self.model = GridSearchCV(SVC(), parameters, cv=5, n_jobs=10)
        if self.config.classifier == "nb":
            parameters = {'alpha':[1.0], 'binarize':[0.0]}
            self.model = GridSearchCV(BernoulliNB(), parameters, cv=5, n_jobs=10)
        if self.config.classifier == "nn":
            parameters = {'hidden_layer_sizes':[(100, )], 'activation':['relu'], 'solver':['adam'],
                          'alpha':[0.0001], 'learning_rate':['constant'],
                          'learning_rate_init':[0.001], 'max_iter':[1000]}
            self.model = GridSearchCV(MLPClassifier(), parameters, cv=5, n_jobs=10)
    
    def train_predict(self):
        """
        optional: n_iterations to reduce variance
        """
        self.coefficients = pd.DataFrame(data=np.zeros((self.X_train.shape[1], len(self.tasks))),
                                         index=self.X_train.columns, columns=self.tasks)
        y_scores, y_preds = [], []
        for task in range(len(self.tasks)):
            self.model.fit(self.X_train, self.y_train[task])
            y_scores.append(self.model.predict_proba(self.X_test)[:,1])
            y_preds.append(self.model.predict(self.X_test))
            if self.config.classifier == "rf":
                self.coefficients.iloc[:,task] = self.model.best_estimator_.feature_importances_
            if self.config.classifier == "lr":
                self.coefficients.iloc[:,task] = self.model.best_estimator_.coef_.T
        self.coefficients.to_csv("output/%s/%s/%s/coefficients"%(self.config.source,self.config.folder,self.config.models))
        self.params = self.model.best_params_
        print(self.params)
        
        self.importances = np.sum(abs(self.coefficients), axis=1)
        self.importances.sort_values(ascending=False, inplace=True)
        self.importances = 100*(self.importances/sum(self.importances))[0:10]
        indices = [list(self.coefficients.index.values).index(self.importances.index[i]) for i in range(10)]
        self.importances = pd.DataFrame(np.array((self.importances, indices)).T, index = self.importances.index,
                               columns = ["importance (%)", "index"])
        np.save("output/%s/%s/%s/y_scores"%(self.config.source,self.config.folder,self.config.models), y_scores)
        np.save("output/%s/%s/%s/y_preds"%(self.config.source,self.config.folder,self.config.models), y_preds)

        return y_scores, y_preds
