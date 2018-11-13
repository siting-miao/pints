#!/usr/bin/env python
#
# Tests the Normal logpdf toy distribution.
#
# This file is part of PINTS.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the PINTS
#  software package.
#
import pints
import pints.toy
import unittest
import numpy as np


class TestNormalLogPDF(unittest.TestCase):
    """
    Tests the normal logpdf toy distribution.
    """
    def test_normal_logpdf(self):
        """
        Test NormalLogPDF basics.
        """
        # Test basics
        x = [1, 2, 3]
        y = [1, 1, 1]
        f = pints.toy.NormalLogPDF(x, y)
        self.assertEqual(f.n_parameters(), len(x))
        self.assertTrue(np.isscalar(f(x)))

        x = [1, 2, 3]
        y = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        f = pints.toy.NormalLogPDF(x, y)
        self.assertEqual(f.n_parameters(), len(x))
        self.assertTrue(np.isscalar(f(x)))

        # Test errors
        self.assertRaises(
            ValueError, pints.toy.NormalLogPDF, [1, 2, 3], [[1, 2], [3, 4]])
        self.assertRaises(
            ValueError, pints.toy.NormalLogPDF, [1, 2, 3], [1, 2, 3, 4])

    def test_sampling_and_kl_divergence(self):
        """
        Test NormalLogPDF.kl_divergence() and .sample().
        """
        # Ensure consistent output
        np.random.seed(1)

        # Create LogPDFs
        d = 3
        mean = np.array([3, -3.0, 0])
        sigma = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1.0]])
        log_pdf1 = pints.toy.NormalLogPDF(mean, sigma)
        log_pdf2 = pints.toy.NormalLogPDF(mean + 0.1, sigma)
        log_pdf3 = pints.toy.NormalLogPDF(mean - 0.2, sigma / 2)

        # Sample from each
        n = 10000
        samples1 = log_pdf1.sample(n)
        samples2 = log_pdf2.sample(n)
        samples3 = log_pdf3.sample(n)

        # Compare calculated divergences
        s11 = log_pdf1.kl_divergence(samples1)
        s12 = log_pdf1.kl_divergence(samples2)
        s13 = log_pdf1.kl_divergence(samples3)
        self.assertLess(s11, s12)
        self.assertLess(s11, s13)

        s21 = log_pdf2.kl_divergence(samples1)
        s22 = log_pdf2.kl_divergence(samples2)
        s23 = log_pdf2.kl_divergence(samples3)
        self.assertLess(s22, s21)
        self.assertLess(s22, s23)

        s31 = log_pdf3.kl_divergence(samples1)
        s32 = log_pdf3.kl_divergence(samples2)
        s33 = log_pdf3.kl_divergence(samples3)
        self.assertLess(s33, s32)
        self.assertLess(s33, s31)

        # Test sample() errors
        self.assertRaises(ValueError, log_pdf1.sample, -1)

        # Test kl_divergence() errors
        self.assertEqual(samples1.shape, (n, d))
        x = np.ones((n, d + 1))
        self.assertRaises(ValueError, log_pdf1.kl_divergence, x)
        x = np.ones((n, d, 2))
        self.assertRaises(ValueError, log_pdf1.kl_divergence, x)

    def test_normal_sensitivity(self):
        """
        Tests that the gradient of the log pdf is correct
        for a few specific examples, and that the log pdf
        returned is correct.
        """
        # 1d normal
        f1 = pints.toy.NormalLogPDF([0], [1])
        L, dL = f1.evaluateS1([2])
        self.assertAlmostEqual(L, -2.918938533204673)
        self.assertEqual(dL[0], -2)

        # 2d normal
        f2_1 = pints.toy.NormalLogPDF([0, 0], [[1, 0], [0, 1]])
        L, dL = f2_1.evaluateS1([2, 1])
        self.assertAlmostEqual(L, -4.337877066409345)
        self.assertTrue(np.array_equal(dL, [-2, -1]))

        f2_2 = pints.toy.NormalLogPDF([-5, 3], [[3, -0.5], [0.5, 2]])
        L, dL = f2_2.evaluateS1([-2.5, 1.5])

        # 3d normal
        f3 = pints.toy.NormalLogPDF([1, 2, 3], [[2, 0, 0],
                                                [0, 2, 0],
                                                [0, 0, 2]])
        L, dL = f3.evaluateS1([0.5, -5, -3])
        self.assertAlmostEqual(L, -25.10903637045394)
        self.assertTrue(np.array_equal(dL, [0.25, 3.5, 3.0]))


if __name__ == '__main__':
    unittest.main()
