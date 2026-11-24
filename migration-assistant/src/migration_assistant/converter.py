"""Conversion déterministe des ressources JAX-RS et des EJB en composants Spring.

Ce qui est sûr est converti par règles ; ce qui ne l'est pas est signalé dans `leftovers`
pour une relecture humaine ou une proposition du LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

HTTP_ANNOTATIONS = {"GET": "GetMapping", "POST": "PostMapping", "PUT": "PutMapping", "DELETE": "DeleteMapping"}
PARAM_ANNOTATIONS = {"QueryParam": "RequestParam", "PathParam": "PathVariable", "HeaderParam": "RequestHeader"}
STATUS = {"CREATED": "CREATED", "BAD_REQUEST": "BAD_REQUEST", "NOT_FOUND": "NOT_FOUND", "OK": "OK",
          "NO_CONTENT": "NO_CONTENT", "CONFLICT": "CONFLICT"}

PACKAGE_RE = re.compile(r"^package\s+([\w.]+);", re.MULTILINE)
CLASS_RE = re.compile(r"public\s+class\s+(\w+)")
CLASS_PATH_RE = re.compile(r"@Path\(\"([^\"]*)\"\)\s*(?:@\w+(?:\([^)]*\))?\s*)*public\s+class")
INJECT_RE = re.compile(r"@Inject\s+(?:private\s+|protected\s+)?(?:final\s+)?([\w<>]+)\s+(\w+);")
METHOD_RE = re.compile(
    r"((?:@\w+(?:\([^)]*\))?\s*)+)public\s+([\w<>, ?]+)\s+(\w+)\s*\(((?:[^()]|\([^()]*\))*)\)\s*(?:throws [\w, .]+)?\s*\{", re.MULTILINE)


@dataclass
class ConversionResult:
    source: str
    leftovers: list[str] = field(default_factory=list)


def _body(text: str, start: int) -> tuple[str, int]:
    """Renvoie le corps d'une méthode à partir de l'accolade ouvrante (start pointe après « { »)."""
    depth, i = 1, start
    while depth and i < len(text):
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[start:i - 1], i


def _convert_params(params: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return f'@{PARAM_ANNOTATIONS[match.group(1)]}("{match.group(2)}")'

    converted = re.sub(r"@(QueryParam|PathParam|HeaderParam)\(\"([^\"]+)\"\)", repl, params.strip())
    parts = [p.strip() for p in converted.split(",")] if converted else []
    # paramètre sans annotation = corps de requête JSON
    return ", ".join(p if p.startswith("@") else f"@RequestBody {p}" for p in parts)


def _convert_response(body: str, leftovers: list[str], method: str) -> str:
    body = re.sub(r"Response\.ok\(([^;]*?)\)\.build\(\)", r"ResponseEntity.ok(\1)", body)
    body = re.sub(r"Response\.status\(Response\.Status\.(\w+)\)\.entity\(([^;]*?)\)\.build\(\)",
                  lambda m: f"ResponseEntity.status(HttpStatus.{STATUS.get(m.group(1), m.group(1))}).body({m.group(2)})",
                  body)
    body = re.sub(r"Response\.status\(Response\.Status\.(\w+)\)\.build\(\)",
                  lambda m: f"ResponseEntity.status(HttpStatus.{STATUS.get(m.group(1), m.group(1))}).build()", body)
    if "Response." in body:
        leftovers.append(f"{method} : construction de Response non reconnue, à convertir à la main")
    return body


def convert_resource(java: str) -> ConversionResult:
    """Ressource JAX-RS → @RestController avec injection par constructeur."""
    leftovers: list[str] = []
    package = PACKAGE_RE.search(java).group(1)
    name = CLASS_RE.search(java).group(1)
    controller = name.replace("Resource", "Controller") if name.endswith("Resource") else name + "Controller"
    base = (m.group(1) if (m := CLASS_PATH_RE.search(java)) else "")
    injected = INJECT_RE.findall(java)

    methods: list[str] = []
    for match in METHOD_RE.finditer(java):
        annotations, return_type, method, params = match.groups()
        verb = next((v for v in HTTP_ANNOTATIONS if re.search(rf"@{v}\b", annotations)), None)
        if verb is None:
            continue
        sub = m.group(1) if (m := re.search(r"@Path\(\"([^\"]*)\"\)", annotations)) else ""
        body, _ = _body(java, match.end())
        body = _convert_response(body, leftovers, method)
        if return_type.strip() == "Response":
            return_type = "ResponseEntity<?>"
        mapping = f'@{HTTP_ANNOTATIONS[verb]}("{sub}")' if sub else f"@{HTTP_ANNOTATIONS[verb]}"
        methods.append(f"    {mapping}\n    public {return_type.strip()} {method}({_convert_params(params)}) {{"
                       f"{body.rstrip()}\n    }}\n")

    if not methods:
        leftovers.append(f"{name} : aucune méthode JAX-RS reconnue")

    fields = "".join(f"    private final {t} {n};\n" for t, n in injected)
    ctor_params = ", ".join(f"{t} {n}" for t, n in injected)
    ctor_body = "".join(f"        this.{n} = {n};\n" for _, n in injected)
    imports = _carry_imports(java) + [
        "org.springframework.http.HttpStatus",
        "org.springframework.http.ResponseEntity",
        "org.springframework.web.bind.annotation.*",
    ]
    header = f"package {package};\n\n" + "".join(f"import {i};\n" for i in sorted(set(imports)))
    source = (f"{header}\n@RestController\n@RequestMapping(\"/api{base}\")\npublic class {controller} {{\n\n"
              f"{fields}\n    public {controller}({ctor_params}) {{\n{ctor_body}    }}\n\n"
              + "\n".join(methods) + "}\n")
    return ConversionResult(source, leftovers)


def _carry_imports(java: str) -> list[str]:
    """Garde les imports métier ; supprime JAX-RS, CDI et EJB, remplacés par Spring."""
    keep = []
    for imp in re.findall(r"^import\s+([\w.*]+);", java, re.MULTILINE):
        if imp.startswith(("jakarta.ws.rs", "jakarta.inject", "jakarta.ejb", "javax.ws.rs", "javax.inject",
                           "javax.ejb")):
            continue
        keep.append(imp.replace("javax.persistence", "jakarta.persistence"))
    return keep


def convert_service(java: str) -> ConversionResult:
    """EJB @Stateless/@Singleton → @Service transactionnel ; @Inject en champ → injection par constructeur."""
    leftovers: list[str] = []
    source = java.replace("javax.persistence", "jakarta.persistence")
    if "@Stateless" in source or "@Singleton" in source:
        source = re.sub(r"@(Stateless|Singleton)\b", "@Service\n@Transactional", source)
        source = re.sub(r"import (jakarta|javax)\.ejb\.(Stateless|Singleton);",
                        "import org.springframework.stereotype.Service;\n"
                        "import org.springframework.transaction.annotation.Transactional;", source)
    for annotation in ("@Schedule", "@Asynchronous", "@TransactionAttribute", "@Remote", "@Local", "@Lock"):
        if annotation in source:
            leftovers.append(f"{annotation} : pas d'équivalent automatique, à migrer à la main")
    if INJECT_RE.search(source):
        leftovers.append("@Inject sur un champ : passer à l'injection par constructeur")
    if "unitName" in source:
        source = re.sub(r"@PersistenceContext\(unitName\s*=\s*\"[^\"]*\"\)", "@PersistenceContext", source)
    return ConversionResult(source, leftovers)


def classify(java: str) -> str:
    if re.search(r"@Path\(", java) and re.search(r"@(GET|POST|PUT|DELETE)\b", java):
        return "resource"
    if re.search(r"@(Stateless|Singleton)\b", java):
        return "ejb"
    if "extends Application" in java and "@ApplicationPath" in java:
        return "jaxrs-application"
    return "other"
