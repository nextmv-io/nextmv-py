"""
Application mixin for handling app managed inputs.
"""

from typing import TYPE_CHECKING, Any

from nextmv.cloud.input_set import ManagedInput
from nextmv.input import InputFormat
from nextmv.output import OutputFormat
from nextmv.run import Format, FormatInput, FormatOutput
from nextmv.safe import safe_id

if TYPE_CHECKING:
    from . import Application


class ApplicationManagedInputMixin:
    """
    Mixin class for handling app managed inputs within an application.
    """

    def delete_managed_input(self: "Application", managed_input_id: str) -> None:
        """
        Delete a managed input.

        Permanently removes the specified managed input from the application.

        Parameters
        ----------
        managed_input_id : str
            ID of the managed input to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_managed_input("inp_123456789")  # Permanently deletes the managed input
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.endpoint}/inputs/{managed_input_id}",
        )

    def list_managed_inputs(self: "Application") -> list[ManagedInput]:
        """
        List all managed inputs.

        Returns
        -------
        list[ManagedInput]
            List of managed inputs.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/inputs",
        )

        return [ManagedInput.from_dict(managed_input) for managed_input in response.json()]

    def managed_input(self: "Application", managed_input_id: str) -> ManagedInput:
        """
        Get a managed input.

        Parameters
        ----------
        managed_input_id: str
            ID of the managed input.

        Returns
        -------
        ManagedInput
            The managed input.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/inputs/{managed_input_id}",
        )

        return ManagedInput.from_dict(response.json())

    def new_managed_input(
        self: "Application",
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        upload_id: str | None = None,
        run_id: str | None = None,
        format: Format | dict[str, Any] | None = None,
    ) -> ManagedInput:
        """
        Create a new managed input. There are two methods for creating a
        managed input:

        1. Specifying the `upload_id` parameter. You may use the `upload_url`
           method to obtain the upload ID and the `upload_data` method
           to upload the data to it.
        2. Specifying the `run_id` parameter. The managed input will be
           created from the run specified by the `run_id` parameter.

        Either the `upload_id` or the `run_id` parameter must be specified.

        Parameters
        ----------
        id: Optional[str], default=None
            ID of the managed input. Will be generated if not provided.
        name: Optional[str], default=None
            Name of the managed input. Will be generated if not provided.
        description: Optional[str], default=None
            Optional description of the managed input.
        upload_id: Optional[str], default=None
            ID of the upload to use for the managed input.
        run_id: Optional[str], default=None
            ID of the run to use for the managed input.
        format: Optional[Format], default=None
            Format of the managed input. Default will be formatted as `JSON`.

        Returns
        -------
        ManagedInput
            The new managed input.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If neither the `upload_id` nor the `run_id` parameter is
            specified.
        """

        if upload_id is None and run_id is None:
            raise ValueError("Either upload_id or run_id must be specified")

        if id is None or id == "":
            id = safe_id(prefix="managed-input")
        if name is None or name == "":
            name = id

        payload = {
            "id": id,
            "name": name,
        }

        if description is not None:
            payload["description"] = description
        if upload_id is not None:
            payload["upload_id"] = upload_id
        if run_id is not None:
            payload["run_id"] = run_id

        if format is not None:
            payload["format"] = format.to_dict() if isinstance(format, Format) else format
        else:
            payload["format"] = Format(
                format_input=FormatInput(input_type=InputFormat.JSON),
                format_output=FormatOutput(output_type=OutputFormat.JSON),
            ).to_dict()

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/inputs",
            payload=payload,
        )

        return ManagedInput.from_dict(response.json())

    def update_managed_input(
        self: "Application",
        managed_input_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> ManagedInput:
        """
        Update a managed input.

        Parameters
        ----------
        managed_input_id : str
            ID of the managed input to update.
        name : Optional[str], default=None
            Optional new name for the managed input.
        description : Optional[str], default=None
            Optional new description for the managed input.

        Returns
        -------
        ManagedInput
            The updated managed input.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        managed_input = self.managed_input(managed_input_id)
        managed_input_dict = managed_input.to_dict()
        payload = managed_input_dict.copy()

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/inputs/{managed_input_id}",
            payload=payload,
        )

        return ManagedInput.from_dict(response.json())
