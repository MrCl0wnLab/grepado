import re
import shlex
import pathlib
import logging
import asyncio
import argparse
import aiometer
import subprocess
from datetime import datetime
from typing import Dict, List
from rich.console import Console
from functools import partial


async def log(value) -> Console:
    try:
        if value:
            console = Console(log_path=False)
            return console.log(
                f"{value}",
                highlight=True
            )
    except Exception as exp:
        await log(str(exp))


def remove_duplicate(value_list: list) -> list:
    if value_list:
        file_lines = [clear_value(line) for line in value_list]
        [file_lines.remove(None) for i in range(file_lines.count(None))]
        file_lines = list(set(file_lines))
        return file_lines


async def open_file(filename: str) -> dict[str, list[str] | str]:
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            f_contents_text = file.read()
            file.seek(0)
            f_contents_lines = file.readlines()
            return {'text': f_contents_text, 'list': f_contents_lines}
    except FileNotFoundError:
        await log("File {filename} not found or inaccessible.")
    except PermissionError:
        await log(f"Permission denied to access {filename}.")


def to_lower(value: str) -> str:
    if value:
        return value


def clear_value(value: str) -> str:
    if value:
        return value.replace("\n", "").strip()


async def verbose(value: str):
    if ARGS.verbose and value:
        await log(value)


async def command_line(command_str: str) -> None:
    if command_str:
        try:
            cmd_shlex = shlex.split(f'{command_str}')
            await verbose(f"[!]COMMAND: {cmd_shlex}")
            rest_spn = subprocess.Popen(cmd_shlex, stdout=subprocess.PIPE, encoding='utf-8')
            if ARGS.pipe:
                try:
                    cmd_shlex_pipe = shlex.split(ARGS.pipe)
                    rest_spn = subprocess.Popen(cmd_shlex_pipe, stdin=rest_spn.stdout, stdout=subprocess.PIPE, encoding='utf-8')
                    await verbose(f"[!]PIPE: {cmd_shlex_pipe}")
                except Exception as exp:
                    await log(str(exp))
            for line_std in rest_spn.stdout:
                if line_std:
                    console = Console(log_path=False)
                    logging.info(line_std.strip())
                    (console.log(line_std.strip()) if ARGS.verbose else console.print(line_std.strip()))
        except Exception as exp:
            await log(str(exp))


async def exec_grep(value: str, path: str) -> None:
    if value and path:
        await verbose(f"[!]VALUE: {value}\n[!]PATH: {path}")
        try:
            excl_str: str = str()
            path_str: str = str()
            if ARGS.rc:
                path_str = f"-r {path}" 
            if ARGS.skip:
                excl_str = f"--exclude-dir={ARGS.skip}"
            value_clear = clear_value(value)
            command_str = "grep -i -E '" + value_clear + f"' {path_str} --text {excl_str}"
            await verbose(f"[!]COMMAND: {command_str}")
            return await command_line(command_str)
        except Exception as exp:
            await log(str(exp))


async def main_async(target_str: str, dir_target_str: str) -> None:
    if dir_target_str and target_str:
        try:
            await verbose(f"[!]TARGET: {target_str}\n[!]DIR: {dir_target_str}\n")
            target_list = await open_file(target_str)
            if target_list:
                result = aiometer.run_all(
                    [partial(exec_grep, target_, dir_target_str) for target_ in remove_duplicate(target_list.get('list'))],
                    max_at_once=1000,   # Limit maximum number of concurrently running tasks.
                    max_per_second=500  # Limit request rate to not overload the server.
                )
                await result
        except BrokenPipeError as exp:
            await log(str(exp))
      

async def find_value_file(value: str, filename: str, regex=False) -> list:
    if value and filename:
        if not regex:
            value = '.*' + value + '.*'
        try:
            regex_compile = re.compile(value)
            file_open = await open_file(filename)
            regex_result = re.findall(regex_compile, file_open.get('text'))
            return regex_result
        except Exception as exp:
            await log(str(exp))


def list_file_dir(dir_str: str) -> dict[list[str], list[str] | str]:
    dir_list: list = []
    file_list: list = []
    skipe_list: list = ["etc", "bin", "home"]
    try:
        if dir_str:
            obj_path = pathlib.Path(dir_str)
            path_tree_list = list(obj_path.rglob("*"))
            for dir_file in path_tree_list:
                if set(dir_file.parts).isdisjoint(skipe_list):
                    if dir_file.is_dir():
                        dir_list.append(dir_file)
                        logging.debug(f"[DIR] {dir_file}")
                    elif dir_file.is_file():
                        file_list.append(dir_file)
                        logging.debug(f"[FILE] {dir_file}")
            return {'dirs': dir_list, 'files': file_list}
    except Exception as exp:
        log(str(exp))


if __name__ == '__main__':

    print(
        """
        ╔──────────────────────────────────────────────────────────────────────────────────╗
        │ ██████╗     ██████╗     ███████╗    ██████╗      █████╗     ██████╗      ██████╗ │
        │██╔════╝     ██╔══██╗    ██╔════╝    ██╔══██╗    ██╔══██╗    ██╔══██╗    ██╔═══██╗│
        │██║  ███╗    ██████╔╝    █████╗      ██████╔╝    ███████║    ██║  ██║    ██║   ██║│
        │██║   ██║    ██╔══██╗    ██╔══╝      ██╔═══╝     ██╔══██║    ██║  ██║    ██║   ██║│
        │╚██████╔╝    ██║  ██║    ███████╗    ██║         ██║  ██║    ██████╔╝    ╚██████╔╝│
        │ ╚═════╝     ╚═╝  ╚═╝    ╚══════╝    ╚═╝         ╚═╝  ╚═╝    ╚═════╝      ╚═════╝ │
        ╚──────────────────────────────────────────────────────────────────────────────────╝
                                                                               By MrCl0wnLab
        """
    )

    dt_string = datetime.now().strftime("%d-%m-%Y-%H")

    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(prog='Grepado', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--list', metavar="file",
                        help="Parâmetro arquivo com nome de valores para pesquisa", default=None, required=True)
    parser.add_argument('-r', '--rc', metavar="dir",
                        help="Pasta onde será pesquisado os valores", default=None, required=True)
    parser.add_argument('-o', '--out', metavar="file",
                        help="Arquivo onde será salvo os valores", default=f'output-{dt_string}.txt')
    parser.add_argument('-s', '--skip', metavar="path",
                        help="Pasta que o processo vai pular. Ex: -k path ou --skip path2 ou -k {path1,path2,path3}")
    parser.add_argument('-p', '--pipe', metavar="cmd", help="Comando que será executado depois de um pipe |")
    parser.add_argument('-v', '--verbose', help="Modo verboso", action='store_true')

    ARGS = parser.parse_args()
    logging.basicConfig(
        filename=str(ARGS.out),
        filemode='a',
        format='%(message)s',
        datefmt='%H:%M:%S',
    )

    try:
        asyncio.run(
            main_async(
                target_str=ARGS.list,
                dir_target_str=ARGS.rc)
        )
    except KeyboardInterrupt as err:
        print(err)
