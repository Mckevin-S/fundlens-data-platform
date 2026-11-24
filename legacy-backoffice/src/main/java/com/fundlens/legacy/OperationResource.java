package com.fundlens.legacy;

import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.time.LocalDate;
import java.util.List;

@Path("/operations")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class OperationResource {

    @Inject
    OperationService service;

    @GET
    public List<Operation> list(@QueryParam("fund") String fundId, @QueryParam("date") String date) {
        return service.findByFundAndDate(fundId, LocalDate.parse(date));
    }

    @POST
    public Response create(Operation operation) {
        try {
            return Response.status(Response.Status.CREATED).entity(service.create(operation)).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.BAD_REQUEST).entity(e.getMessage()).build();
        }
    }
}
