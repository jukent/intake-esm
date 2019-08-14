import os

from . import aggregate, config
from .bld_collection_utils import _extract_attr_with_regex, _reverse_filename_format
from .collection import Collection, docstrings
from .source import BaseSource


class CMIP5Collection(Collection):

    __doc__ = docstrings.with_indents(
        """ Builds a collection for CMIP5 data holdings.
    %(Collection.parameters)s
    """
    )

    def _get_file_attrs(self, filepath):
        """ Extract attributes of a file using information from CMIP5 DRS.

        Notes
        -----
        Reference:

        - CMIP5 DRS: https://pcmdi.llnl.gov/mips/cmip5/docs/cmip5_data_reference_syntax.pdf?id=27

        """
        keys = list(set(self.columns) - set(['resource', 'resource_type', 'direct_access']))
        fileparts = {key: None for key in keys}

        freq_regex = r'/3hr/|/6hr/|/day/|/fx/|/mon/|/monClim/|/subhr/|/yr/'
        realm_regex = r'aerosol|atmos|land|landIce|ocean|ocnBgchem|seaIce'
        version_regex = r'v\d{4}\d{2}\d{2}|v\d{1}'

        file_basename = os.path.basename(filepath)
        fileparts['file_basename'] = file_basename
        fileparts['file_fullpath'] = filepath

        filename_template = (
            '{variable}_{mip_table}_{model}_{experiment}_{ensemble_member}_{temporal_subset}.nc'
        )
        gridspec_template = '{variable}_{mip_table}_{model}_{experiment}_{ensemble_member}.nc'
        f = _reverse_filename_format(
            file_basename, filename_template=filename_template, gridspec_template=gridspec_template
        )
        fileparts.update(f)

        institutes = config.get('collections.cmip5.institutes')
        products = config.get('collections.cmip5.products')
        institute_regex = r'|'.join(institutes)
        product_regex = r'|'.join(products)
        product = _extract_attr_with_regex(filepath, regex=product_regex)
        frequency = _extract_attr_with_regex(filepath, regex=freq_regex, strip_chars='/')
        realm = _extract_attr_with_regex(filepath, regex=realm_regex)
        version = _extract_attr_with_regex(filepath, regex=version_regex) or 'v0'
        institute = _extract_attr_with_regex(os.path.dirname(filepath), regex=institute_regex)
        fileparts['frequency'] = frequency
        fileparts['modeling_realm'] = realm
        fileparts['version'] = version
        fileparts['activity'] = config.get('collections.cmip5.mip_era')
        fileparts['institute'] = institute
        fileparts['product'] = product

        return fileparts


class CMIP5Source(BaseSource):
    name = 'cmip5'
    partition_access = True

    def _open_dataset(self):
        dataset_fields = ['institute', 'model', 'experiment', 'frequency', 'modeling_realm']
        self._open_dataset_groups(
            dataset_fields=dataset_fields,
            member_column_name='ensemble_member',
            variable_column_name='variable',
            file_fullpath_column_name='file_fullpath',
        )


class CMIP6Collection(Collection):

    __doc__ = docstrings.with_indents(
        """ Builds a collection for CMIP6 data holdings.
    %(Collection.parameters)s
    """
    )

    def _get_file_attrs(self, filepath):
        """ Extract attributes of a file using information from CMI6 DRS.

        Notes
        -----
        References
         1. CMIP6 DRS: http://goo.gl/v1drZl
         2. Controlled Vocabularies (CVs) for use in CMIP6:
            https://github.com/WCRP-CMIP/CMIP6_CVs
        """
        keys = list(set(self.columns) - set(['resource', 'resource_type', 'direct_access']))
        fileparts = {key: None for key in keys}

        file_basename = os.path.basename(filepath)
        fileparts['file_basename'] = file_basename
        fileparts['file_fullpath'] = filepath

        filename_template = '{variable_id}_{table_id}_{source_id}_{experiment_id}_{member_id}_{grid_label}_{time_range}.nc'
        gridspec_template = (
            '{variable_id}_{table_id}_{source_id}_{experiment_id}_{member_id}_{grid_label}.nc'
        )

        f = _reverse_filename_format(
            file_basename, filename_template=filename_template, gridspec_template=gridspec_template
        )
        fileparts.update(f)
        version_regex = r'v\d{4}\d{2}\d{2}|v\d{1}'
        activity_ids = config.get('collections.cmip6.activity_ids').keys()
        activity_id_regex = r'|'.join(activity_ids)

        institution_ids = config.get('collections.cmip6.institution_ids').keys()
        institution_id_regex = r'|'.join(institution_ids)

        version = _extract_attr_with_regex(filepath, regex=version_regex) or 'v0'
        activity_id = _extract_attr_with_regex(filepath, regex=activity_id_regex)
        institution_id = _extract_attr_with_regex(
            os.path.dirname(filepath), regex=institution_id_regex
        )
        fileparts['version'] = version
        fileparts['activity_id'] = activity_id
        fileparts['institution_id'] = institution_id
        fileparts['mip_era'] = config.get('collections.cmip6.mip_era')
        return fileparts


class CMIP6Source(BaseSource):
    name = 'cmip6'
    partition_access = True

    def _open_dataset(self):
        # fields which define a single dataset
        dataset_fields = ['institution_id', 'source_id', 'experiment_id', 'table_id', 'grid_label']
        self._open_dataset_groups(
            dataset_fields=dataset_fields,
            member_column_name='member_id',
            variable_column_name='variable_id',
            file_fullpath_column_name='file_fullpath',
        )
