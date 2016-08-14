"""pyomoio: read data from Pyomo models to pandas DataFrames

Pyomo is a AMPL-like model description language for mathematical
optimization problems. This module provides functions to read data from 
Pyomo model instances and result objects. Use list_entities to get a list
of all entities (sets, params, variables, objectives or constraints) inside a 
pyomo instance, before get its contents by get_entity (or get_entities).
    
"""
import pyomo.core as pyomo
import pandas as pd

def get_entity(instance, name):
    """Return a Series for an entity in model instance.
    
    Parameters
    ----------
    instance : pyomo.ConcreteModel
        The model object from which to retrieve the entity.
    name : str
        Name of a Set, Param, Var, Constraint or Objective in `instance`.
    
    Returns
    -------
    pandas.Series
        Series of values (or 1's, in case of a Set) for entity `name`.
    """

    # retrieve entity, its type and its onset names
    entity = instance.__getattribute__(name)
    labels = _get_onset_names(entity)

    # extract values
    if isinstance(entity, pyomo.Set):
        # Pyomo sets don't have values, only elements
        results = pd.DataFrame([(v, 1) for v in entity.value])

        # for unconstrained sets, the column label is identical to their index
        # hence, make index equal to entity name and append underscore to name
        # (=the later column title) to preserve identical index names for both
        # unconstrained supersets
        if not labels:
            labels = [name]
            name = name + '_'

    elif isinstance(entity, pyomo.Param):
        if entity.dim() > 1:
            results = pd.DataFrame([v[0] + (v[1],) for v in entity.items()])
        else:
            results = pd.DataFrame(entity.items())
    else:
        # create DataFrame
        if entity.dim() > 1:
            # concatenate index tuples with value if entity has
            # multidimensional indices v[0]
            results = pd.DataFrame(
                [v[0] + (v[1].value,) for v in entity.items()])
        else:
            # otherwise, create tuple from scalar index v[0]
            results = pd.DataFrame(
                [(v[0], v[1].value) for v in entity.items()])

    # check for duplicate onset names and append one to several "_" to make
    # them unique, e.g. ['sit', 'sit', 'com'] becomes ['sit', 'sit_', 'com']
    for k, label in enumerate(labels):
        if label in labels[:k]:
            labels[k] = labels[k] + "_"

    if not results.empty:
        # name columns according to labels + entity name
        results.columns = labels + [name]
        results.set_index(labels, inplace=True)
        
        # convert to Series
        results = results[name]

    return results


def get_entities(instance, names):
    """Return one DataFrame with entities in columns and a common index.
    
    Works only on entities that share a common domain (set or set_tuple), which
    is used as index of the returned DataFrame.
    
    Parameters
    ----------
    instance : pyomo.ConcreteModel
        The model object from which to retrieve the entity.

    names : list of str 
        A list of entity names (as returned by function `list_entities`).
    
    Returns
    -------
    pandas.DataFrame
        A DataFrame with entities as columns and the union of their domains as 
        a row index.
    """

    df = pd.DataFrame()
    for name in names:
        other = get_entity(instance, name)

        if df.empty:
            df = other.to_frame()
        else:
            index_names_before = df.index.names

            df = df.join(other, how='outer')

            if index_names_before != df.index.names:
                df.index.names = index_names_before

    return df


def list_entities(instance, entity_type):
    """Return list of sets, params, variables, constraints or objectives.
    
    Parameters
    ----------
    instance : pyomo.ConcreteModel
        The model object from which to list the entities.
        
    entity_type : {"set", "par", "var", "con", "obj"}
        Type of entity to be listed.
    
    Returns
    -------
    pandas.DataFrame
        DataFrame of entities with name, domain and description (if specified).

    Example
    -------
    >>> data = read_excel('mimo-example.xlsx')
    >>> model = create_model(data, range(1,25))
    >>> list_entities(model, 'obj')  #doctest: +NORMALIZE_WHITESPACE
                                     Description Domain
    Name
    obj   minimize(cost = sum of all cost types)     []
    """

    # helper function to discern entities by type
    def filter_by_type(entity, entity_type):
        if entity_type == 'set':
            return isinstance(entity, pyomo.Set) and not entity.virtual
        elif entity_type == 'par':
            return isinstance(entity, pyomo.Param)
        elif entity_type == 'var':
            return isinstance(entity, pyomo.Var)
        elif entity_type == 'con':
            return isinstance(entity, pyomo.Constraint)
        elif entity_type == 'obj':
            return isinstance(entity, pyomo.Objective)
        else:
            raise ValueError("Unknown entity_type '{}'".format(entity_type))

    # iterate through all model components and keep only
    iter_entities = instance.__dict__.items()
    entities = sorted(
        (name, entity.doc, _get_onset_names(entity))
        for (name, entity) in iter_entities
        if filter_by_type(entity, entity_type))

    # if something was found, wrap tuples in DataFrame, otherwise return empty
    if entities:
        entities = pd.DataFrame(entities,
                                columns=['Name', 'Description', 'Domain'])
        entities.set_index('Name', inplace=True)
    else:
        entities = pd.DataFrame()
    return entities


def _get_onset_names(entity):
    """Return a list of domain set names for a given model entity
    
    Parameters
    ----------
    entity: Set, Param, Var, Objective, Constraint 
        A member entity of a pyomo.ConcreteModel object.

    Returns
    -------
    list of str
        A list of domain set names for `entity`
        
    Example
    -------
    >>> data = read_excel('mimo-example.xlsx')
    >>> model = create_model(data, range(1,25))
    >>> _get_onset_names(model.e_co_stock)
    ['t', 'sit', 'com', 'com_type']
    """
    # get column titles for entities from domain set names
    labels = []

    if isinstance(entity, pyomo.Set):
        if entity.dimen > 1:
            # N-dimensional set tuples, possibly with nested set tuples within
            if entity.domain:
                domains = entity.domain.set_tuple
            else:
                domains = entity.set_tuple

            for domain_set in domains:
                labels.extend(_get_onset_names(domain_set))

        elif entity.dimen == 1:
            if entity.domain:
                # 1D subset; add domain name
                labels.append(entity.domain.name)
            else:
                # unrestricted set; add entity name
                labels.append(entity.name)
        else:
            # no domain, so no labels needed
            pass

    elif isinstance(entity, (pyomo.Param, pyomo.Var, pyomo.Constraint,
                             pyomo.Objective)):
        if entity.dim() > 0 and entity._index:
            labels = _get_onset_names(entity._index)
        else:
            # zero dimensions, so no onset labels
            pass

    else:
        raise ValueError("Unknown entity type!")

    return labels
    
