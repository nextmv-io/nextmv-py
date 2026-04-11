"""Core marketplace management actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Each action takes ``client: Client`` as its first parameter so the CLI
framework can inject a client at call time. Remaining parameters use
dual-purpose ``Annotated`` aliases from ``nextmv.cli.framework.options``.

Marketplace is CLI-only today — there is no corresponding
``mcp/tools/marketplace.py`` — but following the same pattern lets the
connector table share the same building blocks as every other domain.
"""

from typing import Annotated, Any

import typer
from pydantic import Field

from nextmv.cli.framework.options import (
    DescriptionOption,
    MarketplaceAppIdOption,
    MarketplacePartnerIdOption,
    MarketplaceSubscriptionIdOption,
    MarketplaceVersionIdOption,
    OptionalMarketplaceAppIdOption,
    OptionalMarketplacePartnerIdOption,
    OptionalMarketplaceVersionIdOption,
)
from nextmv.cloud import Client
from nextmv.cloud.marketplace import (
    MarketplaceApplication,
    MarketplaceState,
    MarketplaceSubscription,
    list_marketplace_applications,
    list_marketplace_subscriptions,
)

# ---------------------------------------------------------------------------
# Non-shared option aliases used only by marketplace actions. Declared here
# to keep the framework options file focused on widely-shared options.
# ---------------------------------------------------------------------------

_MARKETPLACE_TITLE_HELP = "The title of the Nextmv Marketplace application."
MarketplaceTitleOption = Annotated[
    str,
    typer.Option("--title", "-t", help=_MARKETPLACE_TITLE_HELP, metavar="TITLE"),
    Field(description=_MARKETPLACE_TITLE_HELP),
]

_OPTIONAL_MARKETPLACE_TITLE_HELP = (
    "An optional title to update on the Nextmv Marketplace application."
)
OptionalMarketplaceTitleOption = Annotated[
    str | None,
    typer.Option(
        "--title",
        "-t",
        help=_OPTIONAL_MARKETPLACE_TITLE_HELP,
        metavar="TITLE",
    ),
    Field(description=_OPTIONAL_MARKETPLACE_TITLE_HELP),
]

_REFERENCE_APP_ID_HELP = (
    "The ID of an existing application to use as a reference for the "
    "new marketplace application."
)
ReferenceAppIdOption = Annotated[
    str,
    typer.Option(
        "--reference-app-id",
        "-r",
        help=_REFERENCE_APP_ID_HELP,
        metavar="REFERENCE_APP_ID",
    ),
    Field(description=_REFERENCE_APP_ID_HELP),
]

_REFERENCE_VERSION_ID_HELP = (
    "The ID of an existing version to use as a reference for the new "
    "marketplace version."
)
ReferenceVersionIdOption = Annotated[
    str,
    typer.Option(
        "--reference-version-id",
        "-r",
        help=_REFERENCE_VERSION_ID_HELP,
        metavar="REFERENCE_VERSION_ID",
    ),
    Field(description=_REFERENCE_VERSION_ID_HELP),
]

_CATEGORIES_HELP = (
    "Categories for the marketplace application. "
    "Pass multiple categories by repeating the flag."
)
CategoriesOption = Annotated[
    list[str] | None,
    typer.Option(
        "--categories",
        "-c",
        help=_CATEGORIES_HELP,
        metavar="CATEGORIES",
    ),
    Field(description=_CATEGORIES_HELP),
]

_FEATURES_HELP = (
    "Features for the marketplace application. "
    "Pass multiple features by repeating the flag."
)
FeaturesOption = Annotated[
    list[str] | None,
    typer.Option(
        "--features",
        "-f",
        help=_FEATURES_HELP,
        metavar="FEATURES",
    ),
    Field(description=_FEATURES_HELP),
]

_CHANGE_LOG_HELP = (
    "Change log entries for the marketplace version. "
    "Pass multiple entries by repeating the flag."
)
ChangeLogOption = Annotated[
    list[str],
    typer.Option(
        "--change-log",
        "-c",
        help=_CHANGE_LOG_HELP,
        metavar="CHANGE_LOG",
    ),
    Field(description=_CHANGE_LOG_HELP),
]

_MARKETPLACE_STATE_HELP = (
    "The state of the marketplace application. "
    "Allowed values: draft, released, archived."
)
MarketplaceStateOption = Annotated[
    MarketplaceState | None,
    typer.Option(
        "--state",
        "-s",
        help=_MARKETPLACE_STATE_HELP,
        metavar="STATE",
    ),
    Field(description=_MARKETPLACE_STATE_HELP),
]


# ---------------------------------------------------------------------------
# App actions
# ---------------------------------------------------------------------------


def list_marketplace_apps(
    client: Client,
    partner_id: OptionalMarketplacePartnerIdOption = None,
) -> list[dict[str, Any]]:
    """List Nextmv Marketplace applications.

    Use ``partner_id`` to filter applications belonging to a specific
    partner. Returns a list of application dicts.
    """
    apps = list_marketplace_applications(client, partner_id)
    return [a.to_dict() for a in apps]


def get_marketplace_app(
    client: Client,
    app_id: MarketplaceAppIdOption,
    partner_id: MarketplacePartnerIdOption,
) -> dict[str, Any]:
    """Get a Nextmv Marketplace application by ID.

    Returns the application dict.
    """
    return MarketplaceApplication.get(
        client=client,
        partner_id=partner_id,
        app_id=app_id,
    ).to_dict()


def create_marketplace_app(
    client: Client,
    partner_id: MarketplacePartnerIdOption,
    reference_app_id: ReferenceAppIdOption,
    title: MarketplaceTitleOption,
    app_id: OptionalMarketplaceAppIdOption = None,
    description: DescriptionOption = None,
    categories: CategoriesOption = None,
    features: FeaturesOption = None,
) -> dict[str, Any]:
    """Create a new Nextmv Marketplace application.

    Marketplace applications are created under a partner ID and are
    based on a reference application which serves as a template.
    Applications can be enriched with categories and features to
    improve discoverability.
    """
    return MarketplaceApplication.new(
        client=client,
        partner_id=partner_id,
        reference_app_id=reference_app_id,
        title=title,
        app_id=app_id,
        description=description,
        categories=categories,
        features=features,
    ).to_dict()


def update_marketplace_app(
    client: Client,
    app_id: MarketplaceAppIdOption,
    partner_id: MarketplacePartnerIdOption,
    title: OptionalMarketplaceTitleOption = None,
    description: DescriptionOption = None,
    categories: CategoriesOption = None,
    features: FeaturesOption = None,
    state: MarketplaceStateOption = None,
) -> dict[str, Any]:
    """Update a Nextmv Marketplace application.

    Only the provided fields are updated; omitted fields remain
    unchanged. Returns the updated application dict.
    """
    mkt_app = MarketplaceApplication.get(
        client=client,
        partner_id=partner_id,
        app_id=app_id,
    )
    return mkt_app.update(
        title=title,
        description=description,
        categories=categories,
        features=features,
        state=state,
    ).to_dict()


# ---------------------------------------------------------------------------
# Subscription actions
# ---------------------------------------------------------------------------


def list_marketplace_subs(client: Client) -> list[dict[str, Any]]:
    """List all Nextmv Marketplace subscriptions for the current account.

    Returns a list of subscription dicts.
    """
    return [s.to_dict() for s in list_marketplace_subscriptions(client)]


def get_marketplace_subscription(
    client: Client,
    subscription_id: MarketplaceSubscriptionIdOption,
) -> dict[str, Any]:
    """Get a Nextmv Marketplace subscription.

    Returns the subscription dict.
    """
    return MarketplaceSubscription.get(
        client=client,
        subscription_id=subscription_id,
    ).to_dict()


def create_marketplace_subscription(
    client: Client,
    subscription_id: MarketplaceSubscriptionIdOption,
) -> dict[str, Any]:
    """Create a new Nextmv Marketplace subscription.

    Subscribe to a marketplace application by providing the
    subscription ID, which combines the partner ID and application ID
    in the format ``<PARTNER_ID>-<APP_ID>``.
    """
    return MarketplaceSubscription.new(client, subscription_id).to_dict()


def delete_marketplace_subscription(
    client: Client,
    subscription_id: MarketplaceSubscriptionIdOption,
) -> None:
    """Delete a Nextmv Marketplace subscription.

    This cancels the subscription and removes the marketplace
    application from the current account.
    """
    MarketplaceSubscription.get(
        client=client,
        subscription_id=subscription_id,
    ).delete()


# ---------------------------------------------------------------------------
# Version actions
# ---------------------------------------------------------------------------


def list_marketplace_versions(
    client: Client,
    app_id: MarketplaceAppIdOption,
    partner_id: MarketplacePartnerIdOption,
) -> list[dict[str, Any]]:
    """List all versions of a Nextmv Marketplace application.

    Returns a list of version dicts.
    """
    mkt_app = MarketplaceApplication.get(
        client=client,
        partner_id=partner_id,
        app_id=app_id,
    )
    return [v.to_dict() for v in mkt_app.list_versions()]


def get_marketplace_version(
    client: Client,
    app_id: MarketplaceAppIdOption,
    partner_id: MarketplacePartnerIdOption,
    version_id: MarketplaceVersionIdOption,
) -> dict[str, Any]:
    """Get a Nextmv Marketplace version for an application.

    Returns the version dict.
    """
    mkt_app = MarketplaceApplication.get(
        client=client,
        partner_id=partner_id,
        app_id=app_id,
    )
    return mkt_app.version(version_id=version_id).to_dict()


def create_marketplace_version(
    client: Client,
    app_id: MarketplaceAppIdOption,
    partner_id: MarketplacePartnerIdOption,
    reference_version_id: ReferenceVersionIdOption,
    change_log: ChangeLogOption,
    version_id: OptionalMarketplaceVersionIdOption = None,
) -> dict[str, Any]:
    """Create a new Nextmv Marketplace version for an application.

    Marketplace versions are created by referencing an existing version
    from the underlying application. The change log provides
    information about what has changed in this marketplace version.
    """
    mkt_app = MarketplaceApplication.get(
        client=client,
        partner_id=partner_id,
        app_id=app_id,
    )
    return mkt_app.new_version(
        change_log=change_log,
        reference_version_id=reference_version_id,
        version_id=version_id,
    ).to_dict()


def update_marketplace_version(
    client: Client,
    app_id: MarketplaceAppIdOption,
    partner_id: MarketplacePartnerIdOption,
    version_id: MarketplaceVersionIdOption,
    change_log: ChangeLogOption,
) -> dict[str, Any]:
    """Update a Nextmv Marketplace version's change log.

    Returns the updated version dict.
    """
    mkt_app = MarketplaceApplication.get(
        client=client,
        partner_id=partner_id,
        app_id=app_id,
    )
    return mkt_app.update_version(
        version_id=version_id,
        change_log=change_log,
    ).to_dict()
