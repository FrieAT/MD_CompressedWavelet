# coding=utf-8
# source: https://github.com/bukalapak/pybrisque/
# Author: Akbar Gumbira

import os
from ctypes import c_double

import cv2
import numpy as np
from scipy.special import gamma

# import svmutil
# from svmutil import gen_svm_nodearray

# from brisque.utilities import root_path
from IProcess import IProcess, EDataType

class BRISQUE(IProcess):

    @staticmethod
    def preprocess_image(img):
        """Handle any kind of input for our convenience.
        :param img: The image path or array.
        :type img: str, np.ndarray
        """
        if isinstance(img, str):
            if os.path.exists(img):
                return cv2.imread(img, 0).astype(np.float64)
            else:
                raise FileNotFoundError('The image is not found on your '
                                        'system.')
        elif isinstance(img, np.ndarray):
            if len(img.shape) == 2:
                image = img
            elif len(img.shape) == 3:
                image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                raise ValueError('The image shape is not correct.')

            return image.astype(np.float64)
        else:
            raise ValueError('You can only pass image to the constructor.')

    @staticmethod
    def _estimate_ggd_param(vec):
        """Estimate GGD parameter.
        :param vec: The vector that we want to approximate its parameter.
        :type vec: np.ndarray
        """
        gam = np.arange(0.2, 10 + 0.001, 0.001)
        r_gam = (gamma(1.0 / gam) * gamma(3.0 / gam) / (gamma(2.0 / gam) ** 2))

        sigma_sq = np.mean(vec ** 2)
        sigma = np.sqrt(sigma_sq)
        E = np.mean(np.abs(vec))
        rho = sigma_sq / E ** 2

        differences = abs(rho - r_gam)
        array_position = np.argmin(differences)
        gamparam = gam[array_position]

        return gamparam, sigma

    @staticmethod
    def _estimate_aggd_param(vec):
        """Estimate AGGD parameter.
        :param vec: The vector that we want to approximate its parameter.
        :type vec: np.ndarray
        """
        gam = np.arange(0.2, 10 + 0.001, 0.001)
        r_gam = ((gamma(2.0 / gam)) ** 2) / (
                    gamma(1.0 / gam) * gamma(3.0 / gam))

        left_std = np.sqrt(np.mean((vec[vec < 0]) ** 2))
        right_std = np.sqrt(np.mean((vec[vec > 0]) ** 2))
        gamma_hat = left_std / right_std
        rhat = (np.mean(np.abs(vec))) ** 2 / np.mean((vec) ** 2)
        rhat_norm = (rhat * (gamma_hat ** 3 + 1) * (gamma_hat + 1)) / (
                (gamma_hat ** 2 + 1) ** 2)

        differences = (r_gam - rhat_norm) ** 2
        array_position = np.argmin(differences)
        alpha = gam[array_position]

        return alpha, left_std, right_std

    def get_feature(self, img):
        """Get brisque feature given an image.
        :param img: The path or array of the image.
        :type img: str, np.ndarray
        """
        imdist = self.preprocess_image(img)

        scale_num = 2
        feat = np.array([])

        for itr_scale in range(scale_num):
            mu = cv2.GaussianBlur(
                imdist, (7, 7), 7 / 6, borderType=cv2.BORDER_CONSTANT)
            mu_sq = mu * mu
            sigma = cv2.GaussianBlur(
                imdist * imdist, (7, 7), 7 / 6, borderType=cv2.BORDER_CONSTANT)
            sigma = np.sqrt(abs((sigma - mu_sq)))
            structdis = (imdist - mu) / (sigma + 1)

            alpha, overallstd = self._estimate_ggd_param(structdis)
            feat = np.append(feat, [alpha, overallstd ** 2])

            shifts = [[0, 1], [1, 0], [1, 1], [-1, 1]]
            for shift in shifts:
                shifted_structdis = np.roll(
                    np.roll(structdis, shift[0], axis=0), shift[1], axis=1)
                pair = np.ravel(structdis, order='F') * \
                       np.ravel(shifted_structdis, order='F')
                alpha, left_std, right_std = self._estimate_aggd_param(pair)

                const = np.sqrt(gamma(1 / alpha)) / np.sqrt(gamma(3 / alpha))
                mean_param = (right_std - left_std) * (
                        gamma(2 / alpha) / gamma(1 / alpha)) * const
                feat = np.append(
                    feat, [alpha, mean_param, left_std ** 2, right_std ** 2])

            imdist = cv2.resize(
                imdist,
                (0, 0),
                fx=0.5,
                fy=0.5,
                interpolation=cv2.INTER_NEAREST
            )
        return feat

    def get_score(self, img):
        """Get brisque score given an image.
        :param img: The path or array of the image.
        :type img: str, np.ndarray
        """
        feature = self.get_feature(img)
        scaled_feature = self._scale_feature(feature)

        return self._calculate_score(scaled_feature)

    def _scale_feature(self, feature):
        """Scale feature with svm scaler.
        :param feature: Brisque unscaled feature.
        :type feature: np.ndarray
        """
        y_lower = self._scaler[0][0]
        y_upper = self._scaler[0][1]
        y_min = self._scaler[1:, 0]
        y_max = self._scaler[1:, 1]
        scaled_feat = y_lower + (y_upper - y_lower) * ((feature - y_min) / (
                y_max - y_min))

        return scaled_feat

    def _calculate_score(self, scaled_feature):
        """Calculate score from scaled brisque feature.
        :param scaled_feature: Scaled brisque feature.
        :type scaled_feature: np.ndarray
        """
        x, idx = gen_svm_nodearray(
            scaled_feature.tolist(),
            isKernel=(self._model.param.kernel_type == 'PRECOMPUTED')
        )
        nr_classifier = 1
        prob_estimates = (c_double * nr_classifier)()

        return svmutil.libsvm.svm_predict_probability(
            self._model, x, prob_estimates)

    def toId(self):
        return str(__class__.__name__)

    def getType(self):
        return EDataType.BRISQUE

    def do(self, imageData):
        IProcess.do(self, imageData)
        inputImgData = np.array(self.data[-1])
        self.brisque_score = self.get_score(inputImgData, imageData)
        return self
