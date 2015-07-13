# rpackage
A SaltStack execution module/state module for managing R packages

##Installation
* copy the rpackage.py file into the _modules directory in the file_root/_modules directory on your Salt master.
* copy the rpkg.py file into the _states directory in the file_root/_states directory on your salt master.
* sync modules/states across the desired minions (e.g. from the salt master "salt '*' saltutil.sync_all'

##Usage

**execution module**

A given package can be installed to the latest available version with:

```salt 'node' rpackage.install zoo```

or

```salt 'node' rpackage.install package=zoo```

If a specific version is desired it can be installed via:

```salt 'node' rpackage.install package='zoo==1.7-11'```

or

```salt 'node' rpackage.install 'zoo==1.7-11'```

A specific repository can be provided via:

```salt 'node' rpackage.install 'zoo==1.7-11' repo='http://cran.belvederetrading.com:38080'```

Build options can be provided via (these will be treated as environment variables):

```salt 'node' rpackage.install 'zoo==1.7-11 build_options="CC=clang"'```

The version installed can be reported via:

```salt 'node' rpackage.pkg_version zoo```

**state module**

packages can be managed using the rpkg state as if using the pkg state, i.e.:

```
zoo:
  rpkg.installed
```

or

```
zoo==1.7-11:
  rpkg.installed
```

**Notes/Known Issues**
* Tested on CentOS 6.X
* Assumes that wget will be available
* Explicitly not compatible with Windows (There's no reason this couldn't be updated to be compatible with Windows, but we don't use R on Windows so we've not sorted out the issues associated with setting this up).
