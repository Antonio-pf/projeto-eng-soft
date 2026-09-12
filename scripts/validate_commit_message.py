#!/usr/bin/env python3
import re
import sys
from pathlib import Path

CONVENTIONAL_COMMIT = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([\w.-]+\))?!?: .+"
)


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: validate_commit_message.py <arquivo-da-mensagem>")
        return 2

    message = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    subject = next(
        (line.strip() for line in message if line.strip() and not line.startswith("#")),
        "",
    )

    if not CONVENTIONAL_COMMIT.match(subject):
        print("Mensagem de commit invalida.")
        print("Formato esperado: <tipo>(escopo-opcional): <descricao>")
        print("Exemplo: feat: adiciona cadastro de doador")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
