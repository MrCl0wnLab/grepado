import io
import os
import sys
import shlex
import select
import logging
import asyncio
import argparse
import aiometer
import textwrap
import subprocess
from datetime import datetime
from typing import Dict, List
from rich.console import Console
from functools import partial

__author__ = "Cleiton Pinheiro aka MrCl0wn"
__credits__ = ["Cleiton Pinheiro"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Cleiton Pinheiro aka MrCl0wn"
__email__ = "mrcl0wnlab@gmail.com"
__git__ = "https://github.com/MrCl0wnLab"
__twitter__ = "https://twitter.com/MrCl0wnLab"





def stdin_get_list() -> list:
    try:
        if select.select([sys.stdin], [], [], 0.0)[0]:
            stdin_list = sys.stdin.readlines()
            if stdin_list:
                return stdin_list
        else:
            return None
        return None
    except Exception as exp:
       log(exp)


def remove_duplicate(value_list: list) -> list:
    if value_list:
        file_lines = [clear_value(line) for line in value_list]
        [file_lines.remove(None) for i in range(file_lines.count(None))]
        file_lines = list(set(file_lines))
        return file_lines


def to_lower(value: str) -> str:
    if value:
        return value


def clear_value(value: str) -> str:
    if value:
        return value.replace("\n", "").strip()


def log(value) -> Console:
    try:
        if value:
            console = Console(log_path=False)
            return console.print(
                f"{value}",
                highlight=True,
            )
    except Exception as exp:
        print(str(exp))


async def open_file(filename: str) -> io.TextIOWrapper:
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        log("File {filename} not found or inaccessible.")
    except PermissionError:
        log(f"Permission denied to access {filename}.")


async def verbose(value: str):
    if ARGS.verbose and value:
        log(value)


async def command_line(command_str: str) -> None:
    if command_str:
        try:
            cmd_shlex = shlex.split(f'{command_str}')
            rest_spn = subprocess.Popen(cmd_shlex, stdout=subprocess.PIPE, encoding='utf-8')
            if ARGS.pipe:
                try:
                    cmd_shlex_pipe = shlex.split(ARGS.pipe)
                    rest_spn = subprocess.Popen(cmd_shlex_pipe, stdin=rest_spn.stdout, stdout=subprocess.PIPE, encoding='utf-8')
                    await verbose(f"[!] PIPE: {cmd_shlex_pipe}")
                except Exception as exp:
                    log(str(exp))
            for line_std in rest_spn.stdout:
                if line_std:
                    console = Console(log_path=False)
                    logging.info(line_std.strip())
                    (console.log(line_std.strip()) if ARGS.verbose else console.print(line_std.strip()))
        except Exception as exp:
            log(str(exp))


async def exec_grep(value: str, path: str) -> None:
    if value and path:
        await verbose(f"[!] VALUE:{value}")
        await verbose(f"[!] PATH: {path}")
        try:
            excl_str: str = str()
            path_str: str = str()
            if ARGS.rc:
                path_str = f"-r {path}" 
            if ARGS.skip:
                excl_str = f"--exclude-dir={ARGS.skip}"
            value_clear = clear_value(value)
            command_str = "grep -i -E '" + value_clear + f"' {path_str}  {excl_str}"
            await verbose(f"[!] COMMAND: {command_str}")
            return await command_line(command_str)
        except Exception as exp:
            log(str(exp))


async def main_async(target_str_list: any, dir_target_str: str) -> None:
    if target_str_list and dir_target_str:
        try:
            await verbose(f"[!] TARGET: {target_str_list}\n[!] DIR: {dir_target_str}\n")
            target_list = await open_file(target_str_list) if os.path.isfile(str(target_str_list)) else target_str_list
            if type(target_list) == list:
                print()
                result = aiometer.run_all(
                    [partial(exec_grep, target_, dir_target_str) for target_ in remove_duplicate(target_list)],
                    max_at_once=1000,   # Limit maximum number of concurrently running tasks.
                    max_per_second=500  # Limit request rate to not overload the server.
                )
                await result
        except BrokenPipeError as exp:
            log(str(exp)) 


if __name__ == '__main__':
    
    print(
        """
        \033[93m
        ╔──────────────────────────────────────────────────────────────────────────────────╗
        │\033[93m ██████╗     ██████╗     ███████╗    ██████╗ \033[32m     █████╗     ██████╗      ██████╗ │
        │\033[93m██╔════╝     ██╔══██╗    ██╔════╝    ██╔══██╗\033[32m    ██╔══██╗    ██╔══██╗    ██╔═══██╗│
        │\033[93m██║  ███╗    ██████╔╝    █████╗      ██████╔╝\033[32m    ███████║    ██║  ██║    ██║   ██║│
        │\033[93m██║   ██║    ██╔══██╗    ██╔══╝      ██╔═══╝ \033[32m    ██╔══██║    ██║  ██║    ██║   ██║│
        │\033[93m╚██████╔╝    ██║  ██║    ███████╗    ██║     \033[32m    ██║  ██║    ██████╔╝    ╚██████╔╝│
        │\033[93m ╚═════╝     ╚═╝  ╚═╝    ╚══════╝    ╚═╝     \033[32m    ╚═╝  ╚═╝    ╚═════╝      ╚═════╝ │
        ╚──────────────────────────────────────────────────────────────────────────────────╝
                                                                               \33[97mBy MrCl0wnLab\033[0m"""
    )

    console = Console(log_path=False)
    dt_string = datetime.now().strftime("%d-%m-%Y-%H")
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        prog='grepado',
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(prog, max_help_position=60, indent_increment=13, width=None),
    )
    parser.add_argument('-l', '--list', metavar="file",
                        help="Parâmetro arquivo com nome de valores para pesquisa", default=stdin_get_list())
    parser.add_argument('-r', '--rc', metavar="dir",
                        help="Pasta onde será pesquisado os valores", default=None, required=True)
    parser.add_argument('-o', '--out', metavar="file",
                        help="Arquivo onde será salvo os valores", default=f'output-{dt_string}.txt')
    parser.add_argument('-s', '--skip', metavar="path",
                        help="Pasta que o processo vai pular. Ex: -k path ou --skip path2 ou -k {path1,path2,path3}")
    parser.add_argument('-p', '--pipe', metavar="cmd", help="Comando que será executado depois de um pipe |")
    parser.add_argument('-v', '--verbose', help="Modo verboso", action='store_true')

    ARGS = parser.parse_args()

    if not ARGS.list:
        log('[X] Grepado: error: the following arguments are required: -l/--list')
        log('[X] Grepado: use pipes: cat list.txt | main.py -r ../testes/')
    

    logging.basicConfig(
        filename=str(ARGS.out),
        filemode='a',
        format='%(message)s',
        datefmt='%H:%M:%S',
    )

    try:
        asyncio.run(
            main_async(
                target_str_list=ARGS.list,
                dir_target_str=ARGS.rc)
        )
    except KeyboardInterrupt as exp:
        log(exp)
