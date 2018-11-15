[![Build Status](https://img.shields.io/travis/TravisToolbox/shellcheck-travis/master.svg)](https://travis-ci.org/TravisToolbox/shellcheck-travis)
[![Software License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)
[![Release](https://img.shields.io/github/release/TravisToolbox/shellcheck-travis.svg)](https://github.com/TravisToolbox/shellcheck-travis/releases/latest)
[![Github commits (since latest release)](https://img.shields.io/github/commits-since/TravisToolbox/shellcheck-travis/latest.svg)](https://github.com/TravisToolbox/shellcheck-travis/commits)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/TravisToolbox/shellcheck-travis.svg)](https://github.com/TravisToolbox/shellcheck-travis)
[![GitHub contributors](https://img.shields.io/github/contributors/TravisToolbox/shellcheck-travis.svg)](https://github.com/TravisToolbox/shellcheck-travis)

Shellcheck Travis 
==================

A submodule to lint your shell projects with shellcheck in travis.ci builds. This is a fork of [Original Repo](https://github.com/caarlos0/shell-ci-build), with a few extra options and clean up, and mostly because from a security standpoint
including sub modules you don't control isn't a wise move.

## Build

- The `install.sh` script will install shellckeck.
- The `build.sh` will lint all executable files with shellcheck, avoiding
Ruby, compdef and the like files. It will also ignore all files inside `.git`
directory and files of your `gitmodules`, if any.

## Usage

```sh
git submodule add https://github.com/TravisToolbox/shellcheck-travis.git build
cp build/travis.yml.simple-example .travis.yml
OR
cp build/travis.yml.complex-example .travis.yml
```

Or tweak your `.travis.yml` to be like this:

```yml
language: bash
install:
  - ./build/install.sh
script:
  - ./build/build.sh
```

## Updating

Update your projects is easy. Just run this:

```sh
git submodule update --remote --merge && \
  git commit -am 'updated shellcheck-travis version' && \
  git push
```
