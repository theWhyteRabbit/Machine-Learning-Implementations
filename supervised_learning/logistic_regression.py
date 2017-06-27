import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets

# Add base directory of project to path.
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + "/..")

from optimization_algorithms.cost_graph import OptimizerCostGraph
from optimization_algorithms.optimizer import Optimizer
from optimization_algorithms.gradient_descent import GradientDescent
from util.data_operation import mean_square_error
from util.data_manipulation import train_test_split
from util.graphing import class_estimation_graph

class LogisticRegression(object):
    """
    Standard Logistic Regression classifier using the maximum likelihood model.
    
    Will add a bias term to X, and otherwise not alter the data at all.
    
    Parameters
    --------
    optimizer : optimization_algorithms.Optimizer
        Will calculate the weights using the logistic function
    
    Theory
    --------
        - Highly dependent on decision boundary being linear combination of \
        provided feature set (which may not be a linear combination of original \
        feature set).
            - Decision boundary is where dot(x, theta) = 0.
        - Has low variance and high bias
            - More features it has, the more this shifts to high variance low bias.
            - To reduce overfitting it may be helpful to prune the feature set.
        - Easy to understand the effect of a single or set of features on output
            - Look at their weight. If >0, then increases likelihood, otherwise decreases
        - Just supports binary features (0 or 1).
            - To have multiple classification, create + train a LogisticRegression \
            for each class, determining how likely it is to occur. Then, for each new \
            input, class is the most likely class.
    """
    
    def __init__(self, optimizer):
        self._optimizer = optimizer
        self._weights = None
        self._intercept = None
        self._coeff = None
        
    def fit(self, X, y):
        """
        Fit internal parameters to minimize MSE on given X y dataset.
        
        Will add a bias term to X.
        
        Parameters
        ---------
        
        X : array-like, shape [n_samples, n_features]
            Input array of features.
            
        y : array-like, shape [n_samples,] or [n_samples,n_values]
            Input array of expected results. Must be binary (0 or 1)
        """
        # Add bias columns as first column
        X = np.insert(X, 0, 1, axis=1)
        
        num_features = np.shape(X)[1]
        self._weights = np.zeros((num_features, ))
        self._weights, status = self._optimizer.optimize(
                X, y,
                self._weights,
                LogisticRegression._logistic_function,
                LogisticRegression._cost_function)

        if (status != Optimizer.Status.CONVERGED):
            print("WARNING: Optimizer did not converge:", self._optimizer.converge_hints())
        
        self._intercept = self._weights[0]
        self._coeff = self._weights[1:]
        
    def predict(self, X):
        """
        Predict the value(s) associated with each row in X.
        
        X must have the same size for n_features as the input this instance was
        trained on.
        
        Parameters
        ---------
        
        X : array-like, shape [n_samples, n_features]
            Input array of features.
            
        Returns
        ---------
        Values in range [0, 1] indicating how sure the predictor is that a value
        is 1. To choose most likely, use np.round.
        """
        X = np.insert(X, 0, 1, axis=1)
        return LogisticRegression._logistic_function(X, self._weights)
    
    def _logistic_function(X, theta):
        value = np.dot(X, theta)
        return 1 / (1 + np.exp(-value))
    
    def _cost_function(X, pred, y):
        """
        Cost using the logistic function.
        """
        m = len(y)
        cost = 1/m * (-np.dot(y.T, np.log(pred)) - np.dot((1-y), np.log(1-pred)))
        gradient = 1/m * np.dot(X.T, (pred - y))
        return (cost, gradient)
        
    def get_feature_params(self):
        return self._coeff


if __name__ == "__main__":
    # Just has one feature to make it easy to graph.
    X, y = datasets.make_classification(n_samples=200, n_features=1, n_informative=1, n_redundant=0,
                                        n_clusters_per_class=1, flip_y=0.1)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_proportion=0.2)
    
    logistic_reg = LogisticRegression(optimizer=OptimizerCostGraph(GradientDescent(num_iterations=20000), iterations_per_update=500))
    logistic_reg.fit(X_train, y_train)
    
    y_pred = logistic_reg.predict(X_test)
    mse = mean_square_error(y_pred, y_test)
    
    y_pred_rounded = np.round(y_pred)
    mse_rounded = mean_square_error(y_pred_rounded, y_test)
    
    plt.figure()
    plt.scatter(X_test, y_test, color="Black", label="Actual")
    plt.scatter(X_test, y_pred, color="Red", label="Prediction")
    plt.scatter(X_test, y_pred_rounded, color="Blue", label="Rounded Prediction")
    plt.legend(loc='center right', fontsize=8)
    plt.title("Logistic Regression %.2f MSE, %.2f MSE with Rounding)" % (mse, mse_rounded))
    plt.show()