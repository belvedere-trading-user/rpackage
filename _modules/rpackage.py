#!/usr/bin/python
'''
Manage R packages on Linux nodes
=====================================
Handles installation (ensure a version is installed, or ensure a specific
version is installed), removal, and version verification of R packages on
 Linux (tested on CentOS).

 A given package can be installed to the latest available version with:

    salt 'node' rpackage.install zoo
or
    salt 'node' rpackage.install package=zoo

If a specific version is desired it can be installed via:

    salt 'node' rpackage.install package='zoo==1.7-11'
or
    salt 'node' rpackage.install 'zoo==1.7-11'

A specific repository can be provided via:

salt 'node' rpackage.install 'zoo==1.7-11' repo='http://cran.belvederetrading.com:38080'

Build options can be provided via (these will be treated as environment variables):

salt 'node' rpackage.install 'zoo==1.7-11 build_options="CC=clang"'

The version installed can be reported via:

    salt 'node' rpackage.pkg_version zoo

TODO:
    Add a command to report on all installed packages
'''

import salt.utils
import salt.exceptions
import logging
import re

log = logging.getLogger(__name__)

def _parse_version(package):
    '''
    Given a package string checks if there's specific version to install
     and if so returns [package,version].  Otherwise it returns [package,'none'].
    '''
    if '==' in package:
        version = package.split('==')
        return [version[0],version[1]]
    else:
        return [package,'none']

def _install_from_cran(package,repo,build_options):
    '''
    Installs the given package from the provided cran repository.  NOTE:  Will
     attempt to install regardless of whether the package exists.
    '''
    install_cmd = "{0} /usr/bin/R --silent -e \"install.packages('{1}', repos='{2}')\"".format(build_options,package,repo)

    debug_message = 'install command: {0}'.format(install_cmd)
    log.debug(debug_message)

    install_result = __salt__['cmd.run'](install_cmd, python_shell=True)
    return install_result

def _install_from_source(package,version,repo,build_options):
    '''
    Downloads the given package version from the provided cran repository and
     installs the package.  NOTE:  Will attempt to install regardless of whether
      the package exists.
    '''
    wget_cmd = '/usr/bin/wget {2}/src/contrib/{0}_{1}.tar.gz -O /tmp/{0}_{1}.tar.gz'.format(package,version,repo)

    debug_message = 'wget command: {0}'.format(wget_cmd)
    log.debug(debug_message)

    wget_result = __salt__['cmd.run'](wget_cmd, python_shell=True)

    install_cmd = "{0} /usr/bin/R CMD INSTALL /tmp/{1}_{2}.tar.gz".format(build_options,package,version)

    debug_message = 'install command: {0}'.format(install_cmd)
    log.debug(debug_message)

    install_result = __salt__['cmd.run'](install_cmd, python_shell=True)
    return install_result

def pkg_version(package):
    '''
    If the R package is installed returns the installed version number.
    If the R package is not installed will return an error message saying so.
    '''
    if salt.utils.is_windows():
        debug_message = 'Managing R packages on Windows is not supported by this module.'
        log.debug(debug_message)
        return debug_message

    pkg,version = _parse_version(package)

    cmd = "/usr/bin/R --silent -e \"packageVersion('{0}')\" | grep \"\[\"".format(pkg)

    debug_message = 'pkg_version command: {0}'.format(cmd)
    log.debug(debug_message)

    version = __salt__['cmd.run'](cmd, python_shell=True)
    if (version == '' or version == None):
        output = 'none'
    elif "package '{0}' not found".format(package) in version:
        output = 'none'
    else:
        output = version.split('\'')[1]

    return output

def install(package, repo = None, build_options = None):
    '''
    Checks if the desired R package is already installed and installs it if not.
    '''
    if not repo:
      repo = __salt__['pillar.get']('r:cran','http://cran.rstudio.com/')
    if not build_options:
      build_options = __salt__['pillar.get']('r:build_options','')
    debug_message = 'Attempting to install {0} from {1}'.format(package,repo)
    log.debug(debug_message)
    if salt.utils.is_windows():
        debug_message = 'Managing R packages on Windows is not supported by this module.'
        log.debug(debug_message)
        return debug_message

    pkg,version = _parse_version(package)

    debug_message = 'Post parsed name: {0}, version: {1}'.format(pkg,version)
    log.debug(debug_message)

    pre_find_result = pkg_version(package)


    if pre_find_result == 'none':
        if version != 'none':
            install_result = _install_from_source(pkg,version,repo,build_options)
        else:
            install_result = _install_from_cran(pkg,repo,build_options)
    else:
        if version  == 'none':
            return 'Package {0} already installed'.format(pkg)
        elif re.split('[.|-]',str(version)) == re.split('[.|-]',str(pre_find_result)):
            return 'Package {0}=={1} already installed'.format(pkg,version)
        else:
            remove(pkg)
            install_result = _install_from_source(pkg,version,repo,build_options)

    find_result = pkg_version(pkg)

    if (find_result == '' or find_result == None or find_result == 'none'):
        output = 'Error installing package {0}\n'.format(pkg) + install_result
    else:
        output = find_result

    return output

def remove(package):
    '''
    Checks if the desired R package is installed and removes it if it is.
    '''
    if salt.utils.is_windows():
        debug_message = 'Managing R packages on Windows is not supported by this module.'
        log.debug(debug_message)
        return debug_message

    pre_find_result = pkg_version(package)

    if (pre_find_result == '' or pre_find_result == None or pre_find_result == 'none'):
        output = 'Package {0} is not installed'.format(package)
        return output

    remove_cmd = "CC=gcc CXX=g++ AR=ar LD=ld /usr/bin/R --silent -e \"remove.packages('{0}')\"".format(package)

    debug_message = 'remove command: {0}'.format(remove_cmd)
    log.debug(debug_message)

    remove_result = __salt__['cmd.run'](remove_cmd, python_shell=True)

    find_result = pkg_version(package)

    if (find_result == '' or find_result == None or find_result == 'none'):
        output = 'Uninstalled package {0}'.format(package)
    else:
        output = 'Error uninstalling package {0}'.format(package)

    return output


def update_cran_index(path = '/mount/nfs/cran/src/contrib'):
    '''
    Updates the metadata information on a given set of R packages.  Should be
     run against the existing CRAN repository in most cases.
    '''
    if salt.utils.is_windows():
        debug_message = 'Managing R packages on Windows is not supported by this module.'
        log.debug(debug_message)
        return debug_message

    update_cmd = "/usr/bin/R --silent -e \"tools::write_PACKAGES('{0}')\" && chmod -R 644 {0}".format(path)
    debug_message = 'Update CRAN index command: {0}'.format(update_cmd)
    log.debug(debug_message)

    update_result = __salt__['cmd.run'](update_cmd, python_shell=True)

    return update_result
