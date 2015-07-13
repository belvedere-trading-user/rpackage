import salt.utils
import salt.exceptions
import logging

log = logging.getLogger(__name__)

def installed(name,
              repo='http://cran.belvederetrading.com:38080'):

    ret = { 'name': name,
            'changes': {},
            'result': False,
            'comment': ''}

    if salt.utils.is_windows():
        ret['comment'] = 'Managing R packages on Windows is not supported by this module.'
        ret['result'] = False
        log.debug(debug_message)
        return ret

    else:
        existing_pkg_version = __salt__['rpackage.pkg_version'](name)
        install_results = __salt__['rpackage.install'](name,repo)

        if ('Error' in install_results) or (install_results == '') or (install_results == None):
            ret['result'] = False
            ret['comment'] = install_results
        elif ('already' in install_results):
            ret['result'] = True
            ret['comment'] = install_results
        else:
            ret['result'] = True
            ret['comment'] = '1 targeted package was installed/updated.'
            ret['changes'] = {name:{'new':install_results,'old':existing_pkg_version}}

    return ret

def removed(name):
    ret = { 'name': name,
            'changes': {},
            'result': False,
            'comment': ''}

    if salt.utils.is_windows():
        ret['comment'] = 'Managing R packages on Windows is not supported by this module.'
        ret['result'] = False
        log.debug(debug_message)
        return ret
    else:
        existing_pkg_version = __salt__['rpackage.pkg_version'](name)
        remove_results = __salt__['rpackage.remove'](name)

        if ('Error' in remove_results) or (remove_results == '') or (remove_results == None):
            ret['result'] = False
            ret['comment'] = remove_results
        elif ('not installed' in remove_results):
            ret['result'] = True
            ret['comment'] = remove_results
        else:
            ret['result'] = True
            ret['comment'] = '1 targeted package was removed.\n' + remove_results
            ret['changes'] = {name:{'new':'','old':existing_pkg_version}}

    return ret