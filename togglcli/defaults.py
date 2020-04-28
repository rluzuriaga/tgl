def get_default_config_file_path() -> str:
    import pkg_resources
    config_file_path = pkg_resources.resource_filename('togglcli', 'data/config.json')
    return config_file_path