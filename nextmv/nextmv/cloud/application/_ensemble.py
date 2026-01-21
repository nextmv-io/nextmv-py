"""
Application mixin for managing app ensembles.
"""

from typing import TYPE_CHECKING

from nextmv.cloud.ensemble import EnsembleDefinition, EvaluationRule, RunGroup
from nextmv.deprecated import deprecated
from nextmv.safe import safe_id

if TYPE_CHECKING:
    from . import Application


class ApplicationEnsembleMixin:
    """
    Mixin class for managing app ensembles within an application.
    """

    def delete_ensemble_definition(self: "Application", ensemble_definition_id: str) -> None:
        """
        Delete an ensemble definition.

        Parameters
        ----------
        ensemble_definition_id : str
            ID of the ensemble definition to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_ensemble_definition("development-ensemble-definition")
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.ensembles_endpoint}/{ensemble_definition_id}",
        )

    def ensemble_definition(self: "Application", ensemble_definition_id: str) -> EnsembleDefinition:
        """
        Get an ensemble definition.

        Parameters
        ----------
        ensemble_definition_id : str
            ID of the ensemble definition to retrieve.

        Returns
        -------
        EnsembleDefintion
            The requested ensemble definition details.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> ensemble_definition = app.ensemble_definition("instance-123")
        >>> print(ensemble_definition.name)
        'Production Ensemble Definition'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.ensembles_endpoint}/{ensemble_definition_id}",
        )

        return EnsembleDefinition.from_dict(response.json())

    def list_ensemble_definitions(self: "Application") -> list[EnsembleDefinition]:
        """
        List all ensemble_definitions.

        Returns
        -------
        list[EnsembleDefinition]
            List of all ensemble definitions associated with this application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> ensemble_definitions = app.list_ensemble_definitions()
        >>> for ensemble_definition in ensemble_definitions:
        ...     print(ensemble_definition.name)
        'Development Ensemble Definition'
        'Production Ensemble Definition'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.ensembles_endpoint}",
        )

        return [EnsembleDefinition.from_dict(ensemble_definition) for ensemble_definition in response.json()["items"]]

    def new_ensemble_defintion(
        self: "Application",
        id: str,
        run_groups: list[RunGroup],
        rules: list[EvaluationRule],
        name: str | None = None,
        description: str | None = None,
    ) -> EnsembleDefinition:
        """
        !!! warning
            `new_ensemble_defintion` is deprecated, use `new_ensemble_definition` instead.

        Create a new ensemble definition.

        Parameters
        ----------
        id: str
            ID of the ensemble defintion.
        run_groups: list[RunGroup]
            Information to facilitate the execution of child runs.
        rules: list[EvaluationRule]
            Information to facilitate the selection of
            a result for the ensemble run from child runs.
        name: Optional[str]
            Name of the ensemble definition.
        description: Optional[str]
            Description of the ensemble definition.
        """

        deprecated(
            name="new_ensemble_defintion",
            reason="`Application.new_ensemble_defintion` is deprecated, use `new_ensemble_definition` instead",
        )

        return self.new_ensemble_definition(
            run_groups=run_groups,
            rules=rules,
            id=id,
            name=name,
            description=description,
        )

    def new_ensemble_definition(
        self: "Application",
        run_groups: list[RunGroup],
        rules: list[EvaluationRule],
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> EnsembleDefinition:
        """
        Create a new ensemble definition.

        Parameters
        ----------
        run_groups: list[RunGroup]
            Information to facilitate the execution of child runs.
        rules: list[EvaluationRule]
            Information to facilitate the selection of
            a result for the ensemble run from child runs.
        id: str | None, default=None
            ID of the ensemble definition. If not provided, a unique ID will be
            generated with the prefix 'ensemble-'.
        name: Optional[str]
            Name of the ensemble definition. If not provided, the ID will be used.
        description: Optional[str]
            Description of the ensemble definition. If not provided, the name will be used.
        """

        if len(run_groups) == 0:
            raise ValueError("at least one run group must be defined to create an ensemble definition")

        if len(rules) == 0:
            raise ValueError("at least one evaluation rule must be defined to create an ensemble definition")

        if id is None or id == "":
            id = safe_id(prefix="ensemble")
        if name is None or name == "":
            name = id
        if description is None or description == "":
            description = name

        payload = {
            "id": id,
            "run_groups": [run_group.to_dict() for run_group in run_groups],
            "rules": [rule.to_dict() for rule in rules],
            "name": name,
            "description": description,
        }

        response = self.client.request(
            method="POST",
            endpoint=f"{self.ensembles_endpoint}",
            payload=payload,
        )

        return EnsembleDefinition.from_dict(response.json())

    def update_ensemble_definition(
        self: "Application",
        id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> EnsembleDefinition:
        """
        Update an ensemble definition.

        Parameters
        ----------
        id : str
            ID of the ensemble definition to update.
        name : Optional[str], default=None
            Optional name of the ensemble definition.
        description : Optional[str], default=None
            Optional description of the ensemble definition.

        Returns
        -------
        EnsembleDefinition
            The updated ensemble definition.

        Raises
        ------
        ValueError
            If neither name nor description is updated
        requests.HTTPError
            If the response status code is not 2xx.
        """

        payload = {}

        if name is None and description is None:
            raise ValueError("Must define at least one value among name and description to modify")
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="PATCH",
            endpoint=f"{self.ensembles_endpoint}/{id}",
            payload=payload,
        )

        return EnsembleDefinition.from_dict(response.json())
