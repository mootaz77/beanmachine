#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


# Suppose we have a mixture of k normal distributions each with standard
# deviation equal to 1, but different means. Our prior on means is that
# mean(0), ... mean(k) are normally distributed.
#
# To make samples mixed(0), ... from this distribution we first choose which
# mean we want with category(0), ..., use that to sample mean(category(0))
# to get the mean, and then use that mean to sample from a normal distribution.
#

import unittest

import beanmachine.ppl as bm
from beanmachine.ppl.inference import BMGInference
from torch import tensor
from torch.distributions import Categorical, Normal


@bm.random_variable
def mean(k):
    # Means of the components are normally distributed
    return Normal(0, 1)


@bm.random_variable
def category(item):
    # Choose a category, 0, 1 or 2 with ratio 1:3:4.
    return Categorical(tensor([1.0, 3.0, 4.0]))


@bm.random_variable
def mixed(item):
    return Normal(mean(category(item)), 2)


class GaussianMixtureModelTest(unittest.TestCase):
    def test_gmm_to_dot(self) -> None:
        self.maxDiff = None
        queries = [mixed(0)]
        observations = {}

        # Here we use a categorical distribution to choose from three possible
        # samples.
        #
        # TODO: The inference step on categorical distributions in BMG is not
        # yet implemented because the gradients are not yet computed correctly
        # and because BMG NMC does not yet implement a discrete sampler. Once
        # that work is complete, update this test to actually do inference.

        observed = BMGInference().to_dot(queries, observations)
        expected = """
digraph "graph" {
  N00[label="[0.125,0.375,0.5]"];
  N01[label=Categorical];
  N02[label=Sample];
  N03[label=0.0];
  N04[label=1.0];
  N05[label=Normal];
  N06[label=Sample];
  N07[label=Sample];
  N08[label=Sample];
  N09[label=Choice];
  N10[label=2.0];
  N11[label=Normal];
  N12[label=Sample];
  N13[label=Query];
  N00 -> N01;
  N01 -> N02;
  N02 -> N09;
  N03 -> N05;
  N04 -> N05;
  N05 -> N06;
  N05 -> N07;
  N05 -> N08;
  N06 -> N09;
  N07 -> N09;
  N08 -> N09;
  N09 -> N11;
  N10 -> N11;
  N11 -> N12;
  N12 -> N13;
}
"""
        self.assertEqual(expected.strip(), observed.strip())
