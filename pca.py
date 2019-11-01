# Principal Component Analysis
from numpy import cov
from numpy.linalg import eig
from sklearn.decomposition import PCA

def pcaFnc(arr):
    v = cov(arr)
    values, vectors = eig(v)
    projected = (vectors.T).dot(arr)
    print('array', arr, '\nvalues: \n', values, '\nvectors: \n', vectors, '\nprojected: \n', projected)
    return values, vectors, projected
def test():
    pcaFnc()
if __name__ == '__main__':
    test()