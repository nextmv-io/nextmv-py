"""
Application module for interacting with Nextmv Cloud applications.

This module provides functionality to interact with applications in Nextmv Cloud,
including application management, running applications, and managing experiments
and inputs.

Classes
-------
ApplicationType
    Enumeration of application types in Nextmv Cloud.
Application
    Class for interacting with applications in Nextmv Cloud.

Functions
---------
list_application
    Function to list applications in Nextmv Cloud.
"""

import json
import shutil
import sys
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import requests
import rich
from pydantic import AliasChoices, Field

from nextmv import deprecated
from nextmv._serialization import deflated_serialize_json
from nextmv.base_model import BaseModel
from nextmv.cloud import package
from nextmv.cloud.application._acceptance import ApplicationAcceptanceMixin
from nextmv.cloud.application._batch_scenario import ApplicationBatchMixin
from nextmv.cloud.application._ensemble import ApplicationEnsembleMixin
from nextmv.cloud.application._input_set import ApplicationInputSetMixin
from nextmv.cloud.application._instance import ApplicationInstanceMixin
from nextmv.cloud.application._managed_input import ApplicationManagedInputMixin
from nextmv.cloud.application._run import ApplicationRunMixin
from nextmv.cloud.application._secrets import ApplicationSecretsMixin
from nextmv.cloud.application._shadow import ApplicationShadowMixin
from nextmv.cloud.application._switchback import ApplicationSwitchbackMixin
from nextmv.cloud.application._utils import _is_not_exist_error
from nextmv.cloud.application._version import ApplicationVersionMixin
from nextmv.cloud.client import Client
from nextmv.cloud.instance import Instance
from nextmv.cloud.url import UploadURL
from nextmv.cloud.version import Version
from nextmv.logger import log
from nextmv.manifest import Manifest
from nextmv.model import Model, ModelConfiguration
from nextmv.safe import safe_id


class ApplicationType(str, Enum):
    """
    Enumeration of application types in Nextmv Cloud.

    You can import the `ApplicationType` class directly from `cloud`:

    ```python
    from nextmv.cloud import ApplicationType
    ```

    Attributes
    ----------
    CUSTOM : str
        Custom application type, which is the most common. Represents a standard
        application that you can push code to.
    SUBSCRIPTION : str
        Subscription application type. You cannot push code to subscription
        applications, but only subscribe to them through the marketplace.
    PIPELINE : str
        Pipeline application type that refers to workflows.
    """

    CUSTOM = "custom"
    """
    Custom application type, which is the most common. Represents a standard
    application that you can push code to.
    """
    SUBSCRIPTION = "subscription"
    """
    Subscription application type. You cannot push code to subscription
    applications, but only subscribe to them through the marketplace.
    """
    PIPELINE = "pipeline"
    """
    Pipeline application type that refers to workflows.
    """


class Application(
    BaseModel,
    ApplicationAcceptanceMixin,
    ApplicationBatchMixin,
    ApplicationRunMixin,
    ApplicationEnsembleMixin,
    ApplicationInstanceMixin,
    ApplicationSecretsMixin,
    ApplicationVersionMixin,
    ApplicationInputSetMixin,
    ApplicationManagedInputMixin,
    ApplicationShadowMixin,
    ApplicationSwitchbackMixin,
):
    """
    A published decision model that can be executed.

    You can import the `Application` class directly from `cloud`:

    ```python
    from nextmv.cloud import Application
    ```

    This class represents an application in Nextmv Cloud, providing methods to
    interact with the application, run it with different inputs, manage versions,
    instances, experiments, and more.

    Note: It is recommended to use `Application.get()` or `Application.new()`
    instead of direct initialization to ensure proper setup.

    Parameters
    ----------
    client : Client
        Client to use for interacting with the Nextmv Cloud API.
    id : str
        ID of the application.
    name : str, optional
        Name of the application.
    description : str, optional
        Description of the application.
    type : ApplicationType, optional
        Type of the application (CUSTOM, SUBSCRIPTION, or PIPELINE).
    default_instance_id : str, optional
        Default instance ID to use for submitting runs.
    default_experiment_instance : str, optional
        Default experiment instance ID to use for experiments.
    subscription_id : str, optional
        Subscription ID if the application is a subscription type.
    locked : bool, default=False
        Whether the application is locked.
    created_at : datetime, optional
        Creation timestamp of the application.
    updated_at : datetime, optional
        Last update timestamp of the application.
    endpoint : str, default="v1/applications/{id}"
        Base endpoint for the application (SDK-specific).
    experiments_endpoint : str, default="{base}/experiments"
        Base endpoint for experiments (SDK-specific).
    ensembles_endpoint : str, default="{base}/ensembles"
        Base endpoint for ensembles (SDK-specific).

    Examples
    --------
    >>> from nextmv.cloud import Client, Application
    >>> client = Client(api_key="your-api-key")
    >>> # Retrieve an existing application
    >>> app = Application.get(client=client, id="your-app-id")
    >>> print(f"Application name: {app.name}")
    Application name: My Application
    >>> # Create a new application
    >>> new_app = Application.new(client=client, name="My New App", id="my-new-app")
    >>> # List application instances
    >>> instances = app.list_instances()
    """

    # Actual API attributes of an application.
    id: str
    """ID of the application."""
    name: str | None = None
    """Name of the application."""
    description: str | None = None
    """Description of the application."""
    type: ApplicationType | None = None
    """Type of the application."""
    default_instance_id: str | None = Field(
        serialization_alias="default_instance",
        validation_alias=AliasChoices("default_instance", "default_instance_id"),
        default=None,
    )
    """Default instance ID to use for submitting runs."""
    default_experiment_instance: str | None = None
    """Default experiment instance ID to use for experiments."""
    subscription_id: str | None = None
    """Subscription ID if the application is a subscription type."""
    locked: bool = False
    """Whether the application is locked."""
    created_at: datetime | None = None
    """Creation timestamp of the application."""
    updated_at: datetime | None = None
    """Last update timestamp of the application."""

    # SDK-specific attributes for convenience when using methods.
    client: Client = Field(exclude=True)
    """Client to use for interacting with the Nextmv Cloud API."""
    endpoint: str = Field(exclude=True, default="v1/applications/{id}")
    """Base endpoint for the application."""
    experiments_endpoint: str = Field(exclude=True, default="{base}/experiments")
    """Base endpoint for the experiments in the application."""
    ensembles_endpoint: str = Field(exclude=True, default="{base}/ensembles")
    """Base endpoint for managing the ensemble definitions in the
    application"""

    def model_post_init(self, __context) -> None:
        """Initialize the endpoint and experiments_endpoint attributes.

        This method is automatically called after class initialization to
        format the endpoint and experiments_endpoint URLs with the application ID.
        """
        self.endpoint = self.endpoint.format(id=self.id)
        self.experiments_endpoint = self.experiments_endpoint.format(base=self.endpoint)
        self.ensembles_endpoint = self.ensembles_endpoint.format(base=self.endpoint)

    @classmethod
    def get(cls, client: Client, id: str) -> "Application":
        """
        Retrieve an application directly from Nextmv Cloud.

        This function is useful if you want to populate an `Application` class
        by fetching the attributes directly from Nextmv Cloud.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        id : str
            ID of the application to retrieve.

        Returns
        -------
        Application
            The requested application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = client.request(
            method="GET",
            endpoint=f"v1/applications/{id}",
        )

        return cls.from_dict({"client": client} | response.json())

    @classmethod
    def new(
        cls,
        client: Client,
        name: str | None = None,
        id: str | None = None,
        description: str | None = None,
        is_workflow: bool | None = None,
        exist_ok: bool = False,
        default_instance_id: str | None = None,
        default_experiment_instance: str | None = None,
    ) -> "Application":
        """
        Create a new application directly in Nextmv Cloud.

        The application is created as an empty shell, and executable code must
        be pushed to the app before running it remotely.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        name : str | None = None
            Name of the application. Uses the ID as the name if not provided.
        id : str | None = None
            ID of the application. Will be generated if not provided.
        description : str | None = None
            Description of the application.
        is_workflow : bool | None = None
            Whether the application is a Decision Workflow.
        exist_ok : bool, default=False
            If True and an application with the same ID already exists,
            return the existing application instead of creating a new one.
        default_instance_id : str, optional
            Default instance ID to use for submitting runs.
        default_experiment_instance : str, optional
            Default experiment instance ID to use for experiments.

        Returns
        -------
        Application
            The newly created (or existing) application.

        Examples
        --------
        >>> from nextmv.cloud import Client
        >>> client = Client(api_key="your-api-key")
        >>> app = Application.new(client=client, name="My New App", id="my-app")
        """

        if exist_ok and (id is None or id == ""):
            raise ValueError("If exist_ok is True, id must be provided")

        if id is None or id == "":
            id = safe_id("app")

        if exist_ok and cls.exists(client=client, id=id):
            response = client.request(
                method="GET",
                endpoint=f"v1/applications/{id}",
            )

            return cls.from_dict({"client": client} | response.json())

        if name is None or name == "":
            name = id

        payload = {
            "name": name,
            "id": id,
        }

        if description is not None:
            payload["description"] = description

        if is_workflow is not None:
            payload["is_pipeline"] = is_workflow

        if default_instance_id is not None:
            payload["default_instance"] = default_instance_id

        if default_experiment_instance is not None:
            payload["default_experiment_instance"] = default_experiment_instance

        response = client.request(
            method="POST",
            endpoint="v1/applications",
            payload=payload,
        )

        return cls.from_dict({"client": client} | response.json())

    def delete(self) -> None:
        """
        Delete the application.

        Permanently removes the application from Nextmv Cloud.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete()  # Permanently deletes the application
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=self.endpoint,
        )

    @staticmethod
    def exists(client: Client, id: str) -> bool:
        """
        Check if an application exists.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        id : str
            ID of the application to check.

        Returns
        -------
        bool
            True if the application exists, False otherwise.

        Examples
        --------
        >>> from nextmv.cloud import Client
        >>> client = Client(api_key="your-api-key")
        >>> Application.exists(client, "app-123")
        True
        """

        try:
            _ = client.request(
                method="GET",
                endpoint=f"v1/applications/{id}",
            )
            # If the request was successful, the application exists.
            return True
        except requests.HTTPError as e:
            if _is_not_exist_error(e):
                return False
            # Re-throw the exception if it is not the expected 404 error.
            raise e from None

    def push(  # noqa: C901
        self,
        manifest: Manifest | None = None,
        app_dir: str | None = None,
        verbose: bool = False,
        model: Model | None = None,
        model_configuration: ModelConfiguration | None = None,
        rich_print: bool = False,
        auto_create: bool = False,
        version_id: str | None = None,
        version_name: str | None = None,
        version_description: str | None = None,
        instance_id: str | None = None,
        instance_name: str | None = None,
        instance_description: str | None = None,
        update_default_instance: bool = False,
    ) -> None:
        """
        Push an app to Nextmv Cloud.

        If the manifest is not provided, an `app.yaml` file will be searched
        for in the provided path. If there is no manifest file found, an
        exception will be raised.

        There are two ways to push an app to Nextmv Cloud:
        1. Specifying `app_dir`, which is the path to an app's root directory.
        This acts as an external strategy, where the app is composed of files
        in a directory and those apps are packaged and pushed to Nextmv Cloud.
        2. Specifying a `model` and `model_configuration`. This acts as an
        internal (or Python-native) strategy, where the app is actually a
        `nextmv.Model`. The model is encoded, some dependencies and
        accompanying files are packaged, and the app is pushed to Nextmv Cloud.

        By default, this function only pushes the app. If you want to
        automatically create a new version and instance after pushing, set
        `auto_create=True`. The `version_id`, `version_name`, and
        `version_description` arguments allow you to customize the new version
        that is created. If not specified, defaults will be generated (random
        ID, timestamped name/description). Similarly, `instance_id`,
        `instance_name`, and `instance_description` can be used to customize
        the new instance. If `update_default_instance` is True, the
        application's default instance will be updated to the newly created
        instance.

        Parameters
        ----------
        manifest : Optional[Manifest], default=None
            The manifest for the app. If None, an `app.yaml` file in the provided
            app directory will be used.
        app_dir : Optional[str], default=None
            The path to the app's root directory. If None, the current directory
            will be used. This is for the external strategy approach.
        verbose : bool, default=False
            Whether to print verbose output during the push process.
        model : Optional[Model], default=None
            The Python-native model to push. Must be specified together with
            `model_configuration`. This is for the internal strategy approach.
        model_configuration : Optional[ModelConfiguration], default=None
            Configuration for the Python-native model. Must be specified together
            with `model`.
        rich_print : bool, default=False
            Whether to use rich printing when verbose output is enabled.
        auto_create : bool, default=False
            If True, automatically create a new version and instance after
            pushing the app.
        version_id : Optional[str], default=None
            ID of the version to create after pushing the app. If None, a unique
            ID will be generated.
        version_name : Optional[str], default=None
            Name of the version to create after pushing the app. If None, a
            name will be generated.
        version_description : Optional[str], default=None
            Description of the version to create after pushing the app. If None, a
            generic description with a timestamp will be generated.
        instance_id : Optional[str], default=None
            ID of the instance to create after pushing the app. If None, a unique
            ID will be generated.
        instance_name : Optional[str], default=None
            Name of the instance to create after pushing the app. If None, a
            name will be generated.
        instance_description : Optional[str], default=None
            Description of the instance to create after pushing the app. If None,
            a generic description with a timestamp will be generated.
        update_default_instance : bool, default=False
            If True, update the application's default instance to the newly
            created instance.

        Raises
        ------
        ValueError
            If neither app_dir nor model/model_configuration is provided correctly,
            or if only one of model and model_configuration is provided.
        TypeError
            If model is not an instance of nextmv.Model or if model_configuration
            is not an instance of nextmv.ModelConfiguration.
        Exception
            If there's an error in the build, packaging, or cleanup process.

        Examples
        --------
        1. Push an app using an external strategy (directory-based):

        >>> import os
        >>> from nextmv import cloud
        >>> client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
        >>> app = cloud.Application(client=client, id="<YOUR-APP-ID>")
        >>> app.push()  # Use verbose=True for step-by-step output.

        2. Push an app using an internal strategy (Python-native model):

        >>> import os
        >>> import nextroute
        >>> import nextmv
        >>> import nextmv.cloud
        >>>
        >>> # Define the model that makes decisions
        >>> class DecisionModel(nextmv.Model):
        ...     def solve(self, input: nextmv.Input) -> nextmv.Output:
        ...         nextroute_input = nextroute.schema.Input.from_dict(input.data)
        ...         nextroute_options = nextroute.Options.extract_from_dict(input.options.to_dict())
        ...         nextroute_output = nextroute.solve(nextroute_input, nextroute_options)
        ...
        ...         return nextmv.Output(
        ...             options=input.options,
        ...             solution=nextroute_output.solutions[0].to_dict(),
        ...             statistics=nextroute_output.statistics.to_dict(),
        ...         )
        >>>
        >>> # Define the options that the model needs
        >>> opt = []
        >>> default_options = nextroute.Options()
        >>> for name, default_value in default_options.to_dict().items():
        ...     opt.append(nextmv.Option(name.lower(), type(default_value), default_value, name, False))
        >>> options = nextmv.Options(*opt)
        >>>
        >>> # Instantiate the model and model configuration
        >>> model = DecisionModel()
        >>> model_configuration = nextmv.ModelConfiguration(
        ...     name="python_nextroute_model",
        ...     requirements=[
        ...         "nextroute==1.8.1",
        ...         "nextmv==0.14.0.dev1",
        ...     ],
        ...     options=options,
        ... )
        >>>
        >>> # Push the model to Nextmv Cloud
        >>> client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
        >>> app = cloud.Application(client=client, id="<YOUR-APP-ID>")
        >>> manifest = nextmv.cloud.default_python_manifest()
        >>> app.push(
        ...     manifest=manifest,
        ...     verbose=True,
        ...     model=model,
        ...     model_configuration=model_configuration,
        ... )
        """

        if verbose:
            if rich_print:
                rich.print(f":cd: Starting build for Nextmv application [magenta]{self.id}[/magenta].", file=sys.stderr)
            else:
                log("💽 Starting build for Nextmv application.")

        if app_dir is None or app_dir == "":
            app_dir = "."

        if manifest is None:
            manifest = Manifest.from_yaml(app_dir)

        if model is not None and not isinstance(model, Model):
            raise TypeError("model must be an instance of nextmv.Model")

        if model_configuration is not None and not isinstance(model_configuration, ModelConfiguration):
            raise TypeError("model_configuration must be an instance of nextmv.ModelConfiguration")

        if (model is None and model_configuration is not None) or (model is not None and model_configuration is None):
            raise ValueError("model and model_configuration must be provided together")

        package._run_build_command(app_dir, manifest.build, verbose, rich_print)
        package._run_pre_push_command(app_dir, manifest.pre_push, verbose, rich_print)
        tar_file, output_dir = package._package(app_dir, manifest, model, model_configuration, verbose, rich_print)
        self.__update_app_binary(tar_file, manifest, verbose, rich_print)

        try:
            shutil.rmtree(output_dir)
        except OSError as e:
            raise Exception(f"error deleting output directory: {e}") from e

        if not auto_create:
            return

        if verbose:
            if rich_print:
                rich.print(
                    f":hourglass_flowing_sand: Push completed for Nextmv application [magenta]{self.id}[/magenta], "
                    "creating a new version and instance...",
                    file=sys.stderr,
                )
            else:
                log("⌛️ Push completed for the Nextmv application, creating a new version and instance...")

        now = datetime.now(timezone.utc)
        version = self.__version_on_push(
            now=now,
            version_id=version_id,
            version_name=version_name,
            version_description=version_description,
            verbose=verbose,
            rich_print=rich_print,
        )
        instance = self.__instance_on_push(
            now=now,
            version_id=version.id,
            instance_id=instance_id,
            instance_name=instance_name,
            instance_description=instance_description,
            verbose=verbose,
            rich_print=rich_print,
        )
        self.__update_on_push(
            instance=instance,
            update_default_instance=update_default_instance,
            verbose=verbose,
            rich_print=rich_print,
        )

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        default_instance_id: str | None = None,
        default_experiment_instance: str | None = None,
    ) -> "Application":
        """
        Update the application.

        Parameters
        ----------
        name : Optional[str], default=None
            Optional name of the application.
        description : Optional[str], default=None
            Optional description of the application.
        default_instance_id : Optional[str], default=None
            Optional default instance ID for the application.
        default_experiment_instance : Optional[str], default=None
            Optional default experiment instance ID for the application.

        Returns
        -------
        Application
            The updated application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        app = self.get(client=self.client, id=self.id)
        app_dict = app.to_dict()
        payload = app_dict.copy()

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if default_instance_id is not None:
            payload["default_instance"] = default_instance_id
        if default_experiment_instance is not None:
            payload["default_experiment_instance"] = default_experiment_instance

        response = self.client.request(
            method="PUT",
            endpoint=self.endpoint,
            payload=payload,
        )

        return Application.from_dict({"client": self.client} | response.json())

    def upload_data(
        self,
        upload_url: UploadURL | str,
        data: dict[str, Any] | str | None = None,
        json_configurations: dict[str, Any] | None = None,
        tar_file: str | None = None,
    ) -> None:
        """
        Upload data to the provided upload URL.

        This method allows uploading data (either a dictionary or string)
        to a pre-signed URL. If the data is a dictionary, it will be converted to
        a JSON string before upload.

        Parameters
        ----------
        upload_url : UploadURL | str
            Upload URL object containing the pre-signed URL to use for
            uploading. If it is a string, it will be used directly as the
            pre-signed URL.
        data : Optional[Union[dict[str, Any], str]]
            Data to upload. Can be either a dictionary that will be
            converted to JSON, or a pre-formatted JSON string.
        json_configurations : Optional[dict[str, Any]], default=None
            Optional configurations for JSON serialization. If provided, these
            configurations will be used when serializing the data via
            `json.dumps`.
        tar_file : Optional[str], default=None
            If provided, this will be used to upload a tar file instead of
            a JSON string or dictionary. This is useful for uploading large
            files that are already packaged as a tarball.

        Returns
        -------
        None
            This method doesn't return anything.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Upload a dictionary as JSON
        >>> data = {"locations": [...], "vehicles": [...]}
        >>> url = app.upload_url()
        >>> app.upload_data(data=data, upload_url=url)
        >>>
        >>> # Upload a pre-formatted JSON string
        >>> json_str = '{"locations": [...], "vehicles": [...]}'
        >>> app.upload_data(data=json_str, upload_url=url)
        """

        if data is not None and isinstance(data, dict):
            data = deflated_serialize_json(data, json_configurations=json_configurations)

        self.client.upload_to_presigned_url(
            url=upload_url.upload_url if isinstance(upload_url, UploadURL) else upload_url,
            data=data,
            tar_file=tar_file,
        )

    def upload_large_input(
        self,
        input: dict[str, Any] | str | None,
        upload_url: UploadURL,
        json_configurations: dict[str, Any] | None = None,
        tar_file: str | None = None,
    ) -> None:
        """
        !!! warning
            `upload_large_input` is deprecated, use `upload_data` instead.

        Upload large input data to the provided upload URL.

        This method allows uploading large input data (either a dictionary or string)
        to a pre-signed URL. If the input is a dictionary, it will be converted to
        a JSON string before upload.

        Parameters
        ----------
        input : Optional[Union[dict[str, Any], str]]
            Input data to upload. Can be either a dictionary that will be
            converted to JSON, or a pre-formatted JSON string.
        upload_url : UploadURL
            Upload URL object containing the pre-signed URL to use for uploading.
        json_configurations : Optional[dict[str, Any]], default=None
            Optional configurations for JSON serialization. If provided, these
            configurations will be used when serializing the data via
            `json.dumps`.
        tar_file : Optional[str], default=None
            If provided, this will be used to upload a tar file instead of
            a JSON string or dictionary. This is useful for uploading large
            files that are already packaged as a tarball.

        Returns
        -------
        None
            This method doesn't return anything.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Upload a dictionary as JSON
        >>> data = {"locations": [...], "vehicles": [...]}
        >>> url = app.upload_url()
        >>> app.upload_large_input(input=data, upload_url=url)
        >>>
        >>> # Upload a pre-formatted JSON string
        >>> json_str = '{"locations": [...], "vehicles": [...]}'
        >>> app.upload_large_input(input=json_str, upload_url=url)
        """

        deprecated(
            name="Application.upload_large_input",
            reason="`upload_large_input` is deprecated, use `upload_data` instead",
        )

        self.upload_data(
            data=input,
            upload_url=upload_url,
            json_configurations=json_configurations,
            tar_file=tar_file,
        )

    def upload_url(self) -> UploadURL:
        """
        Get an upload URL to use for uploading a file.

        This method generates a pre-signed URL that can be used to upload large files
        to Nextmv Cloud. It's primarily used for uploading large input data, output
        results, or log files that exceed the size limits for direct API calls.

        Returns
        -------
        UploadURL
            An object containing both the upload URL and an upload ID for reference.
            The upload URL is a pre-signed URL that allows temporary write access.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Get an upload URL and upload large input data
        >>> upload_url = app.upload_url()
        >>> large_input = {"locations": [...], "vehicles": [...]}
        >>> app.upload_data(data=large_input, upload_url=upload_url)
        """

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/runs/uploadurl",
        )

        return UploadURL.from_dict(response.json())

    @staticmethod
    def __convert_manifest_to_payload(manifest: Manifest) -> dict[str, Any]:  # noqa: C901
        """Converts a manifest to a payload dictionary for the API."""

        activation_request = {
            "requirements": {
                "executable_type": manifest.type,
                "runtime": manifest.runtime,
            },
        }

        if manifest.configuration is not None and manifest.configuration.content is not None:
            content = manifest.configuration.content
            io_config = {
                "format": content.format,
            }
            if content.multi_file is not None:
                multi_config = io_config["multi_file"] = {}
                if content.multi_file.input is not None:
                    multi_config["input_path"] = content.multi_file.input.path
                if content.multi_file.output is not None:
                    output_config = multi_config["output_configuration"] = {}
                    if content.multi_file.output.statistics:
                        output_config["statistics_path"] = content.multi_file.output.statistics
                    if content.multi_file.output.assets:
                        output_config["assets_path"] = content.multi_file.output.assets
                    if content.multi_file.output.solutions:
                        output_config["solutions_path"] = content.multi_file.output.solutions
            activation_request["requirements"]["io_configuration"] = io_config

        if manifest.configuration is not None and manifest.configuration.options is not None:
            options = manifest.configuration.options.to_dict()
            if "format" in options and isinstance(options["format"], list):
                # the endpoint expects a dictionary with a template key having a list of strings
                # the app.yaml however defines format as a list of strings, so we need to convert it here
                options["format"] = {
                    "template": options["format"],
                }
            activation_request["requirements"]["options"] = options

        if manifest.execution is not None:
            if manifest.execution.entrypoint:
                activation_request["requirements"]["entrypoint"] = manifest.execution.entrypoint
            if manifest.execution.cwd:
                activation_request["requirements"]["working_directory"] = manifest.execution.cwd

        return activation_request

    def __update_app_binary(
        self,
        tar_file: str,
        manifest: Manifest,
        verbose: bool = False,
        rich_print: bool = False,
    ) -> None:
        """Updates the application binary in Cloud."""

        if verbose:
            if rich_print:
                rich.print(f":star2: Pushing to application: [magenta]{self.id}[/magenta].", file=sys.stderr)
            else:
                log(f'🌟 Pushing to application: "{self.id}".')

        endpoint = f"{self.endpoint}/binary"
        response = self.client.request(
            method="GET",
            endpoint=endpoint,
        )
        upload_url = response.json()["upload_url"]

        with open(tar_file, "rb") as f:
            response = self.client.request(
                method="PUT",
                endpoint=upload_url,
                data=f,
                headers={"Content-Type": "application/octet-stream"},
            )

        response = self.client.request(
            method="PUT",
            endpoint=endpoint,
            payload=Application.__convert_manifest_to_payload(manifest=manifest),
        )

        if verbose:
            data = {
                "app_id": self.id,
                "endpoint": self.client.url,
                "instance_url": f"{self.endpoint}/runs?instance_id=latest",
            }

            if rich_print:
                rich.print(f":boom: Successfully pushed to application: [magenta]{self.id}[/magenta].", file=sys.stderr)
                rich.print_json(data=data)
            else:
                log(f'💥️ Successfully pushed to application: "{self.id}".')
                log(json.dumps(data, indent=2))

    def __version_on_push(
        self,
        now: datetime,
        version_id: str | None = None,
        version_name: str | None = None,
        version_description: str | None = None,
        verbose: bool = False,
        rich_print: bool = False,
    ) -> Version:
        if version_description is None or version_description == "":
            version_description = f"Version created automatically from push at {now.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        version = self.new_version(
            id=version_id,
            name=version_name,
            description=version_description,
        )
        version_dict = version.to_dict()

        if not verbose:
            return version

        if rich_print:
            rich.print(
                f":white_check_mark: Automatically created new version [magenta]{version.id}[/magenta].",
                file=sys.stderr,
            )
            rich.print_json(data=version_dict)

            return version

        log(f'✅ Automatically created new version "{version.id}".')
        log(json.dumps(version_dict, indent=2))

        return version

    def __instance_on_push(
        self,
        now: datetime,
        version_id: str,
        instance_id: str | None = None,
        instance_name: str | None = None,
        instance_description: str | None = None,
        verbose: bool = False,
        rich_print: bool = False,
    ) -> Instance:
        if instance_description is None or instance_description == "":
            instance_description = f"Instance created automatically from push at {now.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        instance = self.new_instance(
            version_id=version_id,
            id=instance_id,
            name=instance_name,
            description=instance_description,
        )
        instance_dict = instance.to_dict()

        if not verbose:
            return instance

        if rich_print:
            rich.print(
                f":white_check_mark: Automatically created new instance [magenta]{instance.id}[/magenta] "
                f"using version [magenta]{version_id}[/magenta].",
                file=sys.stderr,
            )
            rich.print_json(data=instance_dict)

            return instance

        log(f'✅ Automatically created new instance "{instance.id}" using version "{version_id}".')
        log(json.dumps(instance_dict, indent=2))

        return instance

    def __update_on_push(
        self,
        instance: Instance,
        update_default_instance: bool = False,
        verbose: bool = False,
        rich_print: bool = False,
    ) -> None:
        if not update_default_instance:
            return

        if verbose:
            if rich_print:
                rich.print(
                    f":hourglass_flowing_sand: Updating default instance for app [magenta]{self.id}[/magenta]...",
                    file=sys.stderr,
                )
            else:
                log("⌛️ Updating default instance for the Nextmv application...")

        updated_app = self.update(default_instance_id=instance.id)
        if not verbose:
            return

        if rich_print:
            rich.print(
                f":white_check_mark: Updated default instance to "
                f"[magenta]{updated_app.default_instance_id}[/magenta] for application "
                f"[magenta]{self.id}[/magenta].",
                file=sys.stderr,
            )
            rich.print_json(data=updated_app.to_dict())

            return

        log(
            f'✅ Updated default instance to "{updated_app.default_instance_id}" for application "{self.id}".',
        )
        log(json.dumps(updated_app.to_dict(), indent=2))


def list_applications(client: Client) -> list[Application]:
    """
    List all Nextmv Cloud applications.

    You can import the `list_applications` function directly from `cloud`:

    ```python
    from nextmv.cloud import list_applications
    ```

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client used to make API requests.

    Returns
    -------
    list[Application]
        A list of Nextmv Cloud applications.

    Raises
    -------
    requests.HTTPError
        If the response status code is not 2xx.
    """

    response = client.request(
        method="GET",
        endpoint="v1/applications",
    )

    applications = []
    for app_data in response.json() or []:
        app = Application.from_dict({"client": client} | app_data)
        applications.append(app)

    return applications
