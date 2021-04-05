import pathlib
import os.path

from ..types import Path, Tuple


PATH_PACKAGE_DATA = Path(
    os.path.join(pathlib.Path(__file__).parent.parent, "package_data")
)

PATH_RULESETS = Tuple((
    Path(os.path.join(PATH_PACKAGE_DATA, "rulesets", "data.min.json")),
    Path(os.path.join(PATH_PACKAGE_DATA, "rulesets", "unalix.json"))
))

PATH_COOKIES_ALLOW = Tuple((
    Path(os.path.join(PATH_PACKAGE_DATA, "policies", "cookies_allow.json")),
))

PATH_BODY_REDIRECTS = Tuple((
    Path(os.path.join(PATH_PACKAGE_DATA, "other", "redirects_from_body.json")),
))

PATH_CA_BUNDLE = Path(os.path.join(PATH_PACKAGE_DATA, "ca", "ca-bundle.crt"))