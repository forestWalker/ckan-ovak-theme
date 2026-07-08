import json
from pathlib import Path
from urllib.parse import urlencode

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint


CONTENT_DIR = Path(__file__).resolve().parent / "content"
CONTENT_CACHE = {}


def _fallback_content(filename: str) -> dict:
    return {
        "municipality_name": "Missing content",
        "portal_title": f"Missing JSON: {filename}",
        "nav": {
            "datasets": "Datasets",
            "visualizations": "Visualizations",
            "information": "Information"
        },
        "search_placeholder": "Search",
        "language_switch_label": "HU",
        "chips": [],
        "summary": {
            "title": "Missing summary",
            "body": ""
        },
        "news": {
            "title": "Missing news",
            "date": "",
            "body": ""
        },
        "dataset_detail_page": {
            "breadcrumbs": {
                "home": "Home",
                "datasets": "Datasets"
            },
            "resources_title": "Data",
            "tags_title": "Tags",
            "additional_info_title": "Additional information",
            "edit_button": "Edit dataset",
            "fields": {},
            "empty": {}
        },
        "footer": {
            "links": []
        },
        "resource_page": {
            "breadcrumbs": {
                "home": "Home",
                "datasets": "Datasets"
            },
            "empty_description": "No description is available for this resource.",
            "table_button": "Table",
            "chart_button": "Chart",
            "download_button": "Download"
        }
    }


def _merge_missing_content(data: dict, fallback: dict) -> dict:
    for key, value in fallback.items():
        if key not in data:
            data[key] = value
        elif isinstance(value, dict) and isinstance(data[key], dict):
            _merge_missing_content(data[key], value)
    return data


def read_json_file(filename: str) -> dict:
    file_path = CONTENT_DIR / filename
    fallback = _fallback_content(filename)

    if not file_path.exists():
        return fallback

    try:
        mtime = file_path.stat().st_mtime
        cached = CONTENT_CACHE.get(filename)
        if cached and cached["mtime"] == mtime:
            return cached["data"]

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return fallback

        data = _merge_missing_content(data, fallback)
        CONTENT_CACHE[filename] = {"mtime": mtime, "data": data}
        return data

    except Exception as e:
        fallback["municipality_name"] = "Content error"
        fallback["portal_title"] = "JSON read error"
        fallback["summary"]["title"] = "Error loading summary"
        fallback["summary"]["body"] = str(e)
        fallback["news"]["title"] = "Error loading news"
        fallback["news"]["body"] = str(e)
        return fallback


def get_current_lang() -> str:
    request = toolkit.request

    cookie_lang = request.cookies.get("ovak_lang")
    if cookie_lang in ("hu", "en"):
        return cookie_lang

    query_lang = request.args.get("lang")
    if query_lang in ("hu", "en"):
        return query_lang

    return "en"


def get_language_switch_url() -> str:
    request = toolkit.request
    current_lang = get_current_lang()
    new_lang = "hu" if current_lang == "en" else "en"

    args = request.args.to_dict(flat=True)
    args["lang"] = new_lang

    path = request.path or "/"
    query = urlencode(args)

    if query:
        return f"{path}?{query}"

    return f"{path}?lang={new_lang}"


def visualizations_page():
    return toolkit.render("home/visualizations.html")


def information_page():
    return toolkit.render("home/information.html")


def ovak_resource_page(dataset_name: str, resource_id: str):
    context = {
        "user": getattr(toolkit.g, "user", None),
        "auth_user_obj": getattr(toolkit.g, "userobj", None),
        "ignore_auth": True,
    }

    package = toolkit.get_action("package_show")(context, {"id": dataset_name})

    resource = None
    for res in package.get("resources", []):
        if res.get("id") == resource_id:
            resource = res
            break

    if not resource:
        toolkit.abort(404, "Resource not found")

    resource_views = toolkit.get_action("resource_view_list")(
        context,
        {"id": resource_id}
    )

    return toolkit.render(
        "package/ovak_resource_csv.html",
        extra_vars={
            "package": package,
            "pkg_dict": package,
            "resource": resource,
            "resource_views": resource_views,
        }
    )


class OvakThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")

    def get_helpers(self):
        return {
            "ovak_read_json_file": read_json_file,
            "ovak_get_current_lang": get_current_lang,
            "ovak_get_language_switch_url": get_language_switch_url,
        }

    def get_blueprint(self):
        blueprint = Blueprint(
            "ovak_theme",
            __name__
        )

        blueprint.add_url_rule(
            "/visualizations",
            "visualizations",
            visualizations_page
        )

        blueprint.add_url_rule(
            "/information",
            "information",
            information_page
        )

        blueprint.add_url_rule(
            "/ovak-resource/<dataset_name>/<resource_id>",
            "ovak_resource_page",
            ovak_resource_page
        )

        return blueprint
