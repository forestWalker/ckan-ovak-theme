from setuptools import setup, find_packages

setup(
    name="ckanext-ovak-theme",
    version="0.1.0",
    description="OVAK custom CKAN theme",
    packages=['ckanext.ovak_theme'],
    package_dir={'ckanext.ovak_theme': 'ckanext/ovak_theme', '': '.'},
    include_package_data=True,
    zip_safe=False,
    entry_points="""
        [ckan.plugins]
        ovak_theme=ckanext.ovak_theme.plugin:OvakThemePlugin
    """,
)
