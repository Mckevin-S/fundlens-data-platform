from pathlib import Path

from migration_assistant.converter import classify, convert_resource, convert_service

LEGACY = Path(__file__).resolve().parents[2] / "legacy-backoffice/src/main/java/com/fundlens/legacy"


def test_classify_the_real_legacy_sources():
    kinds = {p.name: classify(p.read_text()) for p in LEGACY.glob("*.java")}
    assert kinds == {
        "OperationResource.java": "resource",
        "OperationService.java": "ejb",
        "JaxRsApplication.java": "jaxrs-application",
        "Operation.java": "other",
        "OperationValidator.java": "other",
    }


def test_resource_becomes_rest_controller_with_constructor_injection():
    result = convert_resource((LEGACY / "OperationResource.java").read_text())
    src = result.source
    assert "@RestController" in src and '@RequestMapping("/api/operations")' in src
    assert "public class OperationController" in src
    assert "private final OperationService service;" in src
    assert "public OperationController(OperationService service)" in src
    assert '@RequestParam("fund") String fundId' in src and '@RequestParam("date") String date' in src
    assert "@PostMapping" in src and "@RequestBody Operation operation" in src
    assert "ResponseEntity.status(HttpStatus.CREATED).body(service.create(operation))" in src
    assert "ResponseEntity.status(HttpStatus.BAD_REQUEST).body(e.getMessage())" in src
    assert "public ResponseEntity<?> create" in src
    assert "jakarta.ws.rs" not in src and "@Inject" not in src
    assert result.leftovers == []


def test_path_params_subpaths_and_ok_responses():
    java = '''package a;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.Response;
@Path("/funds")
public class FundResource {
    @GET
    @Path("/{id}")
    public Response get(@PathParam("id") String id) {
        return Response.ok(id).build();
    }
    @DELETE
    @Path("/{id}")
    public Response delete(@PathParam("id") String id) {
        return Response.status(Response.Status.NO_CONTENT).build();
    }
    @PUT
    public Response weird(String body) {
        return Response.serverError().build();
    }
}
'''
    result = convert_resource(java)
    assert '@GetMapping("/{id}")' in result.source
    assert '@PathVariable("id") String id' in result.source
    assert "ResponseEntity.ok(id)" in result.source
    assert "ResponseEntity.status(HttpStatus.NO_CONTENT).build()" in result.source
    assert result.leftovers == ["weird : construction de Response non reconnue, à convertir à la main"]
    assert "public FundController()" in result.source


def test_resource_without_methods_is_flagged():
    result = convert_resource('package a;\n@Path("/x")\npublic class EmptyResource {\n}\n')
    assert result.leftovers == ["EmptyResource : aucune méthode JAX-RS reconnue"]


def test_ejb_becomes_transactional_service():
    result = convert_service((LEGACY / "OperationService.java").read_text())
    src = result.source
    assert "@Service\n@Transactional" in src
    assert "import org.springframework.stereotype.Service;" in src
    assert "jakarta.ejb" not in src
    assert "@PersistenceContext\n" in src
    assert result.leftovers == []


def test_ejb_specifics_are_reported():
    java = '''package a;
import javax.ejb.Singleton;
import javax.persistence.EntityManager;
@Singleton
public class Batch {
    @Inject Clock clock;
    @Schedule(hour = "2")
    public void run() {}
}
'''
    result = convert_service(java)
    assert "jakarta.persistence.EntityManager" in result.source
    assert any("@Schedule" in item for item in result.leftovers)
    assert any("@Inject" in item for item in result.leftovers)
