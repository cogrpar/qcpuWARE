# Copyright 2018 D-Wave Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# ================================================================================================
"""
A dimod sampler_ that uses the simulated annealing algorithm.

"""
from __future__ import division

import math
import warnings

from numbers import Integral
from random import randint
from collections import defaultdict

import dimod
import numpy as np

from six import itervalues, iteritems

import neal.simulated_annealing as sa


__all__ = ["Neal", "SimulatedAnnealingSampler", "default_beta_range"]


class SimulatedAnnealingSampler(dimod.Sampler):
    """Simulated annealing sampler.

    Also aliased as :class:`.Neal`.

    Examples:
        This example solves a simple Ising problem.

        >>> import neal
        >>> sampler = neal.SimulatedAnnealingSampler()
        >>> h = {'a': 0.0, 'b': 0.0, 'c': 0.0}
        >>> J = {('a', 'b'): 1.0, ('b', 'c'): 1.0, ('a', 'c'): 1.0}
        >>> response = sampler.sample_ising(h, J)
        >>> for sample in response:  # doctest: +SKIP
        ...     print(sample)
        ... {'a': -1, 'b': 1, 'c': -1}
        ... {'a': -1, 'b': 1, 'c': 1}
        ... {'a': 1, 'b': 1, 'c': -1}
        ... {'a': 1, 'b': -1, 'c': -1}
        ... {'a': 1, 'b': -1, 'c': -1}
        ... {'a': 1, 'b': -1, 'c': -1}
        ... {'a': -1, 'b': 1, 'c': 1}
        ... {'a': 1, 'b': 1, 'c': -1}
        ... {'a': -1, 'b': -1, 'c': 1}
        ... {'a': -1, 'b': 1, 'c': 1}

    """

    parameters = None
    """dict: A dict where keys are the keyword parameters accepted by the sampler methods
    (allowed kwargs) and values are lists of :attr:`SimulatedAnnealingSampler.properties`
    relevant to each parameter.

    See :meth:`.SimulatedAnnealingSampler.sample` for a description of the parameters.

    Examples:
        This example looks at a sampler's parameters and some of their values.

        >>> import neal
        >>> sampler = neal.SimulatedAnnealingSampler()
        >>> for kwarg in sorted(sampler.parameters):
        ...     print(kwarg)
        beta_range
        beta_schedule_type
        num_reads
        seed
        num_sweeps
        >>> sampler.parameters['beta_range']
        []
        >>> sampler.parameters['beta_schedule_type']
        ['beta_schedule_options']

    """

    properties = None
    """dict: A dict containing any additional information about the sampler.

    Examples:
        This example looks at the values set for a sampler property.

        >>> import neal
        >>> sampler = neal.SimulatedAnnealingSampler()
        >>> sampler.properties['beta_schedule_options']
        ('linear', 'geometric')

    """

    def __init__(self):
        # create a local copy in case folks for some reason want to modify them
        self.parameters = {'beta_range': [],
                           'num_reads': [],
                           'num_sweeps': [],
                           'beta_schedule_type': ['beta_schedule_options'],
                           'seed': [],
                           'interrupt_function': [],
                           'initial_states': [],
                           'initial_states_generator': [],
                           }
        self.properties = {'beta_schedule_options': ('linear', 'geometric')
                           }

    def sample(self, bqm, beta_range=None, num_reads=None, num_sweeps=1000,
               beta_schedule_type="geometric", seed=None, interrupt_function=None,
               initial_states=None, initial_states_generator="random", **kwargs):
        """Sample from a binary quadratic model using an implemented sample method.

        Args:
            bqm (:class:`dimod.BinaryQuadraticModel`):
                The binary quadratic model to be sampled.

            beta_range (tuple, optional):
                A 2-tuple defining the beginning and end of the beta schedule, where beta is the
                inverse temperature. The schedule is applied linearly in beta. Default range is set
                based on the total bias associated with each node.

            num_reads (int, optional, default=len(initial_states) or 1):
                Number of reads. Each read is generated by one run of the simulated
                annealing algorithm. If `num_reads` is not explicitly given, it is
                selected to match the number of initial states given. If initial states
                are not provided, only one read is performed.

            num_sweeps (int, optional, default=1000):
                Number of sweeps or steps.

            beta_schedule_type (string, optional, default='geometric'):
                Beta schedule type, or how the beta values are interpolated between
                the given 'beta_range'. Supported values are:

                * linear
                * geometric

            seed (int, optional):
                Seed to use for the PRNG. Specifying a particular seed with a constant
                set of parameters produces identical results. If not provided, a random seed
                is chosen.

            initial_states (:class:`dimod.SampleSet` or tuple(numpy.ndarray, dict), optional):
                One or more samples, each defining an initial state for all the
                problem variables. Initial states are given one per read, but
                if fewer than `num_reads` initial states are defined, additional
                values are generated as specified by `initial_states_generator`.

                Initial states are provided either as:

                * :class:`dimod.SampleSet`, or

                * [deprecated] tuple, where the first value is a numpy array of
                  initial states to seed the simulated annealing runs, and the
                  second is a dict defining a linear variable labelling.
                  In tuple format, initial states provided are assumed to use
                  the same vartype the BQM is using.

            initial_states_generator (str, 'none'/'tile'/'random', optional, default='random'):
                Defines the expansion of `initial_states` if fewer than
                `num_reads` are specified:

                * "none":
                    If the number of initial states specified is smaller than
                    `num_reads`, raises ValueError.

                * "tile":
                    Reuses the specified initial states if fewer than `num_reads`
                    or truncates if greater.

                * "random":
                    Expands the specified initial states with randomly generated
                    states if fewer than `num_reads` or truncates if greater.

            interrupt_function (function, optional):
                If provided, interrupt_function is called with no parameters
                between each sample of simulated annealing. If the function
                returns True, then simulated annealing will terminate and return
                with all of the samples and energies found so far.

        Returns:
            :obj:`dimod.Response`: A `dimod` :obj:`~dimod.Response` object.

        Examples:
            This example runs simulated annealing on a binary quadratic model with some
            different input parameters.

            >>> import dimod
            >>> import neal
            ...
            >>> sampler = neal.SimulatedAnnealingSampler()
            >>> bqm = dimod.BinaryQuadraticModel({'a': .5, 'b': -.5}, {('a', 'b'): -1}, 0.0, dimod.SPIN)
            >>> # Run with default parameters
            >>> response = sampler.sample(bqm)
            >>> # Run with specified parameters
            >>> response = sampler.sample(bqm, seed=1234, beta_range=[0.1, 4.2],
            ...                                num_reads=1, num_sweeps=20,
            ...                                beta_schedule_type='geometric')
            >>> # Reuse a seed
            >>> a1 = next((sampler.sample(bqm, seed=88)).samples())['a']
            >>> a2 = next((sampler.sample(bqm, seed=88)).samples())['a']
            >>> a1 == a2
            True

        """

        if 'sweeps' in kwargs:
            warnings.warn("The 'sweeps' parameter is deprecated in "
                          "favor of 'num_sweeps'.", DeprecationWarning)
            num_sweeps = kwargs.get('sweeps', num_sweeps)

        # if already index-labelled, just continue
        if all(v in bqm.linear for v in range(len(bqm))):
            _bqm = bqm
            use_label_map = False
        else:
            try:
                inverse_mapping = dict(enumerate(sorted(bqm.linear)))
            except TypeError:
                # in python3 unlike types cannot be sorted
                inverse_mapping = dict(enumerate(bqm.linear))
            mapping = {v: i for i, v in iteritems(inverse_mapping)}

            _bqm = bqm.relabel_variables(mapping, inplace=False)
            use_label_map = True

        # beta_range, num_sweeps are handled by simulated_annealing

        if not (seed is None or isinstance(seed, Integral)):
            raise TypeError("'seed' should be None or a positive integer")
        if isinstance(seed, Integral) and not (0 < seed < (2**64 - 1)):
            error_msg = "'seed' should be an integer between 0 and 2^64 - 1"
            raise ValueError(error_msg)

        if seed is None:
            # pick a random seed
            seed = randint(0, (1 << 64 - 1))

        if interrupt_function and not callable(interrupt_function):
            raise TypeError("'interrupt_function' should be a callable")

        num_variables = len(_bqm)

        # get the Ising linear biases
        linear = _bqm.spin.linear
        h = [linear[v] for v in range(num_variables)]

        quadratic = _bqm.spin.quadratic
        if len(quadratic) > 0:
            couplers, coupler_weights = zip(*iteritems(quadratic))
            couplers = map(lambda c: (c[0], c[1]), couplers)
            coupler_starts, coupler_ends = zip(*couplers)
        else:
            coupler_starts, coupler_ends, coupler_weights = [], [], []

        if beta_range is None:
            beta_range = _default_ising_beta_range(linear, quadratic)

        num_sweeps_per_beta = max(1, num_sweeps // 1000.0)
        num_betas = int(math.ceil(num_sweeps / num_sweeps_per_beta))
        if beta_schedule_type == "linear":
            # interpolate a linear beta schedule
            beta_schedule = np.linspace(*beta_range, num=num_betas)
        elif beta_schedule_type == "geometric":
            # interpolate a geometric beta schedule
            beta_schedule = np.geomspace(*beta_range, num=num_betas)
        else:
            raise ValueError("Beta schedule type {} not implemented".format(beta_schedule_type))

        _generators = {
            'none': self._none_generator,
            'tile': self._tile_generator,
            'random': self._random_generator
        }

        # unpack initial_states from sampleset/samples_like to numpy array, label map and vartype
        if isinstance(initial_states, dimod.SampleSet):
            initial_states_array = initial_states.record.sample
            init_label_map = dict(map(reversed, enumerate(initial_states.variables)))
            init_vartype = initial_states.vartype
        else:
            if initial_states is None:
                initial_states = (np.empty((0, num_variables)), None)
            else:
                warnings.warn("tuple format for 'initial_states' is deprecated "
                            "in favor of 'dimod.SampleSet'.", DeprecationWarning)

            initial_states_array, init_label_map = initial_states

            # assume initial states samples have bqm's vartype
            init_vartype = bqm.vartype

        if initial_states_array.size:
            if init_label_map and set(init_label_map) ^ bqm.variables:
                raise ValueError("mismatch between variables in 'initial_states' and 'bqm'")
            elif initial_states_array.shape[1] != num_variables:
                raise ValueError("mismatch in number of variables in 'initial_states' and 'bqm'")

        if initial_states_generator not in _generators:
            raise ValueError("unknown value for 'initial_states_generator'")

        # reorder initial states array according to label map
        if init_label_map is not None:
            identity = lambda i: i
            get_label = inverse_mapping.get if use_label_map else identity
            ordered_labels = [init_label_map[get_label(i)] for i in range(num_variables)]
            initial_states_array = initial_states_array[:, ordered_labels]

        numpy_initial_states = np.ascontiguousarray(initial_states_array, dtype=np.int8)

        # convert to ising, if provided in binary
        if init_vartype == dimod.BINARY:
            numpy_initial_states = 2 * numpy_initial_states - 1
        elif init_vartype != dimod.SPIN:
            raise TypeError("unsupported vartype")

        # validate num_reads and/or infer them from initial_states
        if num_reads is None:
            num_reads = len(numpy_initial_states) or 1
        if not isinstance(num_reads, Integral):
            raise TypeError("'samples' should be a positive integer")
        if num_reads < 1:
            raise ValueError("'samples' should be a positive integer")

        # extrapolate and/or truncate initial states, if necessary
        extrapolate = _generators[initial_states_generator]
        numpy_initial_states = extrapolate(numpy_initial_states, num_reads, num_variables, seed)
        numpy_initial_states = self._truncate_filter(numpy_initial_states, num_reads)

        # run the simulated annealing algorithm
        samples, energies = sa.simulated_annealing(
            num_reads, h, coupler_starts, coupler_ends, coupler_weights,
            num_sweeps_per_beta, beta_schedule,
            seed, numpy_initial_states, interrupt_function)

        off = _bqm.spin.offset
        info = {
            "beta_range": beta_range,
            "beta_schedule_type": beta_schedule_type
        }
        response = dimod.SampleSet.from_samples(
            samples,
            energy=energies+off,
            info=info,
            vartype=dimod.SPIN
        )

        response.change_vartype(_bqm.vartype, inplace=True)
        if use_label_map:
            response.relabel_variables(inverse_mapping, inplace=True)

        return response

    @staticmethod
    def _none_generator(initial_states, num_reads, *args, **kwargs):
        if len(initial_states) < num_reads:
            raise ValueError("insufficient number of initial states given")
        return initial_states

    @staticmethod
    def _tile_generator(initial_states, num_reads, *args, **kwargs):
        if len(initial_states) < 1:
            raise ValueError("cannot tile an empty sample set of initial states")

        if len(initial_states) >= num_reads:
            return initial_states

        reps, rem = divmod(num_reads, len(initial_states))

        initial_states = np.tile(initial_states, (reps, 1))
        initial_states = np.vstack((initial_states, initial_states[:rem]))

        return initial_states

    @staticmethod
    def _random_generator(initial_states, num_reads, num_variables, seed):
        rem = max(0, num_reads - len(initial_states))

        np_rand = np.random.RandomState(seed % 2**32)
        random_states = 2 * np_rand.randint(2, size=(rem, num_variables)).astype(np.int8) - 1

        # handle zero-length array of input states
        if len(initial_states):
            initial_states = np.vstack((initial_states, random_states))
        else:
            initial_states = random_states

        return initial_states

    @staticmethod
    def _truncate_filter(initial_states, num_reads):
        if len(initial_states) > num_reads:
            initial_states = initial_states[:num_reads]
        return initial_states


Neal = SimulatedAnnealingSampler


def _default_ising_beta_range(h, J):
    """Determine the starting and ending beta from h J

    Args:
        h (dict)

        J (dict)

    Assume each variable in J is also in h.

    We use the minimum bias to give a lower bound on the minimum energy gap, such at the
    final sweeps we are highly likely to settle into the current valley.
    """
    # Get nonzero, absolute biases
    abs_h = [abs(hh) for hh in h.values() if hh != 0]
    abs_J = [abs(jj) for jj in J.values() if jj != 0]
    abs_biases = abs_h + abs_J

    if not abs_biases:
        return [0.1, 1.0]

    # Rough approximation of min change in energy when flipping a qubit
    min_delta_energy = min(abs_biases)

    # Combine absolute biases by variable
    abs_bias_dict = defaultdict(int, {k: abs(v) for k, v in h.items()})
    for (k1, k2), v in J.items():
        abs_bias_dict[k1] += abs(v)
        abs_bias_dict[k2] += abs(v)

    # Find max change in energy when flipping a single qubit
    max_delta_energy = max(abs_bias_dict.values())

    # Selecting betas based on probability of flipping a qubit
    # Hot temp: We want to scale hot_beta so that for the most unlikely qubit flip, we get at least
    # 50% chance of flipping.(This means all other qubits will have > 50% chance of flipping
    # initially.) Most unlikely flip is when we go from a very low energy state to a high energy
    # state, thus we calculate hot_beta based on max_delta_energy.
    #   0.50 = exp(-hot_beta * max_delta_energy)
    #
    # Cold temp: Towards the end of the annealing schedule, we want to minimize the chance of
    # flipping. Don't want to be stuck between small energy tweaks. Hence, set cold_beta so that
    # at minimum energy change, the chance of flipping is set to 1%.
    #   0.01 = exp(-cold_beta * min_delta_energy)
    hot_beta = np.log(2) / max_delta_energy
    cold_beta = np.log(100) / min_delta_energy

    return [hot_beta, cold_beta]


def default_beta_range(bqm):
    ising = bqm.spin
    return _default_ising_beta_range(ising.linear, ising.quadratic)