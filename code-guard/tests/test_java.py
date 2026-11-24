from pathlib import Path

from code_guard.config import Config
from code_guard.rules.java import check_java_file


def rules(repo, rel, source):
    path = repo(rel, source)
    return [f.rule for f in check_java_file(path, source, Config(root=repo.root))]


def test_clean_service_has_no_finding(repo):
    src = """package com.fundlens.api.application;
public final class NavService {
    private final NavRepository repository;
    public NavService(NavRepository repository) { this.repository = repository; }
}
"""
    assert rules(repo, "fund-api/src/main/java/com/fundlens/api/application/NavService.java", src) == []


def test_public_type_must_match_file_name(repo):
    src = "package a;\npublic class Other {}\n"
    assert rules(repo, "x/src/main/java/a/NavService.java", src) == ["java.naming"]


def test_type_name_must_be_pascal_case(repo):
    src = "package a;\nclass nav_helper {}\n"
    assert rules(repo, "x/src/main/java/a/Helpers.java", src) == ["java.naming"]


def test_sysout_forbidden_in_main_but_allowed_in_tests(repo):
    src = "package a;\npublic class Demo { void run() { System.out.println(\"x\"); } }\n"
    assert rules(repo, "x/src/main/java/a/Demo.java", src) == ["java.no-sysout"]
    assert rules(repo, "x/src/test/java/a/Demo.java", src) == []


def test_field_injection_forbidden_but_constructor_injection_allowed(repo):
    field = "package a;\npublic class Svc {\n    @Autowired\n    private Repo repo;\n}\n"
    ctor = "package a;\npublic class Svc {\n    @Autowired\n    public Svc(Repo repo) {}\n}\n"
    assert rules(repo, "x/src/main/java/a/Svc.java", field) == ["java.no-field-injection"]
    assert rules(repo, "x/src/main/java/a/Svc.java", ctor) == []


def test_domain_must_not_depend_on_frameworks(repo):
    src = """package com.fundlens.api.domain.nav;
import java.math.BigDecimal;
import jakarta.persistence.Entity;
import org.springframework.stereotype.Service;
public record Nav(BigDecimal value) {}
"""
    found = rules(repo, "x/src/main/java/com/fundlens/api/domain/nav/Nav.java", src)
    assert found == ["java.domain-purity", "java.domain-purity"]


def test_adapters_may_use_frameworks(repo):
    src = "package com.fundlens.api.adapter.web;\nimport org.springframework.web.bind.annotation.RestController;\n" \
          "public class NavController {}\n"
    assert rules(repo, "x/src/main/java/com/fundlens/api/adapter/web/NavController.java", src) == []


def test_relative_path_is_reported_as_is():
    finding = check_java_file(Path("A.java"), "public class B {}", Config(root=Path(".")))[0]
    assert finding.path == "A.java"
