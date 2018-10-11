#!/usr/bin/env bash

function main() {
    if ! which python3 &> /dev/null; then
        read -p "The python3 command was not found. Do you want me to try to install it? [y/N] " yn
        case $yn in
            [Yy]*)
                if ! install_python3; then
                    >&2 echo "The installation failed for some reason. Exiting."
                    exit 1
                fi

                if ! which python3 &> /dev/null; then
                    >&2 echo "The python3 command can still not be found for some reason. Exiting."
                    exit 1
                fi
                ;;
            *)
                echo "Python 3 does not seem to be installed. Exiting."
                exit 1
                ;;
        esac
    fi

    if ! which pipenv &> /dev/null; then
        read -p "The pipenv command was not found. Do you want me to try to install it? [y/N] " yn
        case $yn in
            [Yy]*)
                if ! install_pipenv; then
                    >&2 echo "The installation failed for some reason. Exiting."
                    exit 1
                fi

                if ! which pipenv &> /dev/null; then
                    >&2 echo "The pipenv command can still not be found for some reason. Exiting."
                    exit 1
                fi
                ;;
            *)
                echo "pipenv does not seem to be installed. Exiting."
                exit 1
                ;;
        esac
    fi

    pipenv install

    if [ $? -ne 0 ]; then
        >&2 echo "pipenv installation failed. Exiting."
        exit 1
    fi

    pipenv run python main.py
    return $?
}

function install_python3 {
    command=""

    if which apt &> /dev/null; then
        command="sudo apt install python3"
    fi

    if which pacman &> /dev/null; then
        command="sudo pacman -S python"
    fi

    if which zypper &> /dev/null; then
        command="sudo zypper install python3"
    fi

    if [ -z "$command" ]; then
        >&2 echo "None of the known package managers were found."
        return 1
    fi

    read -p "About to run \"$command\". Continue? [Y/n] " yn
    case $yn in
        [Nn]*) return 0;;
        *)
            $command
            return $?
            ;;
    esac
}

function install_pipenv {
    pip3 install --user pipenv
    return $?
}

main
