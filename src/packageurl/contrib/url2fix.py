# -*- coding: utf-8 -*-
#
# Copyright (c) the purl authors
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Visit https://github.com/package-url/packageurl-python for support and
# download.

import re
from dataclasses import dataclass

from packageurl.contrib.route import NoRouteAvailable
from packageurl.contrib.route import Router

"""
This module extract commit and git repo url for an arbitrary URL.
This uses the a routing mechanism available in the route.py module.

In order to make it easy to use, it contains all the conversion functions
in this single Python script.
"""


fix_router = Router()


@dataclass
class CodeFix:
    url: str
    vcs_url: str
    commit_hash: str
    patch_url: str | None


def url2fix(url):
    """
    Return a CodeFix inferred from the `url` string or None.
    """
    if url:
        try:
            return fix_router.process(url)
        except NoRouteAvailable:
            return


@fix_router.route("https?://github\.com/.*")
def build_github_fix(url):
    """
    Return a CodeFix object from GitHub `url`.
    For example:
    https://github.com/aboutcode-org/vulnerablecode/commit/818b92ba8fbdbebf5e773d37eddc4a1698b660a4
    https://github.com/aboutcode-org/vulnerablecode/tree/818b92ba8fbdbebf5e773d37eddc4a1698b660a4
    https://github.com/aboutcode-org/vulnerablecode/blob/818b92ba8fbdbebf5e773d37eddc4a1698b660a4
    """
    pattern = (
        r"https?://github\.com/"
        r"(?P<namespace>[^/]+)/(?P<name>[^/]+)/"
        r"(?:commit|blob|tree)/(?P<commit_hash>[0-9a-fA-F]{7,40})"
        r"(?:/.*)?$"
    )

    matches = re.match(pattern, url)
    namespace = matches.group("namespace")
    name = matches.group("name")
    commit_hash = matches.group("commit_hash")

    vcs_url = f"https://github.com/{namespace}/{name}.git"
    patch_url = f"https://github.com/{namespace}/{name}/commit/{commit_hash}.patch"
    return CodeFix(url=url, vcs_url=vcs_url, commit_hash=commit_hash, patch_url=patch_url)


@fix_router.route("https?://gitlab\.com/.*")
def build_gitlab_fix(url):
    """
    Return a CodeFix object from Gitlab `url`.
    For example:
    https://gitlab.com/tg1999/Firebase/commit/6ceeeb9feb2b7420230e0d19753a626f9a43f9cb
    https://gitlab.com/tg1999/Firebase/-/commit/6ceeeb9feb2b7420230e0d19753a626f9a43f9cb
    https://gitlab.com/tg1999/Firebase/-/blob/6ceeeb9feb2b7420230e0d19753a626f9a43f9cb
    https://gitlab.com/tg1999/Firebase/-/tree/6ceeeb9feb2b7420230e0d19753a626f9a43f9cb
    """
    gitlab_pattern = (
        r"^https?://gitlab\.com/"
        r"(?P<namespace>[^/]+)/"
        r"(?P<name>[^/]+)/"
        r"(?:-/)?"
        r"(?:commit|blob|tree)/"
        r"(?P<commit_hash>[0-9a-fA-F]{7,64})"
        r"(?:/(?P<subpath>.+))?"
        r"/?$"
    )

    matches = re.match(gitlab_pattern, url)
    namespace = matches.group("namespace")
    name = matches.group("name")
    commit_hash = matches.group("commit_hash")

    vcs_url = f"https://gitlab.com/{namespace}/{name}"
    patch_url = f"https://gitlab.com/{namespace}/{name}/-/commit/{commit_hash}.patch"
    return CodeFix(url=url, vcs_url=vcs_url, commit_hash=commit_hash, patch_url=patch_url)


@fix_router.route("https?://bitbucket\.org/.*")
def build_bitbucket_fix(url):
    """
    Return a CodeFix object from BitBucket `url`.
    For example:
    https://bitbucket.org/TG1999/first_repo/commits/38b63edeafc7cc3c3c3ca904cea6c639a96695ab
    """
    # https://bitbucket.org/<namespace>/<name>/commits/<sha>
    bitbucket_commit_pattern = (
        r"https?://bitbucket.org/"
        r"(?P<namespace>[^/]+)/(?P<name>[^/]+)/commits/(?P<commit_hash>[0-9a-fA-F]{7,64})/?$"
    )

    commit_match = re.match(bitbucket_commit_pattern, url)
    namespace = commit_match.group("namespace")
    name = commit_match.group("name")
    commit_hash = commit_match.group("commit_hash")

    vcs_url = f"https://bitbucket.org/{namespace}/{name}"
    patch_url = f"https://bitbucket.org/{namespace}/{name}/commits/{commit_hash}/raw"
    return CodeFix(url=url, vcs_url=vcs_url, commit_hash=commit_hash, patch_url=patch_url)


SELF_HOSTED_GITLAB_ROUTE_REGEX = [
    r"https?://git\.codelinaro\.org/.*",
    r"https?://salsa\.debian\.org/.*",
    "https?://gitlab\.alpinelinux.org/.*",
    "https?://gitlab\.eclipse.org/.*",
    "https?://gitlab\.e\.foundation/.*",
    "https?://gitlab\.eurecom\.fr/.*",
    "https?://gitlab\.freedesktop\.org/.*",
    "https?://gitlab\.fusiondirectory\.org/.*",
    "https?://gitlab\.gnome\.org/.*",
    "https?://gitlab\.isc\.org/.*",
    "https?://gitlab\.kitware\.com/.*",
    "https?://gitlab\.labs\.nic\.cz/.*",
    "https?://gitlab\.lisn\.upsaclay\.fr/.*",
    "https?://gitlab\.manjaro\.org/.*",
    "https?://gitlab\.marlam\.de/.*",
    "https?://gitlab\.matrix\.org/.*",
    "https?://gitlab\.nic\.cz/.*",
    "https?://gitlab\.ow2\.org/.*",
    "https?://gitlab\.redox-os\.org/.*",
    "https?://gitlab\.studip\.de/.*",
    "https?://gitlab\.synchro\.net/.*",
    "https?://gitlab\.torproject\.org/.*",
    "https?://gitlab\.vsb\.cz/.*",
    "https?://gitlab\.xfce\.org/.*",
    "https?://gitlab\.xiph\.org/.*",
]


@fix_router.route(*SELF_HOSTED_GITLAB_ROUTE_REGEX)
def build_self_hosted_gitlab_fix(url):
    """
    Return a CodeFix object from a GitLab self hosted domain URL
    For example:
    https://gitlab.gnome.org/GNOME/gimp/-/commit/112a5e038f0646eae5ae314988ec074433d2b365
    https://git.codelinaro.org/linaro/qcom/project/-/commit/a40a9732c840e5a324fba78b0ff7980b497c3831
    https://salsa.debian.org/rust-team/debcargo-conf/-/tree/4718f75e0ccbb6f1bb79c3692204c5b118a750d9
    https://gitlab.labs.nic.cz/labs/bird/commit/1657c41c96b3c07d9265b07dd4912033ead4124b
    """
    gitlab_sub_pattern = (
        r"^https?://"
        r"(?P<domain>[^/]+)/"
        r"(?P<namespace>.+?)/"
        r"(?P<name>[^/]+)/"
        r"(?:-/)?"
        r"(?:tree|blob|commit)/"
        r"(?P<commit_hash>[^/]+)"
        r"(?:/(?P<subpath>.+))?"
        r"/?$"
    )

    if gitlab_sub_match := re.match(gitlab_sub_pattern, url):
        domain = gitlab_sub_match.group("domain")
        namespace = gitlab_sub_match.group("namespace")
        name = gitlab_sub_match.group("name")
        commit_hash = gitlab_sub_match.group("commit_hash")

        vcs_url = f"https://{domain}/{namespace}/{name}"
        patch_url = f"https://{domain}/{namespace}/{name}/-/commit/{commit_hash}.patch"
        return CodeFix(url=url, vcs_url=vcs_url, commit_hash=commit_hash, patch_url=patch_url)


GITILES_ROUTE_REGEX = [
    r"https?://android\.googlesource\.com/.*",
    r"https?://aomedia\.googlesource\.com/.*",
    r"https?://boringssl\.googlesource\.com/.*",
    r"https?://chromium\.googlesource\.com/.*",
    r"https?://fuchsia\.googlesource\.com/.*",
    r"https?://gerrit\.googlesource\.com/.*",
    r"https?://go\.googlesource\.com/.*",
    r"https?://kernel\.googlesource\.com/.*",
    r"https?://pdfium\.googlesource\.com/.*",
    r"https?://skia\.googlesource\.com/.*",
]


@fix_router.route(*GITILES_ROUTE_REGEX)
def build_gitiles_fix(url):
    """
    Return a CodeFix object from Gitiles url
    For example:
    https://android.googlesource.com/platform/frameworks/base/+/50eec20b570cd4cbbe8c5971af4c9dda3ddcb858
    https://aomedia.googlesource.com/aom/+/4efe20e99dcd9b6f8eadc8de8acc825be7416578
    https://boringssl.googlesource.com/boringssl/+/e759a9cd84198613199259dbed401f4951747cff
    https://chromium.googlesource.com/infra/infra/+/77ef00cb53d90c9d1f984eca434d828de5c167a5
    https://fuchsia.googlesource.com/fuchsia/+/40e7fbcdcd013441daf4492f1ead349a9e5b80dc
    https://gerrit.googlesource.com/gerrit/+/45071d6977932bca5a1427c8abad24710fed2e33
    https://go.googlesource.com/go/+/960ffa98ce73ef2c2060c84c7ac28d37a83f345e
    https://kernel.googlesource.com/pub/scm/git/git/+/3ec804490a265f4c418a321428c12f3f18b7eff5
    https://pdfium.googlesource.com/pdfium/+/767aebbef641a89498deebc29369a078207b4dcc
    https://skia.googlesource.com/skia/+/1c577cd3ee331944b9061ee0eec147b211ee563c
    """

    gitiles_project_pattern = (
        r"^https?://"
        r"(?P<domain>[^/]+)/"
        r"(?:(?P<namespace>(?:(?!/\+/).)+)/)?"
        r"(?P<name>[^/]+)"
        r"(?:/\+/(?P<commit_hash>[0-9a-fA-F]{7,64}))?"
        r"/?$"
    )

    matches = re.match(gitiles_project_pattern, url)
    domain = matches.group("domain")
    namespace = matches.group("namespace")
    name = matches.group("name")
    commit_hash = matches.group("commit_hash")

    if name and namespace:
        project_path = f"{namespace}/{name}"
    else:
        project_path = name

    vcs_url = f"https://{domain}/{project_path}"
    patch_url = f"https://{domain}/{project_path}/+/{commit_hash}^!?format=TEXT"
    return CodeFix(url=url, vcs_url=vcs_url, commit_hash=commit_hash, patch_url=patch_url)


GITEA_ROUTE_REGEX = [
    r"https?://codeberg\.org/.*",
    r"https?://gitea\.com/.*",
    r"https?://forge\.fedoraproject\.org/.*",
    r"https?://git\.distrust\.co/.*",
    r"https?://git\.enlightenment\.org/.*",
]


@fix_router.route(*GITEA_ROUTE_REGEX)
def build_gitea_fix(url):
    """
    Return a CodeFix object from a gitea/forgejo url
    For example:
    https://codeberg.org/alpinelinux/aports/commit/a40a9732c840e5a324fba78b0ff7980b497c3831
    https://gitea.com/htc47/entur/commit/271b852cfb761a1fe257aa0f0a12ff38bd8bfd1c
    """
    gitea_commit_pattern = (
        r"^https?://"
        r"(?P<namespace>.+?)/"
        r"(?P<name>[^/]+)"
        r"(?:/commit/(?P<commit_hash>[0-9a-fA-F]{7,64}))?"
        r"/?$"
    )

    matches = re.match(gitea_commit_pattern, url)
    namespace = matches.group("namespace")
    name = matches.group("name")
    commit_hash = matches.group("commit_hash")

    vcs_url = f"https://{namespace}/{name}.git"
    patch_url = f"https://{namespace}/{name}/commit/{commit_hash}.patch"
    return CodeFix(url=url, vcs_url=vcs_url, commit_hash=commit_hash, patch_url=patch_url)


CGIT_ROUTE_REGEX = [
    r"https?://git\.kernel\.org/.*",
    r"https?://gitweb\.gentoo\.org/.*",
    r"https?://cgit\.git\.savannah\.gnu\.org/.*",
    r"https?://git.musl-libc\.org/cgit/.*",
    r"https?://git\.pengutronix\.de/cgit/.*",
    r"https?://git\.libssh\.org/.*",
]


@fix_router.route(*CGIT_ROUTE_REGEX)
def build_cgit_fix(url):
    """
    Return a CodeFix object from a cgit url
    For example:
    https://git.kernel.org/pub/scm/bluetooth/bluez.git/commit/?id=74770b1fd2be612f9c2cf807db81fcdcc35e6560
    https://git.kernel.org/pub/scm/linux/kernel/git/deller/linux-fbdev.git/commit/?h=for-next&id=bd771cf5c4254511cc4abb88f3dab3bd58bdf8e8
    https://web.git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/fs/smb?id=db363b0a1d9e6b9dc556296f1b1007aeb496a8cf
    https://git.kernel.org/stable/c/9a9a8fe26751334b7739193a94eba741073b8a55
    https://cgit.git.savannah.gnu.org/cgit/uddf.git/commit/?id=98c41e131dc952aee43d4ec392b80ca4c426be8d
    https://gitweb.gentoo.org/dev/darkside.git/commit/?id=8d4b0836f3b6ab7075212926d9aad0b50246d825
    https://git.musl-libc.org/cgit/musl/commit/?id=c47ad25ea3b484e10326f933e927c0bc8cded3da
    https://git.pengutronix.de/cgit/barebox/commit/?id=7cf25e0733f08f68d1bf0ca0c3cf6e2dfe51bd3c
    https://git.libssh.org/projects/libssh.git/commit/?id=697650caa97eaf7623924c75f9fcfec6dd423cd1
    """

    # https://git.kernel.org/stable/c/<hash>
    kernel_shorthand = r"^https?://git\.kernel\.org/stable/c/(?P<commit_hash>[0-9a-fA-F]{7,64})/?$"

    cgit_project_pattern = (
        r"^https?://"
        r"(?P<namespace>.+?)/"
        r"(?P<name>[^/]+?)"
        r"(?:\.git)?"
        r"/commit/(?:[^?]+)?\?.*?\bid=(?P<commit_hash>[0-9a-fA-F]{7,64})(?:&.*)?"
        r"/?$"
    )

    if match := re.match(kernel_shorthand, url):
        res = match.groupdict()
        namespace = "git.kernel.org/pub/scm/linux/kernel/git/stable/"
        name = "linux"
        commit_hash = res["commit_hash"]
    elif match := re.match(cgit_project_pattern, url):
        res = match.groupdict()
        name = res["name"]
        namespace = res["namespace"]
        commit_hash = res["commit_hash"]
    else:
        return

    vcs_url = f"https://{namespace}/{name}.git"
    patch_url = f"https://{namespace}/{name}.git/patch/?id={commit_hash}"
    return CodeFix(url=url, vcs_url=vcs_url, commit_hash=commit_hash, patch_url=patch_url)


@fix_router.route(r"https?://sourceforge\.net/p/.*")
def build_allura_fix(url):
    """
    Return a CodeFix object from an Apache Allura url (e.g., SourceForge).
    For example:
    https://sourceforge.net/p/djvu/djvulibre-git/ci/e15d51510048927f172f1bf1f27ede65907d940d
    https://sourceforge.net/p/infrarecorder/code/ci/9361b6f267e7b1c1576c48f6dac6dec18d8a93e0/
    """

    allura_pattern = (
        r"^https?://sourceforge\.net"
        r"/p/"
        r"(?P<namespace>[^/]+)/"
        r"(?P<name>[^/]+)"
        r"(?:/ci/(?P<commit_hash>[0-9a-fA-F]{7,64}))?"
        r"/?$"
    )

    commit_match = re.match(allura_pattern, url)
    namespace = commit_match.group("namespace")
    name = commit_match.group("name")
    commit_hash = commit_match.group("commit_hash")

    vcs_url = f"https://git.code.sf.net/p/{namespace}/{name}"
    return CodeFix(url=url, vcs_url=vcs_url, commit_hash=commit_hash, patch_url=None)


GITWEB_ROUTE_REGEX = [
    r"https?://gcc\.gnu\.org/git/.*",
    r"https?://git\.postgresql\.org/gitweb/.*",
    r"https?://sourceware\.org/git/.*",
    r"https?://git\.openssl\.org/gitweb/.*",
    r"https?://gitbox\.apache\.org/.*",
    r"https?://git\.openwrt\.org/.*",
]


@fix_router.route(*GITWEB_ROUTE_REGEX)
def build_gitweb_fix(url):
    """
    Return a CodeFix object from a Gitweb url.
    For example:
    https://gcc.gnu.org/git/?p=gcc.git;a=commit;h=82cc94e5fb69d1c45a386f83798251de5bff9339
    https://git.postgresql.org/gitweb/?p=hamn.git;a=commit;h=a796b71a5b3fe7f751f1086a08cb114b9877dea2
    https://sourceware.org/git/?p=glibc.git;a=commit;h=dedebed24f77762eea7d3c5ed2739a90a4d60461
    https://gitbox.apache.org/repos/asf?p=xalan-java.git;a=commit;h=da3e0d06b467247643ce04e88d3346739d119f21
    """

    gitweb_pattern = (
        r"^https?://"
        r"(?P<domain>[^/]+)"
        r"/(?P<namespace>[^?]*?)"
        r"/?(?=\?)"
        r"(?=.*[?;&]p=(?P<name>[^;&]+?)(?:\.git)?(?:[;&]|$))"
        r"(?=.*[?;&]h=(?P<commit_hash>[0-9a-fA-F]{7,64}))"
    )

    commit_match = re.match(gitweb_pattern, url)
    domain = commit_match.group("domain")
    name = commit_match.group("name")
    namespace = commit_match.group("namespace")
    commit_hash = commit_match.group("commit_hash")

    vcs_url = f"https://{domain}/git/{name}.git"
    if domain == "gitbox.apache.org":
        vcs_url = f"https://github.com/apache/{name}.git"

    patch_url = f"https://{domain}/{namespace}/?p={name}.git;a=patch;h={commit_hash}"
    return CodeFix(
        url=url,
        vcs_url=vcs_url,
        commit_hash=commit_hash,
        patch_url=patch_url,
    )
