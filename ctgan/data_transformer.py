"""Data transformer module for CTGAN."""

from collections import namedtuple

import numpy as np
import pandas as pd
from sklearn.mixture import BayesianGaussianMixture

SpanInfo = namedtuple('SpanInfo', ['dim', 'activation_fn'])
ColumnTransformInfo = namedtuple(
    'ColumnTransformInfo', [
        'column_name', 'column_type', 'transform', 'output_info', 'output_dimensions'
    ]
)


class DataTransformer(object):
    """Data Transformer.

    Model continuous and discrete columns with a BayesianGMM and a OneHotEncoder
    respectively.

    Args:
        n_clusters (int):
            Number of modes.
        epsilon (float):
            Epsilon value for categorical columns.
    """

    def __init__(self, n_clusters=10, epsilon=0.005):
        self.n_clusters = n_clusters
        self.epsilon = epsilon
        self.output_info_list = []
        self.output_dimensions = 0
        self.dataframe = False
        self._column_raw_dtypes = None
        self._column_transform_info_list = []

    def _fit_continuous(self, column_name, data):
        """Fit a single continuous column.

        Args:
            column_name (str):
                Name of the column.
            data (pandas.Series):
                Data to fit.

        Returns:
            ColumnTransformInfo:
                Information about the transform.
        """
        gm = BayesianGaussianMixture(
            n_components=self.n_clusters,
            weight_concentration_prior_type='dirichlet_process',
            weight_concentration_prior=0.001,
            n_init=1,
            random_state=0
        )

        gm.fit(data.reshape(-1, 1))
        components = gm.weights_ > self.epsilon
        num_components = components.sum()

        if num_components == 0:
            return self._fit_gaussian(column_name, data)

        means = gm.means_.reshape((1, self.n_clusters))
        stds = np.sqrt(gm.covariances_).reshape((1, self.n_clusters))
        means = means[:, components]
        stds = stds[:, components]

        if len(means) == 0:
            return self._fit_gaussian(column_name, data)

        def transform(col_data):
            means_vector = means.repeat(len(col_data), axis=0)
            stds_vector = stds.repeat(len(col_data), axis=0)
            normalized_values = ((col_data - means_vector) / (4 * stds_vector))
            component_probs = gm.predict_proba(col_data.reshape(-1, 1))
            component_probs = component_probs[:, components]

            selected_component = np.zeros(len(component_probs), dtype='int')
            for i in range(len(component_probs)):
                component_prob_t = component_probs[i] + 1e-6
                component_prob_t = component_prob_t / component_prob_t.sum()
                selected_component[i] = np.random.choice(
                    np.arange(num_components), p=component_prob_t)

            aranged = np.arange(len(selected_component))
            mean = means[0, selected_component]
            std = stds[0, selected_component]
            normalized = normalized_values[aranged, selected_component]

            out = np.zeros((len(col_data), num_components * 2))
            out[aranged, selected_component] = normalized
            out[aranged, num_components + selected_component] = 1

            return out

        output_info = [
            SpanInfo(num_components, 'tanh'),
            SpanInfo(num_components, 'softmax')
        ]
        output_dimensions = sum(info.dim for info in output_info)
        return ColumnTransformInfo(
            column_name=column_name, column_type='continuous', transform=transform,
            output_info=output_info, output_dimensions=output_dimensions)

    def _fit_gaussian(self, column_name, data):
        """Fit a single continuous column with a Gaussian distribution.

        Args:
            column_name (str):
                Name of the column.
            data (pandas.Series):
                Data to fit.

        Returns:
            ColumnTransformInfo:
                Information about the transform.
        """
        mean = data.mean()
        std = data.std()

        def transform(col_data):
            normalized = (col_data - mean) / (4 * std)
            return np.array(normalized.reshape(-1, 1))

        output_info = [SpanInfo(1, 'tanh')]
        output_dimensions = sum(info.dim for info in output_info)
        return ColumnTransformInfo(
            column_name=column_name, column_type='continuous', transform=transform,
            output_info=output_info, output_dimensions=output_dimensions)

    def _fit_discrete(self, column_name, data):
        """Fit a single discrete column.

        Args:
            column_name (str):
                Name of the column.
            data (pandas.Series):
                Data to fit.

        Returns:
            ColumnTransformInfo:
                Information about the transform.
        """
        data = data.fillna(0)
        ohe = np.zeros((len(data), int(max(data)) + 1))
        ohe[np.arange(len(data)), data.astype('int')] = 1

        def transform(col_data):
            return ohe[col_data.astype('int')]

        output_info = [SpanInfo(ohe.shape[1], 'softmax')]
        output_dimensions = sum(info.dim for info in output_info)
        return ColumnTransformInfo(
            column_name=column_name, column_type='discrete', transform=transform,
            output_info=output_info, output_dimensions=output_dimensions)

    def fit(self, raw_data, discrete_columns=()):
        """Fit the transformer to the data.

        Args:
            raw_data (pandas.DataFrame or numpy.ndarray):
                Data to fit.
            discrete_columns (list-like):
                List of discrete columns to transform.
        """
        self.output_info_list = []
        self.output_dimensions = 0
        self._column_raw_dtypes = {}

        if isinstance(raw_data, pd.DataFrame):
            self.dataframe = True
            for column_name in raw_data.columns:
                if column_name in discrete_columns:
                    column_transform_info = self._fit_discrete(
                        column_name, raw_data[column_name].values)
                else:
                    column_transform_info = self._fit_continuous(
                        column_name, raw_data[column_name].values)

                self.output_info_list.append(column_transform_info.output_info)
                self.output_dimensions += column_transform_info.output_dimensions
                self._column_raw_dtypes[column_name] = raw_data[column_name].dtype
                self._column_transform_info_list.append(column_transform_info)
        else:
            raise ValueError("Only pandas.DataFrame is supported for raw_data")

        return self

    def transform(self, raw_data):
        """Take raw data and output a matrix data."""
        if not isinstance(raw_data, pd.DataFrame):
            raise ValueError("Only pandas.DataFrame is supported for raw_data")

        data = []
        for column_transform_info in self._column_transform_info_list:
            column_name = column_transform_info.column_name
            data.append(column_transform_info.transform(raw_data[column_name].values))

        return np.concatenate(data, axis=1).astype(float)

    def inverse_transform(self, data):
        """Convert the matrix back to raw data format.

        Args:
            data (numpy.ndarray):
                Data in matrix format.

        Returns:
            pandas.DataFrame:
                Converted data.
        """
        if not self.dataframe:
            raise ValueError("Only pandas.DataFrame is supported for raw_data")

        st = 0
        recovered_data = {}
        column_names = []
        for column_transform_info in self._column_transform_info_list:
            column_name = column_transform_info.column_name
            dim = column_transform_info.output_dimensions
            ed = st + dim

            if column_transform_info.column_type == 'continuous':
                data_t = np.zeros((len(data), 1))
                for span_info in column_transform_info.output_info:
                    if span_info.activation_fn == 'tanh':
                        span_dim = span_info.dim
                        data_t = data[:, st:st + span_dim]
                    st += span_info.dim
                recovered_data[column_name] = data_t
            else:
                recovered_data[column_name] = np.argmax(
                    data[:, st:ed], axis=1).astype(self._column_raw_dtypes[column_name])
                st = ed

            column_names.append(column_name)

        recovered_data = pd.DataFrame(recovered_data, columns=column_names)
        recovered_data = recovered_data[list(self._column_raw_dtypes.keys())]
        return recovered_data

    def convert_column_name_value_to_id(self, column_name, value):
        """Get the ids of the given `column_name`-`value` pair.

        Args:
            column_name (str):
                Column name to get the ids.
            value:
                Value to get the ids.

        Returns:
            dict:
                Mapping of the given `column_name`-`value` pair to integer id.
        """
        discrete_counter = 0
        column_id = 0
        for column_transform_info in self._column_transform_info_list:
            if column_transform_info.column_name == column_name:
                break
            if column_transform_info.column_type == 'discrete':
                discrete_counter += 1
            column_id += 1

        if column_transform_info.column_type == 'continuous':
            raise ValueError(f"Column {column_name} is not a discrete column.")

        value_id = np.argmax(column_transform_info.transform(np.array([value])))[0]
        return {
            'discrete_column_id': discrete_counter,
            'value_id': value_id
        }
