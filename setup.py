from setuptools import setup, find_packages

setup(
    name="ckanext-ovak-theme",
    version="0.0.1",
    description="OVAK custom CKAN theme",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points="""
        [ckan.plugins]
        ovak_theme=ckanext.ovak_theme.plugin:OvakThemePlugin
    """,
)