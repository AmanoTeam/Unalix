import pathlib
import os.path


PATH_PACKAGE_DATA = os.path.join(pathlib.Path(__file__).parent.parent, "package_data")

PATH_RULESETS = (
    os.path.join(PATH_PACKAGE_DATA, "rulesets", "data.min.json"),
    os.path.join(PATH_PACKAGE_DATA, "rulesets", "unalix.json")
)

PATH_COOKIES_ALLOW = (
    os.path.join(PATH_PACKAGE_DATA, "policies", "cookies_allow.json"),
)

PATH_BODY_REDIRECTS = (
    os.path.join(PATH_PACKAGE_DATA, "other", "redirects_from_body.json"),
)

PATH_CA_BUNDLE = os.path.join(PATH_PACKAGE_DATA, "ca", "ca-bundle.crt")
