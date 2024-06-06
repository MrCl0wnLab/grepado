# Grepado

Um script que simplifica a utilização do comando grep. É possível utilizar um arquivo como fonte de pesquisa para a busca de valores em uma pasta definida pelo usuário.

> Todo script pode ser resumido em algumas linhas de scrpt bash, ou linhas de comando.

[![Python 3.7](https://img.shields.io/badge/python-3.12-yellow.svg)](https://www.python.org/)
[![Build](https://img.shields.io/badge/Supported_OS-Linux-orange.svg)]()
[![Build](https://img.shields.io/badge/Supported_OS-Mac-orange.svg)]()


```
 + Autor: MrCl0wn
 + Blog: http://blog.mrcl0wn.com
 + GitHub: https://github.com/MrCl0wnLab
 + Twitter: https://twitter.com/MrCl0wnLab
 + Email: mrcl0wnlab\@\gmail.com
```

## FLOW
```mermaid
graph TD;
    arquivo_fonte-->pasta-->arquivo1;
    arquivo_fonte-->pasta-->arquivo2;
    arquivo_fonte-->pasta-->arquivo3;
    arquivo_fonte-->pasta-->subpasta-->arquivo4;
```

---

--help

```bash
╔──────────────────────────────────────────────────────────────────────────────────╗
│ ██████╗     ██████╗     ███████╗    ██████╗      █████╗     ██████╗      ██████╗ │
│██╔════╝     ██╔══██╗    ██╔════╝    ██╔══██╗    ██╔══██╗    ██╔══██╗    ██╔═══██╗│
│██║  ███╗    ██████╔╝    █████╗      ██████╔╝    ███████║    ██║  ██║    ██║   ██║│
│██║   ██║    ██╔══██╗    ██╔══╝      ██╔═══╝     ██╔══██║    ██║  ██║    ██║   ██║│
│╚██████╔╝    ██║  ██║    ███████╗    ██║         ██║  ██║    ██████╔╝    ╚██████╔╝│
│ ╚═════╝     ╚═╝  ╚═╝    ╚══════╝    ╚═╝         ╚═╝  ╚═╝    ╚═════╝      ╚═════╝ │
╚──────────────────────────────────────────────────────────────────────────────────╝
                                                                      By MrCl0wnLab
        
usage: Grepado [-h] -f file -p path [-s save]

options:
  -h, --help            show this help message and exit
  -f file, --file file  Parâmetro arquivo com valores para pesquisa
  -p path, --path path  Pasta onde será pesquisado os valores
  -s save, --save save  Arquivo onde será salvo o resultado
```

### EXEMPLO
```bash
python main.py -f ./desaparecidos.txt -p ./governo/
python main.py -f ./desaparecidos.txt -p ./governo/ -s resultado.txt
python main.py --file ./desaparecidos.txt --path ./governo/ --save resultado.txt
```

### GREP
Comando grep usado
```bash
grep -i '{value}' -r {path}
```


### TERMINAL  OUTPUT
![Screenshot](/asset/img1.png)

### ARQUIVO DE SAIDA
arquivo padrão
```
output-%d-%m-%Y-%H.txt
```