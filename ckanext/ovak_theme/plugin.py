from pathlib import Path
import json

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def read_json_file(filename: str) -> dict:
    base_path = Path(__file__).resolve().parent / "content"
    file_path = base_path / filename

    fallback = {
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
        "footer": {
            "links": []
        }
    }

    if not file_path.exists():
        return fallback

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return fallback

        return data

    except Exception as e:
        return {
            "municipality_name": "Content error",
            "portal_title": "JSON read error",
            "nav": {
                "datasets": "Datasets",
                "visualizations": "Visualizations",
                "information": "Information"
            },
            "search_placeholder": "Search",
            "language_switch_label": "HU",
            "chips": [],
            "summary": {
                "title": "Error loading summary",
                "body": str(e)
            },
            "news": {
                "title": "Error loading news",
                "date": "",
                "body": str(e)
            },
            "footer": {
                "links": []
            }
        }


def get_current_lang() -> str:
    request = toolkit.request

    lang = request.args.get("lang")
    if lang in ("hu", "en"):
        return lang

    return "en"


def get_language_switch_url() -> str:
    request = toolkit.request
    current_lang = get_current_lang()
    new_lang = "hu" if current_lang == "en" else "en"

    args = request.args.to_dict(flat=True)
    args["lang"] = new_lang

    query = "&".join(f"{key}={value}" for key, value in args.items())

    path = request.path or "/"

    if query:
        return f"{path}?{query}"

    return f"{path}?lang={new_lang}"


class OvakThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")

    def get_helpers(self):
        return {
            "ovak_read_json_file": read_json_file,
            "ovak_get_current_lang": get_current_lang,
            "ovak_get_language_switch_url": get_language_switch_url,
        }