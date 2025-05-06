"""Base synthesizer module.

This module defines the BaseSynthesizer class and the random_state decorator
that are used as base implementations for all the synthesizers.
"""

import contextlib
import numpy as np
import torch
from functools import wraps


@contextlib.contextmanager
def set_random_states(random_state, set_model_random_state):
    """Context manager for managing the random state.

    Args:
        random_state (int or tuple):
            The random seed or a tuple of (numpy.random.RandomState, torch.Generator).
        set_model_random_state (function):
            Function to set the random state on the model.
    """
    original_np_state = np.random.get_state()
    original_torch_state = torch.get_rng_state()

    random_np_state, random_torch_state = random_state

    np.random.set_state(random_np_state.get_state())
    torch.set_rng_state(random_torch_state.get_state())

    try:
        yield
    finally:
        current_np_state = np.random.RandomState()
        current_np_state.set_state(np.random.get_state())
        current_torch_state = torch.Generator()
        current_torch_state.set_state(torch.get_rng_state())
        set_model_random_state((current_np_state, current_torch_state))

        np.random.set_state(original_np_state)
        torch.set_rng_state(original_torch_state)


def random_state(function):
    """Decorator for methods that require setting the random state.

    This decorator ensures that the random state is properly set for methods that use
    random number generation, allowing for reproducible results.
    """
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, 'random_states'):
            random_state = kwargs.get('random_state')
            if random_state is None:
                random_state = 0

            if callable(random_state):
                random_state = random_state()

            old_states = {}
            for state_name in self.random_states:
                old_states[state_name] = getattr(np.random, 'get_{}'.format(state_name))()
                getattr(np.random, 'set_{}'.format(state_name))(
                    random_state + self.random_states[state_name]
                )

            result = function(self, *args, **kwargs)

            for state_name in self.random_states:
                getattr(np.random, 'set_{}'.format(state_name))(old_states[state_name])

            return result

        return function(self, *args, **kwargs)

    return wrapper


class BaseSynthesizer:
    """Base class for all synthesizers.

    This class defines the common API that all synthesizers expose.
    """

    random_states = {
        'seed': 0
    }

    def __getstate__(self):
        """Improve pickling state for ``BaseSynthesizer``.

        Convert to ``cpu`` device before starting the pickling process in order to be able to
        load the model even when used from an external tool such as ``SDV``. Also, if
        ``random_states`` are set, store their states as dictionaries rather than generators.

        Returns:
            dict:
                Python dict representing the object.
        """
        device_backup = self._device
        self.set_device(torch.device('cpu'))
        state = self.__dict__.copy()
        self.set_device(device_backup)
        if (
            isinstance(self.random_states, tuple) and
            isinstance(self.random_states[0], np.random.RandomState) and
            isinstance(self.random_states[1], torch.Generator)
        ):
            state['_numpy_random_state'] = self.random_states[0].get_state()
            state['_torch_random_state'] = self.random_states[1].get_state()
            state.pop('random_states')

        return state

    def __setstate__(self, state):
        """Restore the state of a ``BaseSynthesizer``.

        Restore the ``random_states`` from the state dict if those are present and then
        set the device according to the current hardware.
        """
        if '_numpy_random_state' in state and '_torch_random_state' in state:
            np_state = state.pop('_numpy_random_state')
            torch_state = state.pop('_torch_random_state')

            current_torch_state = torch.Generator()
            current_torch_state.set_state(torch_state)

            current_numpy_state = np.random.RandomState()
            current_numpy_state.set_state(np_state)
            state['random_states'] = (
                current_numpy_state,
                current_torch_state
            )

        self.__dict__ = state
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.set_device(device)

    def save(self, path):
        """Save the model in the passed `path`."""
        device_backup = self._device
        self.set_device(torch.device('cpu'))
        torch.save(self, path)
        self.set_device(device_backup)

    @classmethod
    def load(cls, path):
        """Load the model stored in the passed `path`."""
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        model = torch.load(path)
        model.set_device(device)
        return model

    def set_random_state(self, random_state):
        """Set the random state.

        Args:
            random_state (int, tuple, or None):
                Either a tuple containing the (numpy.random.RandomState, torch.Generator)
                or an int representing the random seed to use for both random states.
        """
        if random_state is None:
            self.random_states = random_state
        elif isinstance(random_state, int):
            self.random_states = (
                np.random.RandomState(seed=random_state),
                torch.Generator().manual_seed(random_state),
            )
        elif (
            isinstance(random_state, tuple) and
            isinstance(random_state[0], np.random.RandomState) and
            isinstance(random_state[1], torch.Generator)
        ):
            self.random_states = random_state
        else:
            raise TypeError(
                f'`random_state` {random_state} expected to be an int or a tuple of '
                '(`np.random.RandomState`, `torch.Generator`)')

    def fit(self, data, discrete_columns=()):
        """Fit the synthesizer model to the provided data.

        Args:
            data (pandas.DataFrame or numpy.ndarray):
                Data to fit the synthesizer to.
            discrete_columns (list-like):
                List of discrete columns to be used as discrete features.
        """
        raise NotImplementedError("The 'fit' method must be implemented by subclasses.")

    def sample(self, n_samples):
        """Sample synthetic data from the synthesizer.

        Args:
            n_samples (int):
                Number of samples to generate.

        Returns:
            pandas.DataFrame:
                Synthetic data generated.
        """
        raise NotImplementedError("The 'sample' method must be implemented by subclasses.")
